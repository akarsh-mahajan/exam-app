import os
import json
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, generics
from django.conf import settings
from django.utils import timezone
from random import shuffle

from google import genai         # google-generativeai library
from .models import Topic, Question, ExamSession
from .serializers import TopicSerializer, QuestionSerializer, ExamSessionSerializer

client = genai.Client(api_key=settings.GEMINI_API_KEY)



# helper: ask gemini by uploading file and sending prompt

import base64

# helper: ask Gemini by sending PDF bytes inline
def ask_gemini_generate_questions(pdf_path: str, topic: str, weak_focus=None):
    """
    Uploads PDF content inline and asks Gemini to generate MCQs.
    Works with older google-genai SDK versions.
    """

    # 1. Read PDF bytes
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # 2. Encode PDF to base64
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

    # 3. Build the prompt
    prompt_extra = ""
    if weak_focus:
        prompt_extra = "Focus more on the weak areas: " + ", ".join(weak_focus)

    user_prompt = f"""
You are an expert MCQ generator.
Use ONLY the uploaded PDF and topic "{topic}".
Generate EXACTLY 50 MCQs with:
  - question (string)
  - options (list of 4 strings)
  - answer_index (0–3)
  - reasoning (string)
Return STRICT JSON — only the array, no markdown.
{prompt_extra}
"""

    # 4. Send PDF inline with prompt
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=[
            {"inline_data": {"data": pdf_b64, "mime_type": "application/pdf"}},
            {"text": user_prompt}
        ]
    )

    print(response)

    # 5. Extract JSON array from response text
    content = response.text
    start = content.find('[')
    end = content.rfind(']')
    if start == -1 or end == -1:
        raise ValueError(f"Gemini did not return JSON. Raw response: {content}")

    json_text = content[start:end+1]
    return json.loads(json_text)



class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        # expects: file (pdf) and title (topic title) or topic_id to attach to existing topic
        # accept 'pdf' (from frontend) OR fallback to 'file'
        file_obj = request.FILES.get('pdf') or request.FILES.get('file')

        topic_title = topic_title = request.data.get('title') or request.data.get('topic')
        topic_id = request.data.get('topic_id')

        if not file_obj:
            return Response({"detail": "file required"}, status=400)

        if topic_id:
            try:
                topic = Topic.objects.get(id=int(topic_id))
            except Topic.DoesNotExist:
                return Response({"detail":"topic_id invalid"}, status=400)
        else:
            if not topic_title:
                return Response({"detail": "title or topic_id required"}, status=400)
            topic = Topic.objects.create(title=topic_title)

        # save uploaded file locally under MEDIA_ROOT
        save_path = os.path.join(settings.MEDIA_ROOT, file_obj.name)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        # attach to topic record (optional)
        topic.pdf_file = os.path.relpath(save_path, settings.BASE_DIR)
        topic.save()

        # get list of weak focus if any (from existing wrong answers)
        weak_focus = []
        if topic.questions.exists():
            # pick top 5 questions with highest wrong_count and use question text as focus hints
            weak = topic.questions.order_by('-wrong_count')[:5]
            weak_focus = [q.text[:200] for q in weak]

        # call Gemini to generate questions
        try:
            qlist = ask_gemini_generate_questions(save_path, topic.title, weak_focus)
        except Exception as e:
            return Response({"detail": f"Gemini error: {str(e)}"}, status=500)

        created_ids = []
        for item in qlist[:50]:
            qtext = item.get('question') or item.get('q') or ''
            options = item.get('options') or item.get('choices') or []
            if len(options) != 4:
                # skip or try to pad
                continue
            ans_idx = int(item.get('answer_index', item.get('answer_index', 0)))
            reasoning = item.get('reasoning') or item.get('explanation') or ''
            q = Question.objects.create(
                topic=topic,
                text=qtext,
                options=options,
                correct_index=ans_idx,
                reasoning=reasoning
            )
            created_ids.append(q.id)
        return Response({"topic_id": topic.id, "created_question_ids": created_ids})

class TopicListCreateView(generics.ListCreateAPIView):
    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer

class TopicQuestionsView(APIView):
    def get(self, request, pk):
        try:
            topic = Topic.objects.get(pk=pk)
        except Topic.DoesNotExist:
            return Response(status=404)
        qs = topic.questions.all()
        serializer = QuestionSerializer(qs, many=True)
        return Response(serializer.data)

class StartExamView(APIView):
    def post(self, request, topic_id):
        timed = bool(request.data.get('timed', False))
        time_limit_seconds = int(request.data.get('time_limit_seconds', 0))
        focus_mistakes = request.data.get('focus_mistakes', True)

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return Response(status=404)

        all_qs = list(topic.questions.all())
        if len(all_qs) == 0:
            return Response({"detail":"no questions for topic"}, status=400)

        # select up to 50 questions
        if len(all_qs) <= 50:
            selected = all_qs.copy()
            shuffle(selected)
        else:
            if focus_mistakes:
                sorted_qs = sorted(all_qs, key=lambda q: q.wrong_count, reverse=True)
                selected = sorted_qs[:30]
                remaining = [q for q in all_qs if q not in selected]
                shuffle(remaining)
                selected += remaining[:max(0, 50 - len(selected))]
            else:
                shuffle(all_qs)
                selected = all_qs[:50]

        question_order = [q.id for q in selected][:50]
        exam = ExamSession.objects.create(
            topic=topic,
            question_order=question_order,
            timed=timed,
            time_limit_seconds=time_limit_seconds
        )

        # Build full question list for frontend
        question_list = []
        for q in selected:
            question_list.append({
                "id": q.id,
                "question": q.text,
                "options": q.options,
                "correct_index": q.correct_index,  # optional, can hide in frontend
                "reasoning": q.reasoning          # optional, can hide in frontend
            })

        return Response({
            "uuid": str(exam.uuid),
            "topic": TopicSerializer(topic).data,
            "questions": question_list,
            "timed": exam.timed,
            "time_limit_seconds": exam.time_limit_seconds
        })


class ExamDetailView(APIView):
    def get(self, request, uuid):
        try:
            exam = ExamSession.objects.get(uuid=uuid)
        except ExamSession.DoesNotExist:
            return Response(status=404)

        idx = exam.current_index
        if idx < 0 or idx >= len(exam.question_order):
            return Response({"detail":"index out of range", "exam": ExamSessionSerializer(exam).data})

        qid = exam.question_order[idx]
        try:
            q = Question.objects.get(pk=qid)
        except Question.DoesNotExist:
            return Response({"detail":"question missing"}, status=500)

        # mark times_seen
        q.times_seen = q.times_seen + 1
        q.save()

        qdata = {
            "id": q.id,
            "text": q.text,
            "options": q.options,
            "index_in_exam": idx,
            "total_questions": len(exam.question_order),
            "exam": ExamSessionSerializer(exam).data
        }
        return Response(qdata)

class SubmitAnswerView(APIView):
    def post(self, request, uuid):
        data = request.data
        answers_dict = data.get('answers', {})  # expects {questionId: selectedIndex}

        try:
            exam = ExamSession.objects.get(uuid=uuid)
        except ExamSession.DoesNotExist:
            return Response(status=404)

        exam_answers = exam.answers or {}

        for qid_str, chosen_index in answers_dict.items():
            try:
                chosen_index = int(chosen_index)
            except:
                continue  # skip invalid value

            exam_answers[qid_str] = chosen_index

        exam.answers = exam_answers
        exam.save()

        return Response({"ok": True, "answers": exam.answers})


class EndExamView(APIView):
    def post(self, request, uuid):
        try:
            exam = ExamSession.objects.get(uuid=uuid)
        except ExamSession.DoesNotExist:
            return Response(status=404)

        exam.finished_at = timezone.now()

        correct = 0
        wrong = 0
        unattempted = 0
        detailed = []

        for qid_str in exam.question_order:
            chosen = exam.answers.get(str(qid_str))
            try:
                q = Question.objects.get(pk=int(qid_str))
                if chosen is None:
                    unattempted += 1
                elif chosen == q.correct_index:
                    correct += 1
                else:
                    wrong += 1
                detailed.append({
                    "question_id": q.id,
                    "question": q.text,
                    "chosen_index": chosen,
                    "correct_index": q.correct_index,
                    "reasoning": q.reasoning,
                    "options": q.options
                })
            except Question.DoesNotExist:
                pass

        # save counts in ExamSession
        exam.correct_count = correct
        exam.wrong_count = wrong
        exam.unattempted_count = unattempted
        exam.save()

        return Response({
            "score": correct,
            "total": len(exam.question_order),
            "correct": correct,
            "wrong": wrong,
            "unattempted": unattempted,
            "details": detailed
        })



class RegenerateView(APIView):
    """
    Regenerate additional questions focusing on weak areas for a topic.
    """
    def post(self, request, topic_id):
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return Response(status=404)

        # gather wrong questions text as focus hints
        weak = topic.questions.order_by('-wrong_count')[:10]
        weak_focus = [q.text[:300] for q in weak] if weak else None

        # ensure there is a pdf
        if not topic.pdf_file:
            return Response({"detail":"topic has no pdf_file stored"}, status=400)

        upload_path = os.path.join(settings.BASE_DIR, topic.pdf_file)
        try:
            new_questions = ask_gemini_generate_questions(upload_path, topic.title, weak_focus)
        except Exception as e:
            return Response({"detail": f"Gemini error: {str(e)}"}, status=500)

        created = []
        for item in new_questions:
            options = item.get('options') or []
            if len(options) != 4:
                continue
            q = Question.objects.create(
                topic=topic,
                text=item.get('question',''),
                options=options,
                correct_index=int(item.get('answer_index',0)),
                reasoning=item.get('reasoning','')
            )
            created.append(q.id)
        return Response({"created": created})

class ExamSessionListView(APIView):
    def get(self, request):
        sessions = ExamSession.objects.all().order_by('-finished_at')
        data = []
        for ex in sessions:
            data.append({
                "uuid": str(ex.uuid),
                "topic": TopicSerializer(ex.topic).data,
                "finished_at": ex.finished_at,
                "correct": ex.correct_count,
                "wrong": ex.wrong_count,
                "unattempted": ex.unattempted_count,
                "total": len(ex.question_order)
            })
        return Response(data)

class ExamSessionDetailView(APIView):
    def get(self, request, uuid):
        try:
            exam = ExamSession.objects.get(uuid=uuid)
        except ExamSession.DoesNotExist:
            return Response(status=404)

        details = []
        for qid_str in exam.question_order:
            chosen = exam.answers.get(str(qid_str))
            try:
                q = Question.objects.get(pk=int(qid_str))
                details.append({
                    "question_id": q.id,
                    "question": q.text,
                    "chosen_index": chosen,
                    "correct_index": q.correct_index,
                    "reasoning": q.reasoning,
                    "options": q.options
                })
            except Question.DoesNotExist:
                pass

        return Response({
            "uuid": str(exam.uuid),
            "topic": TopicSerializer(exam.topic).data,
            "finished_at": exam.finished_at,
            "correct": exam.correct_count,
            "wrong": exam.wrong_count,
            "unattempted": exam.unattempted_count,
            "total": len(exam.question_order),
            "details": details
        })


class ClearDatabaseView(APIView):
    def post(self, request):
        try:
            # Delete all questions, then sessions, then topics
            Question.objects.all().delete()
            ExamSession.objects.all().delete()
            Topic.objects.all().delete()
            return Response(
                {"detail": "Database cleared successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TopicExamSessionListView(generics.ListAPIView):
    serializer_class = ExamSessionSerializer

    def get_queryset(self):
        topic_id = self.kwargs['topic_id']
        return ExamSession.objects.filter(topic_id=topic_id).order_by('-finished_at')

from django.db import models
import uuid

class Topic(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="topic_pdfs/", blank=True, null=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    options = models.JSONField(default=list)   # list of 4 strings
    correct_index = models.IntegerField()      # 0..3
    reasoning = models.TextField(blank=True, null=True)
    wrong_count = models.IntegerField(default=0)
    times_seen = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:80]

class ExamSession(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    current_index = models.IntegerField(default=0)
    question_order = models.JSONField(default=list)    # list of question IDs
    answers = models.JSONField(default=dict)           # question_id -> chosen_index
    timed = models.BooleanField(default=False)
    time_limit_seconds = models.IntegerField(default=0)

    correct_count = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)
    unattempted_count = models.IntegerField(default=0)


    def score(self):
        if self.correct_count and self.wrong_count and self.unattempted_count:
            return self.correct_count
        s = 0
        for qid_str, ans in self.answers.items():
            try:
                q = Question.objects.get(id=int(qid_str))
                if q.correct_index == ans:
                    s += 1
            except Question.DoesNotExist:
                pass
        return s

    def __str__(self):
        return f"Exam {self.uuid} for {self.topic}"

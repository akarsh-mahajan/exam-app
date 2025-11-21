from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.UploadPDFView.as_view(), name="upload_pdf"),
    path("topics/", views.TopicListCreateView.as_view(), name="topics"),
    path("topics/<int:pk>/questions/", views.TopicQuestionsView.as_view(), name="topic_questions"),
    path("start_exam/<int:topic_id>/", views.StartExamView.as_view(), name="start_exam"),
    path("exam/<uuid:uuid>/", views.ExamDetailView.as_view(), name="exam_detail"),
    path("submit_answer/<uuid:uuid>/", views.SubmitAnswerView.as_view(), name="submit_answer"),
    path("end_exam/<uuid:uuid>/", views.EndExamView.as_view(), name="end_exam"),
    path("regenerate/<int:topic_id>/", views.RegenerateView.as_view(), name="regenerate"),
]

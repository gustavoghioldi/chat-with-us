from django.urls import path

from analysis.views.chat_analysis_view import ChatAnalysisView

app_name = "analysis"

urlpatterns = [
    path("chat", ChatAnalysisView.as_view(), name="chat-analysis"),
]

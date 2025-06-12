from django.views.generic import TemplateView


class ChatUIView(TemplateView):
    template_name = "UI/chat-ui/index.html"

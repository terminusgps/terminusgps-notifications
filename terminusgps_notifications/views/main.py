from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin


class HomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Terminus GPS Notifications",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_home.html"
    template_name = "terminusgps_notifications/home.html"

from django.urls import path

from .views import *

app_name = "Ranker"

urlpatterns = [
    path("", BoopInfiniteList.as_view(), name="texts_list"),
    path("search", BoopInfiniteList.as_view(), name="boop_search"),
    path("send_foop", sendFoop, name="send_vote"),
    path("shoop_boop", sendBoop, name="send_boop"),
    path("send_report", sendReport, name="send_report"),
    path("boop/<int:boop_id>", viewBoop, name="view_boop"),
    path("about", aboutPage, name="about_page"),
]

from django.urls import path

from interactive import views

app_name = "interactive"

urlpatterns = [
    path("interactive/chat/", views.chat, name="chat"),
]

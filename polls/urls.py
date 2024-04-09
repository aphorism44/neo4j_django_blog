from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/editor
    path("editor/", views.editor, name="editor"),
    path("save_entry/", views.editor, name="save_entry"),
    path("lists/", views.lists, name="lists"),
]
from django.urls import path, include

from . import views

app_name = "polls"
urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/editor
    path("editor/", views.editor, name="editor"),
    path("lists/", views.lists, name="lists"),
    path('tinymce/', include('tinymce.urls')),
]
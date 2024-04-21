from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/editor
    path("editor/", views.editor, name="editor"),
    path("save_entry/", views.editor, name="save_entry"),
    path("analysis/", views.analysis, name="analysis"),
     path("blog_entry/", views.blog_entry, name="blog_entry"),
    path("blog_entry/<str:entry_id>/", views.blog_entry, name="blog_entry"),
    path("blog_keyword/<str:keyword>/", views.blog_keyword, name="blog_keyword"),
]
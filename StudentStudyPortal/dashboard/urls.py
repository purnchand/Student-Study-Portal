from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('notes/', views.notes, name='notes'),
    path('delete_notes/<int:pk>/', views.delete_notes, name='delete-notes'),
    path('notes_detail/<int:pk>/', views.NotesDetailView.as_view(), name='notes-detail'),
    path('homework/', views.homework, name='homework'),
    path('update_homework/<int:pk>', views.update_homework, name='update-homework'),
    path('delete_homework/<int:pk>', views.delete_homework, name='delete-homework'),
    path('youtube/', views.youtube, name='youtube'),
    path('todo/', views.todo, name='todo'),
    path('toggle_todo/<int:id>/', views.toggle_todo, name='toggle-todo'), 
    path('delete_todo/<int:id>/', views.delete_todo, name='delete-todo'), 
    path('books/',views.books,name='books'),
    path('wiki/',views.wiki,name='wiki'),
]


from django.shortcuts import render, redirect, get_object_or_404
import requests
import wikipedia
from .forms import DashboardForm, HomeworkForm, NotesForm, TodoForm, UserRegistrationForm
from django.contrib import messages
from django.views import generic
from .models import Homework, Notes, Todo
from youtubesearchpython import VideosSearch
from django.contrib.auth.decorators import login_required

# Home View
def home(request):
    return render(request, 'dashboard/home.html')

# Notes View
@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(request, "Notes Added Successfully!")
    else:
        form = NotesForm()

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

# Delete Note View
@login_required
def delete_notes(request, pk=None):
    note = get_object_or_404(Notes, id=pk)
    note.delete()
    messages.success(request, "Note Deleted Successfully!")
    return redirect('notes')

# Notes Detail View (Class-based View)
class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method=='POST':
        form=HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            homeworks=Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished   
            )
            homeworks.save()
            messages.success(request,f'Homework Added Successfully!!!')
    else:
        form = HomeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
        
    context={'homeworks':homework,'homeworks_done':homework_done,'form':form}
    return render(request,'dashboard/homework.html',context)

@login_required
def update_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    if homework.is_finished==True:
        homework.is_finished=False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')

@login_required
def youtube(request):
    if request.method=='POST':
        form=DashboardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=10)
        result_list=[]
        for i in video.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc+=j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form=DashboardForm()

    context = {'form':form}
    return render(request,'dashboard/youtube.html',context)

@login_required
def todo(request):
    if request.method=='POST':
        form=TodoForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            todos=Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )
            todos.save()
            messages.success(request,f'Todo Added Successfully!!!')
    else:
        form=TodoForm()
    todo=Todo.objects.filter(user=request.user)
    if len(todo)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,'dashboard/todo.html',context)

@login_required
def toggle_todo(request, id):
    todo = get_object_or_404(Todo, id=id)
    todo.is_finished = not todo.is_finished
    todo.save()
    return redirect('todo') 

@login_required
def delete_todo(request,id):
    todo = get_object_or_404(Todo, id=id)
    todo.delete()
    return redirect('todo')

@login_required
def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = f'https://www.googleapis.com/books/v1/volumes?q={text}'
        r = requests.get(url)
        
        # Check if the API request was successful (status code 200)
        if r.status_code == 200:
            ans = r.json()

            # Check if the 'items' key exists in the response
            if 'items' in ans:
                result_list = []
                for i in range(min(10, len(ans['items']))):  # Use min to avoid index errors
                    volume_info = ans['items'][i]['volumeInfo']  # Extract volumeInfo
                    result_dict = {
                        'title': volume_info.get('title'),
                        'subtitle': volume_info.get('subtitle'),
                        'description': volume_info.get('description'),
                        'count': volume_info.get('pageCount'),
                        'categories': volume_info.get('categories'),
                        'rating': volume_info.get('averageRating'),
                        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail'),
                        'preview': volume_info.get('previewLink')
                    }
                    result_list.append(result_dict)

                context = {
                    'form': form,
                    'results': result_list
                }
            else:
                # If no 'items' key, handle the case where there are no results
                messages.error(request, "No books found for your search query.")
                context = {'form': form}
        else:
            # Handle the case where the API request fails (non-200 status code)
            messages.error(request, "There was an error with the book search. Please try again later.")
            context = {'form': form}

        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()

    context = {'form': form}
    return render(request, 'dashboard/books.html', context)

@login_required
def wiki(request):
    if request.method=='POST':
        text=request.POST['text']
        form=DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form=DashboardForm()
        context={
            'form':form
        }

    return render(request,'dashboard/wiki.html',context)

def register(request):
    if request.method=='POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"Account Created Successfully!!!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context={
        'form':form
    }
    return render(request,'dashboard/register.html',context)

@login_required
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done
    }
    return render(request,'dashboard/profile.html',context)

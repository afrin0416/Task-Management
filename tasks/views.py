from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from tasks.models import Employee, Task, TaskDetail, Project
from datetime import date
from django.db.models import Q
from django.db.models import Count, Max, Min, Avg
from django.contrib import messages


# Create your views here.


def manager_dashboard(request):
     type = request.GET.get('type', 'all')
    # print(type)

    # getting task count
    # total_task = tasks.count()
    # completed_task = Task.objects.filter(status="COMPLETED").count()
    # in_progress_task = Task.objects.filter(status='IN_PROGRESS').count()
    # pending_task = Task.objects.filter(status="PENDING").count()
        # total_task = tasks.count()
    # completed_task = Task.objects.filter(status="COMPLETED").count()
    # in_progress_task = Task.objects.filter(status='IN_PROGRESS').count()
    # pending_task = Task.objects.filter(status="PENDING").count()

    # count = {
    #     "total_task":
    #     "completed_task":
    #     "in_progress_task":
    #     "pending_task":
    # }

     counts = Task.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='COMPLETED')),
        in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
        pending=Count('id', filter=Q(status='PENDING')),

    )
    # Retriving task data

     base_query = Task.objects.select_related(
        'details').prefetch_related('assigned_to')

     if type == 'completed':
        tasks = base_query.filter(status='COMPLETED')
     elif type == 'in-progress':
        tasks = base_query.filter(status='IN_PROGRESS')
     elif type == 'pending':
        tasks = base_query.filter(status='PENDING')
     elif type == 'all':
        tasks = base_query.all()
   

     context = {
        "tasks": tasks,
        "counts": counts,
    }
     return render(request, "dashboard/manager-dashboard.html", context)


def user_dashboard(request):
    return render(request, "dashboard/userdashboard.html")
def test(request):
    return render(request, "test.html")

def create_task(request):
    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            return redirect('create-task')
    else:
        task_form = TaskModelForm()
        task_detail_form = TaskDetailModelForm()

    return render(request, "task_form.html", {
        "task_form": task_form,
        "task_detail_form": task_detail_form
    })
        

            # data = form.cleaned_data
            # title = data.get('title')
            # description = data.get('description')
            # due_date = data.get('due_date')
            # assigned_to = data.get('assigned_to')  # list [1,3]

            # task = Task.objects.create(
            #     title=title, description=description, due_date=due_date)

            # # Assign employee to tasks
            # for emp_id in assigned_to:
            #     employee = Employee.objects.get(id=emp_id)
            #     task.assigned_to.add(employee)

            # return HttpResponse("Task Added successfully")
def update_task(request, id):
        task = Task.objects.get(id=id)
        task_form = TaskModelForm(request.POST, instance=task)  # For GET
        task_detail_form = TaskDetailModelForm(request.POST, instance=task.details)

        if request.method == "POST":
           task_form = TaskModelForm(request.POST, instance=task)
           task_detail_form = TaskDetailModelForm(request.POST, instance=task.details)

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('create-task')


        context = {"task_form": task_form, "task_detail_form": task_detail_form}
        return render(request, "task_form.html", context)

def delete_task(request, id):
    
    if request.method == "POST":
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request, "Task Deleted Successfully")
        return redirect('manager-dashboard')
    else:
        messages.error(request,'something went wrong')
        return redirect('manager-dashboard')




def view_task(request):
    projects = Project.objects.annotate(
        num_task=Count('task')).order_by('num_task')
    return render(request, "show_task.html", {"projects": projects})
    
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from tasks.models import Task, TaskDetail, Project
from datetime import date
from django.db.models import Q, Count, Max, Min, Avg
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, 
from django.contrib.auth.mixins import PermissionRequiredMixin ,UserPassesTestMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView, DetailView, UpdateView


# Class Based View Re-use example


class Greetings(View):
    greetings = 'Hello Everyone'

    def get(self, request):
        return HttpResponse(self.greetings)


class HiGreetings(Greetings):
    greetings = 'Hi Everyone'


class HiHowGreetings(Greetings):
    greetings = 'Hi Everyone, How are you'


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_employee(user):
    return user.groups.filter(name='Manager').exists()


@user_passes_test(is_manager, login_url='no-permission')
class ManagerDashboardView(View):
    template_name = "dashboard/manager-dashboard.html"

    def get(self, request, *args, **kwargs):
        task_type = request.GET.get('type', 'all')

        # Task counts
        counts = Task.objects.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            pending=Count('id', filter=Q(status='PENDING')),
        )

        base_query = Task.objects.select_related(
            'details'
        ).prefetch_related(
            'assigned_to'
        )

        if task_type == 'completed':
            tasks = base_query.filter(status='COMPLETED')
        elif task_type == 'in-progress':
            tasks = base_query.filter(status='IN_PROGRESS')
        elif task_type == 'pending':
            tasks = base_query.filter(status='PENDING')
        else:
            tasks = base_query.all()

        context = {
            "tasks": tasks,
            "counts": counts,
            "role": "manager",
        }

        return render(request, self.template_name, context)


class EmployeeDashboardView(UserPassesTestMixin, View):
    template_name = "dashboard/user-dashboard.html"

    def test_func(self):
        return is_employee(self.request.user)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

@login_required
@permission_required("tasks.add_task", login_url='no-permission')
def create_task(request):
    # employees = Employee.objects.all()
    task_form = TaskModelForm()  # For GET
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            return redirect('create-task')

    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)


# variable for list of decorators
create_decorators = [login_required, permission_required(
    "tasks.add_task", login_url='no-permission')]


class CreateTask(ContextMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    """ For creating task """
    permission_required = 'tasks.add_task'
    login_url = 'sign-in'
    template_name = 'task_form.html'

    """ 
    0. Create Task
    1. LoginRequiredMixin
    2. PermissionRequiredMixin
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = kwargs.get('task_form', TaskModelForm())
        context['task_detail_form'] = kwargs.get(
            'task_detail_form', TaskDetailModelForm())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            context = self.get_context_data(
                task_form=task_form, task_detail_form=task_detail_form)
            return render(request, self.template_name, context)

class UpdateTaskView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "tasks.change_task"
    login_url = "no-permission"
    template_name = "task_form.html"

    def get_task(self, id):
        return get_object_or_404(Task, id=id)

    def get(self, request, id, *args, **kwargs):
        task = self.get_task(id)
        task_form = TaskModelForm(instance=task)
        task_detail_form = None
        if task.details:
            task_detail_form = TaskDetailModelForm(instance=task.details)

        context = {
            "task_form": task_form,
            "task_detail_form": task_detail_form
        }
        return render(request, self.template_name, context)

    def post(self, request, id, *args, **kwargs):
        task = self.get_task(id)
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = None
        if task.details:
            task_detail_form = TaskDetailModelForm(
                request.POST, request.FILES, instance=task.details
            )

        if task_form.is_valid() and (task_detail_form is None or task_detail_form.is_valid()):
            task = task_form.save()

            if task_detail_form:
                task_detail = task_detail_form.save(commit=False)
                task_detail.task = task
                task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect("update-task", id=id)

        context = {
            "task_form": task_form,
            "task_detail_form": task_detail_form
        }
        return render(request, self.template_name, context)


class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        # print(context)
        if hasattr(self.object, 'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(
                instance=self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)

        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, 'details', None))

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', self.object.id)
        return redirect('update-task', self.object.id)


class DeleteTaskView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "tasks.delete_task"
    login_url = "no-permission"

    def post(self, request, id, *args, **kwargs):
        task = get_object_or_404(Task, id=id)
        task.delete()
        messages.success(request, "Task Deleted Successfully")
        return redirect("manager-dashboard")

    def get(self, request, id, *args, **kwargs):
        messages.error(request, "Something went wrong")
        return redirect("manager-dashboard")
class ViewTaskView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "tasks.view_task"
    login_url = "no-permission"
    template_name = "show_task.html"

    def get(self, request, *args, **kwargs):
        projects = Project.objects.annotate(
            num_task=Count('task')
        ).order_by('num_task')

        context = {
            "projects": projects
        }
        return render(request, self.template_name, context)




class ViewProjectView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "projects.view_project"
    login_url = "no-permission"
    template_name = "show_task.html"
    context_object_name = "projects"

    def get_queryset(self):
        """Return projects annotated with number of tasks"""
        return Project.objects.annotate(num_task=Count("task")).order_by("num_task")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        context = {self.context_object_name: queryset}
        return render(request, self.template_name, context)





class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "tasks.view_task"
    login_url = "no-permission"
    template_name = "task_details.html"

    def get_task(self, task_id):
        return get_object_or_404(Task, id=task_id)

    def get(self, request, task_id, *args, **kwargs):
        task = self.get_task(task_id)
        status_choices = Task.STATUS_CHOICES
        context = {
            "task": task,
            "status_choices": status_choices
        }
        return render(request, self.template_name, context)

    def post(self, request, task_id, *args, **kwargs):
        task = self.get_task(task_id)
        selected_status = request.POST.get("task_status")
        if selected_status:
            task.status = selected_status
            task.save()
        return redirect("task-details", task_id=task.id)



class TaskDetail(DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # {"task": task}
        # {"task": task, 'status_choices': status_choices}
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)


@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')

    return redirect('no-permission')

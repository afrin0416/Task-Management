from django.urls import task, path
from tasks.views import CreateTask, ManagerDashboardView, ManagerDashboardView ,EmployeeDashboardView, UpdateTaskView, create_task, 
 ViewProjectView, dashboard, delete_task, TaskDetailView, ViewTaskView, create_task, view_task, UpdateTaskView, DeleteTaskView, task_details, dashboard, Greetings, HiGreetings, HiHowGreetings, CreateTask, ViewProject, TaskDetail, UpdateTask

urlpatterns = [
   path("manager/dashboard/",ManagerDashboardView.as_view(),name="manager-dashboard"),
    path("employee/dashboard/",EmployeeDashboardView.as_view(), name="employee-dashboard" ),
    # path('create-task/', create_task, name='create-task'),
    path("tasks/update/<int:id>/", UpdateTaskView.as_view(), name="update-task"),
    path('create-task/', CreateTask.as_view(), name='create-task'),
    # path('view_task/', view_task, name='view-task'),
    path("tasks/delete/<int:id>/", DeleteTaskView.as_view(), name="delete-task"),
    # path('task/<int:task_id>/details/', task_details, name='task-details'),
    path('task/<int:task_id>/details/',
         TaskDetail.as_view(), name='task-details'),
    # path('update-task/<int:id>/', update_task, name='update-task'),
    path('update-task/<int:id>/', UpdateTask.as_view(), name='update-task'),
    path('delete-task/<int:id>/', delete_task, name='delete-task'),
    path('dashboard/', dashboard, name='dashboard'),
    path('greetings/', HiHowGreetings.as_view(greetings='Hi Good Day!'), name='greetings') 
    path("projects/view/", ViewProjectView.as_view(), name="view-project"),
    path("tasks/<int:task_id>/", TaskDetailView.as_view(), name="task-details"),]



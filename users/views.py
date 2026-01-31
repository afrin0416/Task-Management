from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm
from django.contrib import messages
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import AssignRoleForm,CreateGroupForm



class SignOutView(LoginRequiredMixin, View):
    login_url = "sign-in"

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("sign-in")

User = get_user_model()

# Create your views here.

# Test for users
"""
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['userprofile'] = UserProfile.objects.get(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        print("views", user_profile)
        context['form'] = self.form_class(
            instance=self.object, userprofile=user_profile)
        return context

    def form_valid(self, form):
        form.save(commit=True)
        return redirect('profile')
"""


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')


def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')

        else:
            print("Form is not valid")
    return render(request, 'registration/register.html', {"form": form})


def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()


class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm




class SignOutView(LoginRequiredMixin, View):
    login_url = "sign-in"

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("sign-in")


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')


@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    
    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'
    return render(request, 'admin/dashboard.html', {"users": users})



class AssignRoleView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "no-permission"
    template_name = "admin/assign_role.html"

    def test_func(self):
        """Check if user is admin"""
        return is_admin(self.request.user)

    def get_user(self, user_id):
        return get_object_or_404(User, id=user_id)

    def get(self, request, user_id, *args, **kwargs):
        user = self.get_user(user_id)
        form = AssignRoleForm()
        return render(request, self.template_name, {"form": form, "user": user})

    def post(self, request, user_id, *args, **kwargs):
        user = self.get_user(user_id)
        form = AssignRoleForm(request.POST)

        if form.is_valid():
            role = form.cleaned_data.get("role")
            user.groups.clear()  
            user.groups.add(role)
            messages.success(
                request,
                f"User {user.username} has been assigned to the {role.name} role"
            )
            return redirect("admin-dashboard")

        
        return render(request, self.template_name, {"form": form, "user": user})




class CreateGroupView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "no-permission"
    template_name = "admin/create_group.html"

    def test_func(self):
        """Check if user is admin"""
        return is_admin(self.request.user)

    def get(self, request, *args, **kwargs):
        form = CreateGroupForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(
                request,
                f"Group {group.name} has been created successfully"
            )
            return redirect("create-group")

    
        return render(request, self.template_name, {"form": form})





class GroupListView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "no-permission"
    template_name = "admin/group_list.html"
    context_object_name = "groups"

    def test_func(self):
        """Check if user is admin"""
        return is_admin(self.request.user)

    def get(self, request, *args, **kwargs):
        groups = Group.objects.prefetch_related("permissions").all()
        context = {self.context_object_name: groups}
        return render(request, self.template_name, context)


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)


"""

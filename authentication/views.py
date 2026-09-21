import secrets
import string
from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        # Step 1: Check if a user with this email even exists
        try:
            user_obj = User.objects.get(email=email_input)
            
            # Step 2: Email exists! Now test if the password matches
            user = authenticate(request, username=user_obj.username, password=password_input)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                # Email is valid, but authentication failed -> wrong password
                messages.error(request, "Incorrect password.")
                
        except User.DoesNotExist:
            # Email was not found anywhere in the PostgreSQL database
            messages.error(request, "Incorrect email address.")
            
    return render(request, 'authentication/login.html')

def home_view(request):
    # If the user is not logged in, STOP them and render the error page
    if not request.user.is_authenticated:
        return render(request, 'authentication/error.html')
        
    return render(request, 'authentication/home.html')

def user_management_view(request):
    # 1. If they aren't logged in at all, show the exact same login error page
    if not request.user.is_authenticated:
        return render(request, 'authentication/error.html')
    #  SECURITY BLOCK: Only allow superusers (admins)
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 1. ADD USER
        # Add Sub-Action
        if action == 'add':
            username = request.POST.get('username')
            email = request.POST.get('email')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                # 1. Automatically generate a random 8-character password
                allowed_chars = string.ascii_letters + string.digits
                generated_password = ''.join(secrets.choice(allowed_chars) for i in range(8))
                
                # 2. Create the user account in PostgreSQL
                new_user = User.objects.create_user(username=username, email=email, password=generated_password)
                
                # 3. Store a special temporary session key so our view knows who to redirect to
                request.session['newly_created_user_id'] = new_user.id
                
                # 4. Send the generated password to the frontend template safely
                # Replace your old messages.info line with this one:
                messages.info(request, f"PASSWORD_GENERATED:{generated_password}:{new_user.id}")
                messages.success(request, "User added successfully!")

        # 2. MODIFY USER (Updated to redirect to Profile Page)
        elif action == 'modify':
            target_email = request.POST.get('target_email')
            
            try:
                # 1. Find the user account based on the selected dropdown email
                user_to_edit = User.objects.get(email=target_email)
                
                # 2. Redirect straight to their dynamic profile modification file using their ID!
                return redirect('profile', user_id=user_to_edit.id)
                
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")

        # 3. DELETE USER
        elif action == 'delete':
            email_to_delete = request.POST.get('email')
            
            try:
                user_to_delete = User.objects.get(email=email_to_delete)
                user_to_delete.delete()
                messages.success(request, "User account permanently deleted successfully!")
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")

    # Fetch all user records from PostgreSQL so your new dropdown can display them
    all_users = User.objects.all().order_by('email')

    return render(request, 'authentication/user_management.html', {
        'users': all_users  # 👈 Make sure this context variable is being sent!
    })



# Import your new UserProfile table at the top of views.py if it isn't there:
from .models import UserProfile

def profile_view(request, user_id):  # 👈 Added user_id parameter here
    if not request.user.is_authenticated:
        return render(request, 'authentication/error.html')

    # Fetch the exact user account matching the ID in the URL address bar
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "This user account does not exist.")
        return redirect('home')

    # Security Check: Regular employees shouldn't look at other people's profiles!
    # If they aren't an admin, and they are trying to view someone else's ID, stop them.
    if not request.user.is_superuser and request.user.id != target_user.id:
        return redirect('home')

    # Grab or build the specific profile row for that target user
    profile, created = UserProfile.objects.get_or_create(user=target_user)

    # Show an advisory banner if an admin is inspecting a newly created account
    if request.user.is_superuser and request.user.id != target_user.id:
        # Check if the profile fields are empty to see if it's new
        if not profile.first_name and not profile.last_name:
            messages.info(request, f"Please complete the profile information for new user: {target_user.username}")

def profile_view(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    
    if request.method == "POST":
        # Capture standard fields
        profile.first_name = request.POST.get('first_name')
        profile.last_name = request.POST.get('last_name')
        profile.age = request.POST.get('age') or None
        profile.gender = request.POST.get('gender')
        profile.country = request.POST.get('country')
        profile.city = request.POST.get('city')
        profile.address = request.POST.get('address')
        profile.department = request.POST.get('department')
        profile.service = request.POST.get('service')
        profile.job_title = request.POST.get('job_title')
        
        # Capture the new reporting workflow data
        parent_id = request.POST.get('parent_report')
        if parent_id:
            try:
                profile.parent_report = UserProfile.objects.get(id=parent_id)
            except UserProfile.DoesNotExist:
                profile.parent_report = None
        else:
            # Auto-assign parent when possible according to org rules
            job = (profile.job_title or '').strip()
            if job == 'Manager':
                directors = UserProfile.objects.filter(department=profile.department, job_title='Director')
                if directors.count() == 1:
                    profile.parent_report = directors.first()
                else:
                    profile.parent_report = None
            elif job == 'Team Leader':
                managers = UserProfile.objects.filter(department=profile.department, job_title='Manager')
                profile.parent_report = managers.first() if managers.exists() else None
            elif job in ['Senior', 'Junior', 'Trainee']:
                team_leaders = UserProfile.objects.filter(department=profile.department, job_title='Team Leader')
                if team_leaders.exists():
                    profile.parent_report = team_leaders.first()
                else:
                    managers = UserProfile.objects.filter(department=profile.department, job_title='Manager')
                    profile.parent_report = managers.first() if managers.exists() else None
            else:
                profile.parent_report = None
            
        profile.save()
        return redirect('profile', user_id=user_id)

    # Fetch choices filtered by department so people only report to team members in their division
    managers = UserProfile.objects.filter(department=profile.department, job_title='Manager')
    team_leaders = UserProfile.objects.filter(department=profile.department, job_title='Team Leader')
    # Also pass all managers and team leaders so the frontend can populate selects dynamically
    managers_all = UserProfile.objects.filter(job_title='Manager')
    team_leaders_all = UserProfile.objects.filter(job_title='Team Leader')
    # All directors for dynamic department lookup
    directors_all = UserProfile.objects.filter(job_title='Director')
    # Directors (usually only one per department)
    directors = UserProfile.objects.filter(department=profile.department, job_title='Director')

    context = {
        'profile': profile,
        'target_user': profile.user,
        'managers': managers,
        'team_leaders': team_leaders,
        'directors': directors,
        'managers_all': managers_all,
        'team_leaders_all': team_leaders_all,
        'directors_all': directors_all,
    }
    return render(request, 'authentication/profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def stickman_view(request):
    # Fetch all user profiles from PostgreSQL
    profiles = UserProfile.objects.select_related('user').all()
    
    # Organize all workers dynamically by department and job hierarchy
    departments_map = {}
    for p in profiles:
        # Skip profiles without a department assignment
        if not p.department:
            continue
        dept = p.department
        if dept not in departments_map:
            departments_map[dept] = {
                'director': None,
                'managers': [],
                'team_leaders': [],
                'other_employees': []
            }
        
        # Separate by job title into hierarchy
        if p.job_title == 'Director':
            departments_map[dept]['director'] = p
        elif p.job_title == 'Manager':
            departments_map[dept]['managers'].append(p)
        elif p.job_title == 'Team Leader':
            departments_map[dept]['team_leaders'].append(p)
        else:  # Senior, Junior, Trainee
            departments_map[dept]['other_employees'].append(p)
        
    return render(request, 'authentication/stickman.html', {
        'departments_map': departments_map
    })
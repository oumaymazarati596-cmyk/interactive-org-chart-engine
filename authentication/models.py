from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # This links the profile directly to your existing login user account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Information
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Location Information
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # Company Structure
    DEPARTMENT_CHOICES = [
        ('informatique', 'Informatique'),
        ('HR', 'Human Resources (HR)'),
    ]
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    service = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ==========================================
    # NEW PARENT REPORT RELATIONFIELD FOR ORG CHART TEAM MATCHING
    # ==========================================
    parent_report = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinates'
    )

    def __str__(self):
        return f"Profile for {self.user.email if self.user.email else self.user.username}"
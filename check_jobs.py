import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import UserProfile

print("\nInfo Division Org Structure:")
print("="*60)
for p in UserProfile.objects.filter(department='Info').order_by('job_title'):
    parent_name = f"@{p.parent_report.user.username}" if p.parent_report else "None"
    print(f"{p.user.username:15} | {p.job_title:15} -> {parent_name}")

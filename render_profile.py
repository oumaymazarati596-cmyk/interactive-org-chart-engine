import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.test import RequestFactory
from django.contrib.auth.models import User
from authentication.views import profile_view
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

u = User.objects.first()
if not u:
    print('NO_USER')
    exit(1)

rf = RequestFactory()
req = rf.get('/')
req.user = u
# attach session
sess_mw = SessionMiddleware()
sess_mw.process_request(req)
req.session.save()
# attach messages
req._messages = FallbackStorage(req)

resp = profile_view(req, u.id)
content = resp.content.decode()
with open('rendered_profile.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('WROTE rendered_profile.html')

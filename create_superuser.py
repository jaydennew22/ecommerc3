import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User

User.objects.create_superuser('root', 'root@example.com', 'root')
print("Superuser created")
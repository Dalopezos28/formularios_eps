import sys
import os
sys.path.append(os.path.abspath('formularios'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formularios.settings')
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()

users = User.objects.all()

if users:
    print("List of users:")
    for user in users:
        print(f"- Username: {user.username}, Email: {user.email}, Is Superuser: {user.is_superuser}")
else:
    print("No users found.")

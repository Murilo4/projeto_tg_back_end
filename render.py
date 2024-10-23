import os
from django.core.management import execute_from_command_line

# Use a variável de ambiente PORT que o Render fornece
PORT = os.environ.get('PORT', 8000)  # Defina 8000 como padrão

if __name__ == "__main__":
    execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{PORT}'])

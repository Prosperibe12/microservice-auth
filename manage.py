#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from decouple import config 

def main():
    """Run administrative tasks."""
    environment = config('ENVIRONMENT')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_core.settings.'+environment)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    from django.conf import settings
    if 'test' in sys.argv:
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test_database',
            }
        }
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

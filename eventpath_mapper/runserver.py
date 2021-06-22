#!/usr/bin/env python
import os


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eventpath_mapper.settings")
    args = ["./manage.py", "runserver", "0.0.0.0:8111"]
    from django.core.management import execute_from_command_line    
    execute_from_command_line(args)

	

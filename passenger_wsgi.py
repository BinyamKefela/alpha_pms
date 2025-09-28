

import os
import sys

project_root = "/home/sunristg/alphapms/property_management"

sys.path.insert(0,project_root)
os.environ['DJANGO_SETTINGS_MODULE'] = 'property_management.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
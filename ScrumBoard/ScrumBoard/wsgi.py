"""
WSGI config for ScrumBoard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/home/pi/ISW19-20/ScrumBoard')
sys.path.append('/home/pi/ISW19-20/virtualenv/lib/python3.7/site-packages')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ScrumBoard.settings')

try:
    application = get_wsgi_application()
except:
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from seed_data import create_demo_data


if __name__ == '__main__':
    create_demo_data()

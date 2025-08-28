# CRM Celery Setup

## Requirements
- Redis
- Celery
- django-celery-beat

## Setup Steps
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
2. Install and run Redis:

sudo apt update
sudo apt install redis-server
redis-server --daemonize yes


3. Apply migrations:

python manage.py migrate


4. Start Celery worker:

celery -A crm worker -l info


5. Start Celery Beat scheduler:

celery -A crm beat -l info


6. Check generated reports:

cat /tmp/crm_report_log.txt


Reports are generated every Monday at 6:00 AM with:

Total Customers

Total Orders

Total Revenue


---

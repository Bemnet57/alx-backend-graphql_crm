#!/bin/bash
# crm/cron_jobs/clean_inactive_customers.sh

# Navigate to project root (adjust path if needed)
cd "$(dirname "$0")/../.."

# Run the cleanup inside Django shell
deleted_count=$(python3 manage.py shell -c "
import datetime
from crm.models import Customer
from django.utils import timezone

one_year_ago = timezone.now() - datetime.timedelta(days=365)

inactive_customers = Customer.objects.filter(
    orders__isnull=True
) | Customer.objects.exclude(
    orders__created_at__gte=one_year_ago
)

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log output with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt

#!/usr/bin/env python3
# crm/cron_jobs/send_order_reminders.py

import sys
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/order_reminders_log.txt"

def main():
    # Setup transport
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Calculate cutoff date
    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()

    # GraphQL query (adjust field names if different in your schema)
    query = gql("""
        query RecentOrders($cutoff: Date!) {
            orders(orderDate_Gte: $cutoff) {
                id
                customer {
                    email
                }
            }
        }
    """)

    # Execute query
    try:
        result = client.execute(query, variable_values={"cutoff": cutoff_date})
    except Exception as e:
        print(f"GraphQL query failed: {e}", file=sys.stderr)
        sys.exit(1)

    orders = result.get("orders", [])

    # Log orders
    with open(LOG_FILE, "a") as f:
        for order in orders:
            order_id = order.get("id")
            customer_email = order.get("customer", {}).get("email")
            log_line = f"{datetime.datetime.now().isoformat()} - Order {order_id}, Customer {customer_email}\n"
            f.write(log_line)

    print("Order reminders processed!")

if __name__ == "__main__":
    main()

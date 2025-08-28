import requests
import datetime
from celery import shared_task
from datetime import datetime

@shared_task
def generate_crm_report():
    url = "http://localhost:8000/graphql/"  # adjust if different

    query = """
    query {
        customers: allCustomers {
            totalCount
        }
        orders: allOrders {
            totalCount
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    """

    try:
        response = requests.post(url, json={"query": query})
        data = response.json()

        customers_count = data["data"]["customers"]["totalCount"]
        orders = data["data"]["orders"]["edges"]
        orders_count = data["data"]["orders"]["totalCount"]
        total_revenue = sum(float(order["node"]["totalAmount"]) for order in orders)

        log_entry = (
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            f"- Report: {customers_count} customers, {orders_count} orders, {total_revenue} revenue\n"
        )

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(log_entry)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} - ERROR: {str(e)}\n")

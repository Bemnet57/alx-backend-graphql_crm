import datetime
import requests
import datetime

def update_low_stock():
    url = "http://localhost:8000/graphql/"  # adjust if different
    query = """
    mutation {
        updateLowStockProducts {
            success
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """

    try:
        response = requests.post(url, json={"query": query})
        data = response.json()

        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(
                f"[{datetime.datetime.now()}] Response: {data}\n"
            )

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(
                f"[{datetime.datetime.now()}] ERROR: {str(e)}\n"
            )


def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_line = f"{timestamp} CRM is alive\n"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_line)

    # Optional: Query GraphQL hello field (requires gql lib + running server)
    try:
        from gql import gql, Client
        from gql.transport.requests import RequestsHTTPTransport

        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=1,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql(""" query { hello } """)
        result = client.execute(query)
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL hello: {result.get('hello')}\n")
    except Exception as e:
        # Fail silently to avoid breaking cron job
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")



def update_low_stock():
    url = "http://localhost:8000/graphql/"  # adjust if different
    query = """
    mutation {
        updateLowStockProducts {
            success
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """

    try:
        response = requests.post(url, json={"query": query})
        data = response.json()

        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(
                f"[{datetime.datetime.now()}] Response: {data}\n"
            )

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(
                f"[{datetime.datetime.now()}] ERROR: {str(e)}\n"
            )


import json
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm
import os
from dotenv import load_dotenv

# --- CockroachDB Cloud connection ---
# Copy your connection string from CockroachDB Cloud console.
# Example:
# postgresql://<user>:<password>@<host>:26257/geotrack?sslmode=verify-full&sslrootcert=<path-to-ca.crt>
load_dotenv()
COCKROACH_URL = os.getenv("COCKROACH_URL")

# def load_table_data(conn, table_name, records, columns):
#     with conn.cursor() as cur:
#         cur.execute("SET search_path = public;")
#         cur.execute("select current_database()")
#         print("DB:", cur.fetchone()[0])

#         cur.execute("show search_path")
#         print("search_path:", cur.fetchone()[0])

#         cur.execute("show tables from geotrack.public")
#         print("tables:", [r[0] for r in cur.fetchall()])
#         insert_query = f"""
#         INSERT INTO {table_name} ({", ".join(columns)})
#         VALUES %s
#         ON CONFLICT DO NOTHING;
#         """
#         values = [[r[col] for col in columns] for r in records]
#         execute_values(cur, insert_query, values)
#     conn.commit()

def load_table_data(conn, table_name, records_iter, columns, batch_size=10_000):
    with conn.cursor() as cur:
        # one-time session setup
        cur.execute("SET search_path = public;")
        cur.execute("select current_database()")
        print("DB:", cur.fetchone()[0])

        cur.execute("show search_path")
        print("search_path:", cur.fetchone()[0])

        cur.execute("show tables from geotrack.public")
        print("tables:", [r[0] for r in cur.fetchall()])

        insert_query = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING;
        """

        batch = []
        total_inserted = 0

        for rec in records_iter:              # records_iter can be tqdm(...)
            batch.append([rec[col] for col in columns])

            if len(batch) >= batch_size:
                execute_values(cur, insert_query, batch, page_size=batch_size)
                conn.commit()
                total_inserted += len(batch)
                batch = []                    # clear list
        # flush last partial batch
        if batch:
            execute_values(cur, insert_query, batch, page_size=batch_size)
            conn.commit()
            total_inserted += len(batch)

        print(f"{table_name}: {total_inserted:,} rows loaded")

def load_accounts(path="./data/accounts.json"):
    with open(path) as f: data = json.load(f)
    cols = ["id", "name", "tier", "active", "home_region", "created_at"]
    return data, cols, "accounts"

def load_carriers(path="./data/carriers.json"):
    with open(path) as f: data = json.load(f)
    cols = ["id", "name", "scac", "contact_email", "active", "created_at"]
    return data, cols, "carriers"

def load_parcels(path="./data/parcels.json"):
    with open(path) as f: data = json.load(f)
    cols = ["tracking_id", "account_id", "carrier_id", "origin_region", "source_location", "destination_location",
            "destination_region", "status", "last_event_ts",
            "created_at", "updated_at"]
    return data, cols, "parcels"

def run_load():
    print("Connecting to CockroachDB Cloud...")
    conn = psycopg2.connect(COCKROACH_URL)
    print("Connected.")

    for loader in [load_parcels]:
        data, cols, table = loader()
        print(f"Loading {len(data):,} records into {table}...")
        load_table_data(conn, table, tqdm(data, desc=f"{table}"), cols)

    conn.close()
    print("All tables loaded successfully.")

if __name__ == "__main__":
    run_load()

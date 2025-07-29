from google.cloud import bigquery

def push_to_bigquery(df, project_id, dataset_id, table_id, unique_col="link"):
    print(f"Starting to push data to BigQuery table {table_id}")
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    if table_exists(client, dataset_id, table_id):
        query = f"SELECT {unique_col} FROM `{table_ref}`"
        existing_df = client.query(query).to_dataframe()
        new_df = df[~df[unique_col].isin(existing_df[unique_col])]
    else:
        print("Table not found. Will create new one.")
        new_df = df

    if new_df.empty:
        print("No new data to insert.")
        return

    job = client.load_table_from_dataframe(new_df, table_ref)
    job.result()

    print(f"Inserted {len(new_df)} new rows to BigQuery: {table_ref}")

def table_exists(client, dataset_id, table_id):
    try:
        client.get_table(f"{dataset_id}.{table_id}")
        return True
    except Exception:
        return False

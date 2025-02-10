##### LOAD LIBRARIES
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

####

##### AMIE LIBRARIES
from .auto_analytics_utils import *


def grab_tiktok_stats_grouped(client_id, st_date, end_date):

    # Authenticate using the service account
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

    # Initialize BigQuery client
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    # Query BigQuery
    query = f"""
        SELECT 
        CONCAT(objective_type, ' ', COALESCE(campaign_product_source, '')) AS obj_camp_source,
        ROUND(SUM(spend), 2) AS Spend, 
        ROUND(SUM(total_complete_payment_rate), 2) AS DTC_Revenue,
        ROUND(SUM(total_onsite_shopping_value), 2) AS TTS_Revenue,
        SUM(follows) AS Follows,
        SUM(engaged_view) AS Views,
        SUM(engagements) AS Engagements,
        SUM(impressions) AS Impressions,
        SUM(conversions) AS Conversions
        FROM reporting.campaign_conversions
        WHERE advertiser_name='{client_id}'
        AND date BETWEEN '{st_date}' AND '{end_date}'
        GROUP BY obj_camp_source;
    """
    query_job = client.query(query)

    # Convert the query results to a Pandas DataFrame
    return query_job.to_dataframe()

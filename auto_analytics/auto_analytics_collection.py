##### LOAD LIBRARIES
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

####

##### AMIE LIBRARIES
from .auto_analytics_utils import *


def grab_tiktok_stats(client_id, st_date, end_date):

    # Authenticate using the service account
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

    # Initialize BigQuery client
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    # Query BigQuery
    query = f"""
        SELECT ROUND(SUM(spend), 2) AS Spend, 
        SUM(follows) AS Follows,
        ROUND(SUM(Spend)/(SUM(impressions)/1000), 2) AS CPM,
        ROUND(SUM(Spend)/SUM(engagements), 2) AS CPC,
        ROUND(100*SUM(engagements)/SUM(impressions), 2) AS `Engagement Rate`,
        ROUND(100*SUM(clicks)/SUM(impressions), 2) AS CTR,
        ROUND(SUM(Spend)/SUM(Follows), 2) AS CPF,
        ROUND(SUM(total_complete_payment_rate)/SUM(Spend), 2) AS `CP ROAS`
        FROM reporting.campaign_conversions
        WHERE advertiser_name='{client_id}'
        AND date BETWEEN '{st_date}' AND '{end_date}';
    """
    query_job = client.query(query)

    # Convert the query results to a Pandas DataFrame
    return query_job.to_dataframe()

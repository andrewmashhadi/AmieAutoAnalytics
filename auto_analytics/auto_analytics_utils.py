##### LOAD LIBRARIES
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
import pytz
import smtplib
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth import exceptions
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

##### GLOBAL VARIABLES

SCOPES = ['https://www.googleapis.com/auth/gmail.send'] # Define the SCOPES required for sending email via Gmail
CLIENT_SECRET_FILE = os.environ['CONFIG_PATH']+'/AmieAutoAnalytics/AAA_oauth_creds_file.json' # Path to OAuth 2.0 credentials JSON file
TOKEN_FILE = os.environ['CONFIG_PATH']+'/AmieAutoAnalytics/token.json' # OAuth Token storage location
SERVICE_ACCOUNT_FILE = os.environ['CONFIG_PATH']+'/AmieAutoAnalytics/AAA_service_account_key.json' # Path to BQ service account key JSON file
CONFIG_FILE_PATH = os.environ['CONFIG_PATH']+'/AmieAutoAnalytics/config.yaml'


#### UTILITY FUNCTION DEFINITIONS

def get_todays_date():
    """Returns today's date in Los Angeles time."""
    la_timezone = pytz.timezone('America/Los_Angeles')
    return datetime.now(la_timezone)

def get_yesterdays_date():
    """Returns yesterday's date in Los Angeles time."""
    today = get_todays_date()
    yest_date = today - timedelta(days=1)
    return yest_date

def get_last_weeks_date():
    """Returns last weeks's date in Los Angeles time."""
    today = get_todays_date()
    last_week_date = today - timedelta(days=7)
    return last_week_date

# Function to convert non-empty DataFrames to HTML
def df_to_html(df):
    return df.to_html(index=False, classes="small-table", border=1) if not df.empty else ""

def get_blended_table(perf_df):

    if not perf_df.empty:
        spend = perf_df['Spend'].sum()
        roas = (perf_df['DTC_Revenue'].sum() + perf_df['TTS_Revenue'].sum()) / spend
        
        data = {('Blended', ' Spend '): [f" ${spend:,.2f} "],
                ('Blended', ' ROAS '): [f" {roas:.2f} "]}
        
        multi_index = pd.MultiIndex.from_tuples(data.keys())
        return pd.DataFrame(data.values(), index=multi_index).T
    
    else:
        return pd.DataFrame()

def get_video_views_table(perf_df):

    view_df = perf_df[perf_df['obj_camp_source']=='VIDEO_VIEWS ']

    if not view_df.empty:
        views = view_df['Views'].sum()
        engagement_rate = view_df['Engagements'].sum() / view_df['Impressions'].sum()
        data = {
            ('Video Views', ' Views '): [f" {round(views)} "],
            ('Video Views', ' Engagement Rate '): [f" {engagement_rate:.2%} "],
            ('Benchmark', ' Engagement Rate '): [f" X.XX% "]
        }

        multi_index = pd.MultiIndex.from_tuples(data.keys())
        return pd.DataFrame(data.values(), index=multi_index).T

    else:
        return pd.DataFrame()

def get_community_table(perf_df):

    com_df = perf_df[perf_df['obj_camp_source']=='ENGAGEMENT ']

    if not com_df.empty:
        follows = com_df['Follows'].sum()
        CPF = com_df['Spend'].sum() / com_df['Follows'].sum()
        data = {
            ('Community Interaction', ' Follows '): [f" {round(follows)} "],
            ('Community Interaction', ' CPF '): [f" ${CPF:,.2f} "],
            ('Benchmark', ' CPF '): [f" $X.XX "]
        }

        multi_index = pd.MultiIndex.from_tuples(data.keys())
        return pd.DataFrame(data.values(), index=multi_index).T

    else:
        return pd.DataFrame()

def get_dtc_table(perf_df):

    dtc_df = perf_df[np.any((perf_df['obj_camp_source']=='WEB_CONVERSIONS ', perf_df['obj_camp_source']=='PRODUCT_SALES CATALOG'), axis=0)]

    if not dtc_df.empty:
        spend = dtc_df['Spend'].sum()
        CPA = dtc_df['Spend'].sum() / dtc_df['Conversions'].sum()
        ROAS = dtc_df['DTC_Revenue'].sum() / dtc_df['Spend'].sum()
        data = {
            ('Conversion - DTC', ' ROAS '): [f" {ROAS:.2f} "],
            ('Conversion - DTC', ' CPA '): [f" ${CPA:,.2f} "],
            ('Benchmark', ' ROAS '): [f" X.XX "]
        }

        multi_index = pd.MultiIndex.from_tuples(data.keys())
        return pd.DataFrame(data.values(), index=multi_index).T

    else:
        return pd.DataFrame()

def get_tts_table(perf_df):

    tts_df = perf_df[perf_df['obj_camp_source']=='PRODUCT_SALES STORE']

    if not tts_df.empty:
        spend = tts_df['Spend'].sum()
        CPA = tts_df['Spend'].sum() / tts_df['Conversions'].sum()
        ROAS = tts_df['TTS_Revenue'].sum() / tts_df['Spend'].sum()
        data = {
            ('Conversion - TTS', ' ROAS '): [f" {ROAS:.2f} "],
            ('Conversion - TTS', ' CPA '): [f" ${CPA:,.2f} "],
            ('Benchmark', ' ROAS '): [f" X.XX "]
        }

        multi_index = pd.MultiIndex.from_tuples(data.keys())
        return pd.DataFrame(data.values(), index=multi_index).T

    else:
        return pd.DataFrame()

def authenticate_gmail():
    """Authenticate and return a valid Gmail API client."""
    creds = None
    # Check if the token file exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials are found, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    # Build the Gmail API client
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to_list, subject, body):
    """Create an email message."""
    message = MIMEMultipart()
    message['to'] = ', '.join(to_list)  # Join the list of email addresses with commas
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body, 'html')
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(sender, subject, body, to_emails):
    """Send email using Gmail API."""
    # Authenticate using OAuth credentials
    service = authenticate_gmail()
    
    # Ensure `to_emails` is a list
    if not isinstance(to_emails, list):
        raise ValueError("     --> The 'to_emails' parameter must be a list of email addresses.")
    
    # Create the email message
    message = create_message(sender, to_emails, subject, body)
    
    try:
        # Send the email via Gmail API
        message_sent = service.users().messages().send(userId='me', body=message).execute()
        print(f"     --> Email sent successfully. Message ID: {message_sent['id']}")
    except exceptions.HttpError as error:
        print(f"     --> An error occurred: {error}")
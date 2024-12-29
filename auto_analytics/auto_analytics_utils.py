##### LOAD LIBRARIES
import os
import numpy as np
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
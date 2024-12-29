##### LOAD LIBRARIES
import os
import numpy as np
from datetime import datetime, timedelta, time
import pytz
import smtplib
import pandas as pd
import tabulate
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


#### UTILITY FUNCTION DEFINITIONS

def send_email_summaries(client_name, message, emails_to):
    
    subject = f"{client_name} Daily Analytics Report"

    # Combine all emails into a comma-separated string
    to_emails = ', '.join(emails_to)

    # Compose the message
    send_message = f"Good Morning," + message + "\n\nSincerely,\n\nAmie Analytics Team"
    
    # Send email to all recipients
    send_email(subject, send_message, "hello@amiesocial.com", to_emails)


def send_email(subject, message, from_email, to_email):
    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add message body
    msg.attach(MIMEText(message, 'plain'))

    # Connect to Gmail's SMTP server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login('analytics@amiesocial.com', os.environ['GMAIL_PW'])

    # Send email to all recipients
    server.sendmail(from_email, to_email.split(', '), msg.as_string())

    # Close the connection
    server.quit()
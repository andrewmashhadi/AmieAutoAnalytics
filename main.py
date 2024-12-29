##### LOAD LIBRARIES
import warnings
warnings.filterwarnings('ignore')
import yaml


##### AMIE LIBRARIES
from auto_analytics.auto_analytics_collection import *
from auto_analytics.auto_analytics_utils import *


#### MAIN DEFINITION
def build_subject(client_name):

    return f"{client_name}: Daily TikTok Performance \U0001F4C8"


def build_message(client_id):

    # Assuming these functions are defined elsewhere
    yest_date = get_yesterdays_date()
    perf_df = grab_tiktok_stats(client_id, yest_date.strftime('%Y-%m-%d'), yest_date.strftime('%Y-%m-%d'))

    # Add "$" in front of certain columns
    if 'Spend' in perf_df.columns:
        perf_df['Spend'] = perf_df['Spend'].apply(lambda x: f"${x:,.2f}")
    if 'CPM' in perf_df.columns:
        perf_df['CPM'] = perf_df['CPM'].apply(lambda x: f"${x:,.2f}")
    if 'CPC' in perf_df.columns:
        perf_df['CPC'] = perf_df['CPC'].apply(lambda x: f"${x:,.2f}")
    if 'CPF' in perf_df.columns:
        perf_df['CPF'] = perf_df['CPF'].apply(lambda x: f"${x:,.2f}")

    # Add "%" after certain columns
    if 'Engagement Rate' in perf_df.columns:
        perf_df['Engagement Rate'] = perf_df['Engagement Rate'].apply(lambda x: f"{x:.2f}%")
    if 'CTR' in perf_df.columns:
        perf_df['CTR'] = perf_df['CTR'].apply(lambda x: f"{x:.2f}%")

    # Convert DataFrame to an HTML table
    table_html = perf_df.to_html(index=False, classes="small-table", border=1)


    # Build the message with added newlines
    message = f"""
    <html>
        <body>
            <p>Hello,<br></p>
            <p>The following table contains a summary of yesterday's brand-level performance ({yest_date.strftime('%m/%d')}):</p>
            <br> 
            {table_html}
            <br> 
            <p>For a more detailed view, please visit your <a href="https://lookerstudio.google.com/reporting/f23afdf6-4dbe-4e57-8564-a4f0c744e5d8" target="_blank">Performance Overview Dashboard</a>.</p>
            <br>
            <p>Best,
            <br>
            <br>
            Amie's Analytics Team</p>
        </body>
    </html>
    """
    return message


def main(auto_settings):

    for client_id, client_settings in auto_settings.items():

        print(f"Building email for {client_settings['client_name_str']} ...")
        subject = build_subject(client_settings["client_name_str"])
        body = build_message(client_id)

        send_email(client_settings['sender_email'], subject, body, client_settings['client_emails'])


####

if __name__ == "__main__":

    #### LOAD SETTINGS
    with open(CONFIG_FILE_PATH, 'r') as file:
        auto_settings = yaml.safe_load(file)
    ####


    main(auto_settings)
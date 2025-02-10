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
    lw_date = get_last_weeks_date()
    perf_df = grab_tiktok_stats_grouped(client_id, lw_date.strftime('%Y-%m-%d'), yest_date.strftime('%Y-%m-%d'))

    # Generate DataFrames
    blended_df = get_blended_table(perf_df)
    view_df = get_video_views_table(perf_df)
    com_df = get_community_table(perf_df)
    dtc_df = get_dtc_table(perf_df)
    tts_df = get_tts_table(perf_df)

    # Generate tables only if they have data
    tables = {
        "Blended Performance Metrics": df_to_html(blended_df),
        "Video Views Metrics": df_to_html(view_df),
        "Community Engagement Metrics": df_to_html(com_df),
        "Direct-To-Consumer Metrics": df_to_html(dtc_df),
        "TikTok Shop Metrics": df_to_html(tts_df)
    }

    # Construct the HTML by including only non-empty tables
    tables_html = "".join(
        f"<h4>{title}</h4><br>{html}<br>" for title, html in tables.items() if html
    )

    # Build the message
    message = f"""
    <html>
        <body>
            <p>Good morning,<br><br></p>
            <p>Please see below for the L7D TikTok performance metrics. Feel free to email your dedicated Paid Account Manager with any questions.</p>
            <br>
            {tables_html if tables_html else "<p>No data available for this period...</p>"}
            <br> 
            <p>For a more detailed & interactive view, please visit your <a href="https://lookerstudio.google.com/reporting/f23afdf6-4dbe-4e57-8564-a4f0c744e5d8" target="_blank">Performance Overview Dashboard</a>.</p>
            <br>
            <p>Best,
            <br>
            <br>
            Amie's Paid Media Team</p>
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
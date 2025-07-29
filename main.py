from analysis.sentiment_model import sentiment_task
from etl.clean import clean_task
from etl.scrape_detik import scrape_detik
from etl.to_bigquery import push_to_bigquery
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure GOOGLE_APPLICATION_CREDENTIALS is set from .env
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if GOOGLE_CREDENTIALS:
    print(f"✅ GOOGLE_APPLICATION_CREDENTIALS loaded")
else:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS not found in .env or is empty")

# Main execution flow
print("Starting sentiment analysis pipeline...")
raw_df = scrape_detik()
cleaned_df = clean_task(raw_df)
final_df = sentiment_task(cleaned_df)

push_to_bigquery(
    final_df,
    project_id="compnet-2206825965",
    dataset_id="news_analysis",
    table_id="sentiment_results"
)
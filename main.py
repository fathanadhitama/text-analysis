from analysis.sentiment_model import sentiment_task
from etl.clean import clean_task
from etl.scrape_detik import scrape_detik
from etl.to_bigquery import push_to_bigquery
import os

def main(request):
    # Ambil env langsung dari Cloud Function, bukan .env
    # google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    # if google_credentials:
    #     print("✅ GOOGLE_APPLICATION_CREDENTIALS loaded")
    # else:
    #     print("❌ GOOGLE_APPLICATION_CREDENTIALS not found")

    print("🚀 Starting sentiment analysis pipeline...")
    raw_df = scrape_detik()
    cleaned_df = clean_task(raw_df)
    final_df = sentiment_task(cleaned_df)

    push_to_bigquery(
        final_df,
        project_id="compnet-2206825965",
        dataset_id="news_analysis",
        table_id="sentiment_results"
    )

    return "✅ ETL pipeline finished successfully", 200

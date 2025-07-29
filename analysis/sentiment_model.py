from transformers import pipeline

# Load sentiment analysis pipeline
sentiment = pipeline("sentiment-analysis", model="w11wo/indonesian-roberta-base-sentiment-classifier")

def sentiment_task(df):
    # Jalankan prediksi sentimen untuk semua teks
    df['sentiment'] = df['teks_cleaned'].apply(lambda x: sentiment(x)[0]['label'])
    print("Sentiment in dataset is classified")

    return df

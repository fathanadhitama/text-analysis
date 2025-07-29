import re
import pandas as pd
from datetime import datetime, timedelta

month_map = {
    'jan': 'jan',
    'feb': 'feb',
    'mar': 'mar',
    'apr': 'apr',
    'mei': 'may',
    'jun': 'jun',
    'jul': 'jul',
    'agu': 'aug',
    'sep': 'sep',
    'okt': 'oct',
    'nov': 'nov',
    'des': 'dec'
}

def clean_text(text):
    text = text.lower() 
    text = re.sub(r'[^a-zA-Z\s]', '', text) 
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def translate_month_short(text):
    # Replace short Indo month to English
    for indo, eng in month_map.items():
        text = re.sub(rf'\b{indo}\b', eng, text, flags=re.IGNORECASE)
    return text

def normalize_date(raw_text):
    raw_text = raw_text.lower()
    now = datetime.now()
    raw_text = re.sub(r'^(senin|selasa|rabu|kamis|jumat|sabtu|minggu),\s*', '', raw_text)

    if 'menit' in raw_text:
        return now.strftime('%Y-%m-%d')

    elif 'jam' in raw_text:
        match = re.search(r'(\d+)', raw_text)
        if match:
            hours = int(match.group(1))
            # If more than 7 hours ago, set as yesterday
            if hours > 7:
                return (now - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                return now.strftime('%Y-%m-%d')
    else:
        # Translate month
        text = translate_month_short(raw_text)

        # Remove WIB if present
        text = text.replace('wib', '').strip()

        # Try parsing full datetime
        try:
            dt = datetime.strptime(text, '%d %b %Y %H:%M')
            return dt.strftime('%Y-%m-%d')
        except:
            return text  # fallback

def clean_task(df):
    # gabungin judul dan deskripsi, lalu bersihin
    df['teks_cleaned'] = (df['judul'] + ' ' + df['deskripsi']).apply(clean_text)
    # Example usage if your DataFrame has a 'date_text' column
    df['waktu'] = df['waktu'].apply(normalize_date)

    print("Data is cleaned and normalized.")
    return df

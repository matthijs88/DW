import pandas as pd
import numpy as np

import brotli
import csv
import requests
import sys
from bs4 import BeautifulSoup

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import string
from langdetect import detect

from urllib.request import Request, urlopen  

# WEEK_RANGE = '2019-11-01--2019-11-08'
WEEK_RANGE = sys.argv[1]

# req = Request('https://spotifycharts.com/regional/au/weekly/' + WEEK_RANGE)
req = Request('https://spotifycharts.com/regional/gb/daily/' + WEEK_RANGE)

# req.add_header(':authority', 'spotifycharts.com')
# req.add_header(':path', '/regional')
# req.add_header(':scheme', 'https')
req.add_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')
req.add_header('accept-encoding', 'gzip, deflate, br')
req.add_header('accept-language', 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6')
req.add_header('cache-control', 'no-cache')
req.add_header('dnt', '1')
req.add_header('sec-fetch-mode', 'navigate')
req.add_header('sec-fetch-site', 'none')
req.add_header('sec-fetch-user', '?1')
req.add_header('upgrade-insecure-requests', '1')
# req.add_header('user-agent', '?1')
req.add_header('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36')


resp = urlopen(req)
# brotli.decompress(response.content)
binaryResponse = resp.read()
decodedResponse = brotli.decompress(binaryResponse).decode('UTF-8')

data = pd.read_html(decodedResponse)[0]
print(WEEK_RANGE + ' is starting')

def sentiment_of_lyrics(lyrics):
    if lyrics != "":
        sid = SentimentIntensityAnalyzer()
        return sid.polarity_scores(lyrics)
    else:
        return {'neg': 'none', 'neu': 'none', 'pos': 'none', 'compound': 'none' }

with open('dataGbDay/' + WEEK_RANGE + '.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(['Artist', 'title', 'streams', 'lyrics', 'neg', 'neu', 'pos', 'compound'])
    for index, row in data.iterrows():
        print(WEEK_RANGE + ':' + str(index / 200 * 100) + '%')
        # print(row['Track'])
        trackSplitted = row['Track'].rpartition(' by ')
        # print(trackSplitted[-1] + ': ' + trackSplitted[0] + 'Has streams: ' + str(row['Streams']))

        artist_name = trackSplitted[-1]
        song_title = trackSplitted[0]
        base_url = 'https://api.genius.com'
        headers = {'Authorization': 'Bearer ' + '2wN0egWOzQ-_KQDN4XkblxZoUjG2H_Zl-xq3uXNJhVFNaIkaM0QfvSWM4pm3fWhw'}
        search_url = base_url + '/search'
        data = {'q': song_title + ' ' + artist_name}
        response = requests.get(search_url, data=data, headers=headers)

        json = response.json()
        remote_song_info = None

        for hit in json['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break
                
        if remote_song_info:
            url = remote_song_info['result']['url']
        else :
            url = ""

        if url != "":
            page = requests.get(url)
            html = BeautifulSoup(page.text, 'html.parser')
            lyrics = html.find('div', class_='lyrics').get_text()
            # we detect the language of the lyrics, since the function that comes later in this document can only
            # calculate the sentiment of english lyrics we won't process lyrics that are not english
            if detect(lyrics) == "en":
                enter_removed = lyrics.replace('\u2005', ' ').replace('\n', ' ').replace('\u200a', ' ')
                punctuation_removed = enter_removed.translate(str.maketrans("","", string.punctuation))
        else:
            lyrics = ''
            punctuation_removed = ''
        
        sentiment = sentiment_of_lyrics(lyrics)
        writer.writerow([trackSplitted[-1], trackSplitted[0], str(row['Streams']), punctuation_removed, sentiment['neg'], sentiment['neu'], sentiment['pos'], sentiment['compound']])

print(WEEK_RANGE + ' is done')

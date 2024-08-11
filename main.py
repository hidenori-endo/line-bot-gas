import json
import os
import time
from xml.etree import ElementTree as ET

import requests
from fake_useragent import UserAgent
from linebot import LineBotApi
from linebot.models import TextSendMessage

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")


MAX_RETRIES = 5
RETRY_DELAY = 15


def get_rss_titles_and_urls(rss_url):
    for attempt in range(MAX_RETRIES):
        try:
            ua = UserAgent()
            header = {"User-Agent": str(ua.chrome)}
            response = requests.get(rss_url, headers=header)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            channel = root.find("channel")

            titles = []
            shortened_urls = []

            for item in channel.findall("item"):
                title = item.find("title").text
                print(title)

                original_url = item.find("link").text
                shortened_url = shorten_url(original_url)

                titles.append(title)
                shortened_urls.append(shortened_url)

            return titles, shortened_urls
        except requests.exceptions.RequestException as e:
            print(f"Error fetching RSS feed (Attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Giving up.")
                return None, None


def shorten_url(url):
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        print(f"Error shortening URL: {url}")
        return url  # エラー時は元のURLを返す


def chat_gpt(number_title):
    api_url = "https://api.openai.com/v1/chat/completions"
    messages = [
        {
            "role": "system",
            "content": "公認会計士の業務に役立つと思われる内容、すなわち会計基準や企業の粉飾決算、内部統制や監査、財務に関係するニュースがあれば、タイトルとURLを抽出して。企業の業績や株価、スキャンダルなどに関するものは抽出しないで。該当するものがなかった場合は「関連するニュースはありません」という文字列のみ出力して",
        },
        {"role": "user", "content": number_title},
    ]
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-type": "application/json",
    }
    data = {
        "model": "gpt-4o",
        "max_tokens": 2048,
        "temperature": 0.9,
        "messages": messages,
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    response_text = response.json()["choices"][0]["message"]["content"]
    return response_text


def send_line(message):
    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
    line_bot_api.push_message(LINE_GROUP_ID, TextSendMessage(text=message))

def main(request):
    rss_url = "https://news.google.com/news/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja"
    titles, shortened_urls = get_rss_titles_and_urls(rss_url)

    if titles is None or shortened_urls is None:
        print("Failed to fetch RSS feed. Exiting.")
        return

    articles = []
    number_title = ""

    for i, (title, url) in enumerate(zip(titles, shortened_urls)):
        articles.append([url, title])
        number_title += f"{i+1}. {title}\n"

    response_text = chat_gpt(number_title)
    if "関連するニュースはありません" not in response_text:
        send_line(response_text)

import json
import os
import re

import requests
from GoogleNews import GoogleNews
from linebot import LineBotApi
from linebot.models import TextSendMessage
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")


MAX_RETRIES = 5
RETRY_DELAY = 15


def get_news():
    UNNECESSARY_COMMON = "'\"\’\’”{}\[\]「」『』【】・|^\.|^\．|^\…"
    UNNECESSARY_PATTERN = rf"[\s|\u3000|{UNNECESSARY_COMMON}]"
    PARENTHESES_PATTERN = r"（.*?）|［.*?］|〈.*?〉"

    googlenews = GoogleNews(lang="ja", region="JP")
    googlenews.set_topic("CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtcGhHZ0pLVUNnQVAB")
    googlenews.get_news()

    # news_textとnews_linkの順番を保持するため、辞書に格納する
    news_data = {}
    for text, link in zip(googlenews.get_texts(), googlenews.get_links()):
        text_without_parentheses = re.sub(PARENTHESES_PATTERN, "", text)
        cleaned_text = re.sub(UNNECESSARY_PATTERN, "", text_without_parentheses)
        # 重複を避けるため、cleaned_textをキーとして辞書に格納
        news_data[cleaned_text] = link

    request_news = ""
    cnt = 0
    for text, link in news_data.items():
        request_news += f"{cnt},{text}\n"
        cnt += 1

    phrases_prompt = f"""
    ```
    [{request_news}]
    ```
    公認会計士の業務に役立つと思われる内容、すなわち会計基準や企業の粉飾決算、内部統制や不正、監査、財務に関係するニュースがあれば、番号を抽出して。
    短期的な企業業績や株価、スキャンダルなどに関するものは抽出しないで。
    該当するものがなかった場合は空のリストで出力して
    """
    return (phrases_prompt, list(news_data.keys()), list(news_data.values()))

def chat_gpt(prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "news_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            },
        },
    )
    return response.choices[0].message.content

def shorten_url(url):
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        print(f"Error shortening URL: {url}")
        return url  # エラー時は元のURLを返す


def send_line(message):
    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
    line_bot_api.push_message(LINE_GROUP_ID, TextSendMessage(text=message))

def main(request):
    prompt, titles, links = get_news()
    # print(prompt)
    # print("--------------------")
    response_text = chat_gpt(prompt)
    print(response_text)

    try:
        response_json = json.loads(response_text)
        selected_ids = [int(id) for id in response_json["id"]]
        selected_titles_and_links = [
            (titles[i], links[i]) for i in selected_ids if 0 <= i < len(titles)
        ]

        # LINEに送信するメッセージを作成
        message = ""
        for title, link in selected_titles_and_links:
            message += f"{title}\n{shorten_url(link)}\n\n"
        send_line(message)
        # print(message)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: {e}")

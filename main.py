import json
import os
import re

import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def remove_leading_whitespace(input_string: str) -> str:
    """
    入力文字列の各行の先頭の空白を削除する関数
    空白のみの行はそのまま残す
    """
    # 正規表現パターンを定義
    pattern = re.compile(r"^(?!\s*$)\s+", re.MULTILINE)
    # パターンにマッチする部分を削除
    return pattern.sub("", input_string)

def get_news():
    UNNECESSARY_COMMON = r"'\"\’\’”{}\[\]「」『』【】・|^\.|^\．|^\…"
    UNNECESSARY_PATTERN = rf"[\s|\u3000|{UNNECESSARY_COMMON}]"
    PARENTHESES_PATTERN = r"（.*?）|［.*?］|〈.*?〉"

    news_api_key = NEWS_API_KEY
    news_api_url = f"https://newsapi.org/v2/top-headlines?country=jp&category=business&apiKey={news_api_key}&pageSize=100&from=2024-08-16"

    response = requests.get(news_api_url)

    if response.status_code == 200:
        data = response.json()

        # news_textとnews_linkの順番を保持するため、辞書に格納する
        news_data = {}
        original_titles = []
        for article in data["articles"]:
            title = article["title"]
            link = article["url"]
            original_titles.append(title)
            text_without_parentheses = re.sub(PARENTHESES_PATTERN, "", title)
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
        以下の条件に該当するニュースがあれば、番号を抽出してください。
        メタ認知を用いて、重複する内容のニュースがあった場合、代表的な1つのみを出力してください。
        該当するものがなかった場合は空のリストで出力してください。

        抽出する条件：公認会計士の業務に役立つと思われる内容。すなわち企業の粉飾決算や不正、内部統制、監査、財務、会計基準に関係するもの
        抽出しない条件：短期的な企業業績、株価などに関するもの。行政や地方自治体が関係する不祥事に関するもの。
        """
        return (
            phrases_prompt,
            original_titles,
            list(news_data.keys()),
            list(news_data.values()),
        )
    else:
        # エラー処理
        print(f"Error: {response.status_code}")
        return None

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
    result = get_news()
    if result is None:
        return "ニュースの取得に失敗しました。"
    prompt, original_titles, titles, links = result
    print(prompt.replace("\n", ", "))
    print("--------------------")
    response_text = chat_gpt(remove_leading_whitespace(prompt))
    print(response_text)

    try:
        response_json = json.loads(response_text)
        selected_ids = [int(id) for id in response_json["id"]]
        selected_titles_and_links = [
            (original_titles[i], links[i])
            for i in selected_ids
            if 0 <= i < len(original_titles)
        ]

        # LINEに送信するメッセージを作成
        message = ""
        for title, link in selected_titles_and_links:
            message += f"{title}\n{shorten_url(link)}\n\n"
        if message != "":
            send_line(message)
            return "ok"
        else:
            return "関連するニュースは見つかりませんでした"
        # print(message)
    except (json.JSONDecodeError, KeyError) as e:
        return f"Error: {e}"

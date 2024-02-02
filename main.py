import os
import json
from linebot import LineBotApi
from linebot.models import TextSendMessage

channel_access_token = "hogehoge"
group_id = "fugafuga"

def main(request):

    request_json = request.get_json(silent=True)

    if request_json and 'message' in request_json:
        message = request_json['message']
    else:
        message = 'No message provided'

    # LINE Bot APIを使用してメッセージを送信
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(group_id, TextSendMessage(text=message))

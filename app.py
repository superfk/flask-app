import pygsheets, re, datetime, os
import pandas as pd
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from get_gsheet import gs

line_bot_api = LineBotApi('wLEey/GMZQx8ZsljBrRM2yZJKOk6icjcbNNfm0ewk4u/YEQ0Dh5hiZQ0ueRcSV6QvfDbbkBHgoC7wfbNsiJcFtTUgnKEepZbrZvTd3IpWtR4ck9GILHBH0X4iA4VfrIMztd0zflbgLIf+ld4o7T+8AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9302f9177c23c41b6a217497a482c0e8')

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    print(f"received event: {event}")
    print(f"received message: {event.message.text}")
    input_txt = event.message.text
    try:
        df, input_type = gs.smart_query(input_txt)
        if len(df) == 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='接下來沒有服事喔！'))
            return
        ret = gs.fmt_useful_message(df, input_type)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ret))
    except:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='好像找不到喔！'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
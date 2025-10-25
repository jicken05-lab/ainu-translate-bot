from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai, os

app = Flask(__name__)

# --- LINE設定 ---
line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# --- OpenAI設定 ---
openai.api_key = os.environ['OPENAI_API_KEY']

@app.route("/")
def index():
    return "AI Ainu Translate Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    prompt = f"日本語の文章をアイヌ語に翻訳し、カタカナまたはローマ字で出力してください。さらに日本語で短い文化的説明を添えてください。特殊文字や記号は使わないでください。翻訳する文章：{user_text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"Error: {str(e)}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

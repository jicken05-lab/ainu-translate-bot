import os
import openai
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- LINE環境変数 ---
line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
openai.api_key = os.environ['OPENAI_API_KEY']

# --- アイヌ語辞書を読み込み ---
dictionary_data = {}
with open("ainu_dictionary.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "：" in line:
            ainu, meaning = line.strip().split("：", 1)
            dictionary_data[ainu] = meaning

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    # --- 辞書にある単語を検索 ---
    for word in dictionary_data:
        if user_text in dictionary_data[word] or user_text == word:
            reply_text = word  # カタカナ＋ローマ字のみを返す
            break
    else:
        # --- AIに依頼（辞書補完＋文化的翻訳） ---
        prompt = f"""
        次の日本語をアイヌ語に翻訳してください。
        出力は「カタカナ (ローマ字)」の形式で、文化的に正確な言葉を選んでください。
        参考辞書：
        {dictionary_data}
        翻訳する文章：{user_text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_text = response.choices[0].message.content.strip()

    # --- LINEに返信 ---
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

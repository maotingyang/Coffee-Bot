# import apiai   # 嘗試串接dialogflow

from flask import Flask, request, abort
#先pip install line-bot-sdk
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImageMessage
)
from linebot.exceptions import LineBotApiError

# from hanziconv import HanziConv  # 繁簡轉換器
# from snownlp import SnowNLP      # 情緒分析
import detail_comment #情緒分析

import art  # 人臉拉花
from PIL import Image  # 剪裁圖片
import os.path
import glob
import upload_imgur_demo_2  # 把照片上傳雲端並回傳URL
import time #計時用

def convertjpg(jpgfile,outdir='./',width=400,height=300):        #剪裁圖片
    try:
        img=Image.open(jpgfile)
        # img = img.convert('RGB')   #png轉jpg才需要這行
        new_img=img.resize((width,height),Image.BILINEAR)
        file_name = os.path.basename(jpgfile)   #.replace('.png', '.jpg')
        new_img.save(os.path.join(outdir,file_name))
    except Exception as e:
        print(e)

# for jpgfile in glob.glob("data/man2coffee/trainA/*.jpg"):
#     convertjpg(jpgfile,"data/man2coffee/resize_trainA/")
for jpgfile in glob.glob("data/comic_head/*.png"):
    convertjpg(jpgfile,"data/man2comic/resize_trainB/")    


app = Flask(__name__)

line_bot_api = LineBotApi('LmkUVvPVszPSZ1j+a+nW0J9y+YRAfivvjE/8fD47Sqh0xVZ82jxNBxDr5pmAFuqbO9uxOPXzPmd0KiYs17y/GxIebobZBXu1320dRhVTatgnL3Azg0P+SrZI58tZf/EpVOrHBTtp1rWhPRzg8HjN0QdB04t89/1O/w1cDnyilFU=')     #負責與Line本身的API做溝通(就是幫你都做好準備了啦XD)
handler = WebhookHandler('3ac4d2dd700e214123f149fa1205323d')    #負責處理送過來的資料

opinion_flag = False    # 意見指標
pic_flag = False        # 拉花指標
pic_url = ''  

@app.route("/webhook", methods=['POST'])
def callback():
    print('進來了')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']   
    # print('signature是', signature)
    # get request body as text
    body = request.get_data(as_text=True)
    # print('body是', body)
    app.logger.info("Request body: " + body)
    
    # handle webhook body
    try:
        handler.handle(body, signature)
        print('OK')
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    global pic_url
    global pic_flag
    print('event是', event)
    print('id是', event.message.id)
    pic_id = event.message.id           #拿到圖片ID
    user_id = event.source.user_id      #拿到使用者ID
    print("user_id =", user_id)
    message_content = line_bot_api.get_message_content(pic_id)
    comfort_text = "稍等30秒…我正在努力畫、找靈感…(`・ω・´)"
    hint_text = "先逼要打擾我歐~~~"
    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=comfort_text),
                                                    TextSendMessage(text=hint_text)
                                                        ])           
    
    pic_flag = True
    latte_art(message_content, user_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global opinion_flag
    global pic_flag
    # print('event是', event)
    text = event.message.text
    
    if opinion_flag:   # 確定填意見才進入 
        result_list, speech, imgUrl = detail_comment.analysis(text)
        decorate_text = '請稍等…我正努力閱讀您的意見…(ง๑ •̀_•́)ง'
        result_text = '\n'.join(result_list)
        print('result text是', result_text)
        line_bot_api.reply_message(event.reply_token,[
                                    TextSendMessage(text=decorate_text),
                                    TextSendMessage(text=result_text),
                                    ImageSendMessage(original_content_url=imgUrl, preview_image_url=imgUrl),
                                    TextSendMessage(text=speech)])
        opinion_flag = False  # 意見旗標回復False

    if text == '意見':  # 檢查使用者是不是要填意見
        opinion_flag = True
        line_bot_api.reply_message(event.reply_token,
                                    TextSendMessage(text='請大聲說出您的意見吧，我…我才不是玻璃心勒'))
    else:
        fallback_text1 = "給我一張照片，我可以稍微秀一下我的拉花魔術 σ`∀´)σ"
        fallback_text2 = "也麻煩您用完餐後，輸入「意見」幫我填下意見調查！想知道你對偶滿不滿意嘛 (๑¯∀¯๑)"
        line_bot_api.reply_message(event.reply_token,[
                                    TextSendMessage(text=fallback_text1),
                                    TextSendMessage(text=fallback_text2)
                                    ])                                
    print("處理完意見了！")

# def makeWebhookResult(comments):   # 程式邏輯之所在      
    

def latte_art(thepic, user_id):
    t_start = time.time()
    with open('pic.jpg', 'wb') as fd:
        for chunk in thepic.iter_content():
            fd.write(chunk)
    convertjpg('pic.jpg')           # 剪裁照片         
    # art.give_me_pic('pic.jpg')    # 深度學習拉花
    # pic_url = upload_imgur_demo_2.pic_to_web('output/400.png')
    pic_url = upload_imgur_demo_2.pic_to_web('pic.jpg')
    print('拉完照片，url是' + pic_url + '準備上傳雲端') 
    try:
        line_bot_api.push_message(user_id, [ImageSendMessage(original_content_url=pic_url, preview_image_url=pic_url),
                                            TextSendMessage(text='精彩吧~神奇吧~哇哈哈哈')])
    except LineBotApiError as e:
    # error handle
        raise e
    t_end = time.time()
    t_total = t_end - t_start    
    print("照片送出，費時：", t_total)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
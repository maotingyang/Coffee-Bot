
#沒用結巴
import speech_recognition as sr
from os import path
from gtts import gTTS    
from pygame import mixer
import tempfile
# import jieba
import time
from hanziconv import HanziConv  #繁簡轉換器

drink_list = [
    '拿鐵','那堤',
    '美式','黑咖啡',
    '摩卡',
]
quantity_list = [
    '一','二','兩','三','四','五','六','七','八','九','十'
]
degree_list = [
    '冰','熱','去冰','不要冰','少冰','正常'
]
sweetness_list = [
    '無糖','不要糖','微糖','半糖','正常'
]
welcome_text = '歡迎來到羅伯咖啡，請問您今天想點甚麼？'
fail_text = '對不起，本店尚無販售此商品'

# jieba.suggest_freq('去冰', True)
# jieba.suggest_freq('拿鐵', True)
# jieba.suggest_freq('摩卡', True)
# jieba.suggest_freq('美式', True)
# jieba.suggest_freq('黑咖啡', True)

item_list = []
check_out = False

def speak(sentence):
    '''機器人說話'''
    sentence = HanziConv.toSimplified(sentence)
    with tempfile.NamedTemporaryFile(delete=True) as fp:  #產生一個有名字的暫存檔，使用完刪除
        response = polly_client.synthesize_speech(VoiceId='Zhiyu',
                LanguageCode='cmn-CN',
                OutputFormat='mp3', 
                Text = sentence)
        file = open('{}.mp3'.format(fp.name), 'wb', )
        file.write(response['AudioStream'].read())
        file.close()
#         tts = gTTS(sentence, lang='zh-tw')
#         tts.save('{}.mp3'.format(fp.name))
        mixer.init()
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play()
        
def listen():
    """聆聽客人點菜""" 
    global item_list
    r = sr.Recognizer()
    the_count = len(drink_list)   
    with sr.Microphone(device_index=0) as source:
        print('bot listening...')
        audio = r.listen(source)
        print('bot processing...')
        # time.sleep(2)
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        customer_drink = r.recognize_google(audio, language='zh-TW')
        print("Google Speech Recognition thinks you said " + customer_drink)
        if '結帳' in customer_drink :            
            if not item_list:
                speak('您尚未點餐歐！請繼續點餐')
                time.sleep(2)
            else:
                print('結帳')
                global check_out
                check_out = True

        elif '重新點餐' in customer_drink:             
            item_list = []
            speak('點餐紀錄已刪除，請重新點餐')
            time.sleep(2)
        else:    
            # seg_list = jieba.cut(customer_drink, cut_all=False)
    #         print(','.join(seg_list))
            info = {}
            # for word in seg_list:
                # print(word)
                # 找出數量詞
            print(customer_drink)    
            for quantity in quantity_list:
                if quantity in customer_drink:
                    info['數量'] = quantity
            for degree in degree_list:
                if degree in customer_drink:
                    info['溫度'] = degree
            for sweetness in sweetness_list:
                if sweetness in customer_drink:
                    info['甜度'] = sweetness        
            name_counts = len(drink_list)  # 餐點種類
            for name in drink_list:
                if name_counts == 0:
                    speak('本店尚無販售此飲料，請重新點餐')
                elif name in customer_drink:
                    info['品名'] = name        
                    print(info)
                    item_list.append(info)
                    print(item_list)
                    speak("你點了{}咖啡，{}杯，{}，{}，請繼續點餐，重新點餐，或說「結帳」完成點餐"
                        .format(info.get('品名'), info.get('數量', '一'), info.get('溫度',''), info.get('甜度','')))
                name_counts -= 1        
            time.sleep(3)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        listen()
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def checkOut():
    for info in item_list:
        speak('你點了{}咖啡，{}杯，{}，{}'.format(info.get('品名'), info.get('數量', '一'), info.get('溫度',''), info.get('甜度','')))
        time.sleep(5)
    
    speak('請稍等，餐點馬上為您送上！')
    time.sleep(4)
    print('end')
    
speak(welcome_text)
time.sleep(2)

while not check_out:      
    listen()

print(check_out)    
checkOut()

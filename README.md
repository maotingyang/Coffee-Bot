# Robo Coffee Bot
資策會時期專題作品

### 簡介
因為專題是做「AI咖啡廳」，這是一個幫助咖啡廳營運的chatbot
兩個功能：

#### 1.酷炫拉花：

給line上傳一張照片，會利用深度學習vgg19模型進行風格轉換，傳回一張有咖啡拉花感覺的照片

**注意：vgg19是19層的CNN模型，非常深，如果電腦GPU不夠力，要跑一段時間。**

#### 2.意見分析：

用python的snownlp套件製作文字情緒分析，負責處理客人的意見調查，若發現客人用餐感覺不佳，會立刻送折價券補償

**注意：我有利用jieba套件斷詞的功能，更深入分析客戶是對餐廳哪部分不滿意，並存進mysql資料庫，若不需要可註解掉**

---------------------------------------

另外，資料夾最外面有一個跟line chatbot無關的語音點餐機器人(voice_order_bot.py)，是用gtts跟speech_recognition兩個套件兜起來的，
注意speech_recognition的麥克風收音功能，需要pyaudio這個套件，但python3.7目前灌不起來，請愛用python3.6
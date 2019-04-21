from hanziconv import HanziConv  #繁簡轉換器
from snownlp import SnowNLP
import jieba
import MySQLdb

drink_menu = [
    '美式咖啡','咖啡','飲料'
    '拿鐵咖啡',
    '摩卡咖啡',
    '曼巴咖啡',
    '巴西咖啡',
    '藝妓咖啡',
    '藍山咖啡',
    '莊園咖啡',
]
meal_menu = [
    '肉醬義大利麵','義大利麵', '麵',
    '法國麵包','麵包',
    '雞肉三明治','三明治',
    '凱薩沙拉','沙拉',
    '海鮮焗烤飯','焗烤','飯',
    '餐點','食物'
]
other_feature = [
    '氣氛','品質',
    '裝潢','環境',
    '服務','AI','人工智慧','機器人'
    '時間',
    '等','等待',
    '價錢','價格',
    
]
drink_menu_simp = [HanziConv.toSimplified(x) for x in drink_menu]
meal_menu_simp = [HanziConv.toSimplified(x) for x in meal_menu]
other_menu_simp = [HanziConv.toSimplified(x) for x in other_feature]

# all_list = []
# all_list_simp = []
# all_list.extend(drink_menu)
# all_list.extend(meal_menu)
# all_list.extend(other_feature)
# for i in range(len(all_list)):
#     all_list[i] = HanziConv.toSimplified(all_list[i])

# for word in all_list:
#     word = HanziConv.toSimplified(word)
#     all_list_simp.append(word)
#     jieba.suggest_freq(word, True)
    
# all_list_simp 

# 分析顧客意見
def analysis(text):
    # text = u"AI感覺很酷炫！義大利麵也滿好吃的，咖啡倒是冷掉了，不太好喝，氣氛很有科技感"  # u是unicode的意思
    text = HanziConv.toSimplified(text)  #繁轉簡b
    s = SnowNLP(text)
    total_senti = s.sentiments
    print('意見總情緒歸類：', total_senti) 

    # 調頻
    jieba.suggest_freq('义大利面', True)

    drink_detail = {} #把滿意度更詳細的分類
    meal_detail = {}
    other_detail = {}
    for sentence in s.sentences:    #評論斷句
        cut = jieba.cut(sentence)
        sentence = SnowNLP(sentence)
        for word in cut:
            if word in drink_menu_simp:
                sent = sentence.sentiments         
                drink_detail[word] = [sent, sentence.sentences[0]]
            if word in meal_menu_simp:
                sent = sentence.sentiments         
                meal_detail[word] = [sent, sentence.sentences[0]]    
            if word in other_menu_simp:
                sent = sentence.sentiments         
                other_detail[word] = [sent, sentence.sentences[0]]   

    # 存進mysql
    conn=MySQLdb.connect(host="localhost",user="root", passwd="root", db="robo_coffee", charset='utf8') 
    cursor=conn.cursor()
    bad_items = {'drink':[], 'meal':[], 'other':[]}
    good_items = {'drink':[], 'meal':[], 'other':[]}
    for item in drink_detail:
        if drink_detail[item][0] <= 0.5:
            SQL="INSERT INTO drink_comments (item,score,comment) VALUES('{}',0,'{}')".format(item, drink_detail[item][1]) 
            cursor.execute(SQL)
            bad_items['drink'].append(item)
            
        else:
            SQL="INSERT INTO drink_comments (item,score,comment) VALUES('{}',1,'{}')".format(item, drink_detail[item][1]) 
            cursor.execute(SQL)
            good_items['drink'].append(item)
    for item in meal_detail:
        if meal_detail[item][0] <= 0.5:
            SQL="INSERT INTO meal_comments (item,score,comment) VALUES('{}',0,'{}')".format(item, meal_detail[item][1]) 
            cursor.execute(SQL)
            bad_items['meal'].append(item)
        else:
            SQL="INSERT INTO meal_comments (item,score,comment) VALUES('{}',1,'{}')".format(item, meal_detail[item][1]) 
            cursor.execute(SQL)
            good_items['meal'].append(item)        
    for item in other_detail:
        if other_detail[item][0] <= 0.5:
            SQL="INSERT INTO other_comments (item,score,comment) VALUES('{}',0,'{}')".format(item, other_detail[item][1]) 
            cursor.execute(SQL)
            bad_items['other'].append(item)
        else:
            SQL="INSERT INTO other_comments (item,score,comment) VALUES('{}',1,'{}')".format(item, other_detail[item][1]) 
            cursor.execute(SQL)
            good_items['other'].append(item)
    conn.commit()
    conn.close()        

    # 結果回傳chatbot
    result_list = []
    for key in good_items:        
        if good_items[key]:
            result_text = "您喜歡我們的{}，太感動了QQ".format('、'.join(good_items[key]))
            print(result_text)
            result_list.append(result_text)        
    for key in bad_items:        
        if bad_items[key]:
            result_text = "您對{}不甚滿意，真不好意思".format('、'.join(bad_items[key]))
            print(result_text)
            result_list.append(result_text)

    if total_senti > 0.6:
        speech = '您開心我們也開心！期待很快能再見到您！'
        imgUrl = 'https://is3-ssl.mzstatic.com/image/thumb/Purple125/v4/b9/d4/e7/b9d4e772-1bb4-2aaf-4544-ce8406e201d8/source/256x256bb.jpg'
    else:
        speech = '感謝您的批評和指教，我們會繼續努力，隨即贈送折價券給您！'   
        imgUrl = "https://scontent-frt3-2.cdninstagram.com/vp/b66cc0afec53847dba058d4c1b96b678/5C82ED8C/t51.2885-15/e35/s240x240/43914334_1466002923534617_1179572702714902544_n.jpg"
    #speech就是回應的內容
    
    return result_list, speech, imgUrl        

# #存入mysql
# conn=MySQLdb.connect(host="localhost",user="root", passwd="root", db="robo_coffee", charset='utf8') 
# cursor=conn.cursor()
# for item in bad_items:
#     SQL="INSERT INTO comments (item,score,comment) VALUES('{}','bad','{}')".format(item, detail[item][1]) 
#     cursor.execute(SQL)
# for item in good_items:
#     SQL="INSERT INTO comments (item,score,comment) VALUES('{}','good','{}')".format(item, detail[item][1]) 
#     cursor.execute(SQL)        
# conn.commit()
# conn.close()
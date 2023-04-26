#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki 4.0 Template For Python3

    [URL] https://api.droidtown.co/Loki/BulkAPI/

    Request:
        {
            "username": "your_username",
            "input_list": ["your_input_1", "your_input_2"],
            "loki_key": "your_loki_key",
            "filter_list": ["intent_filter_list"] # optional
        }

    Response:
        {
            "status": True,
            "msg": "Success!",
            "version": "v223",
            "word_count_balance": 2000,
            "result_list": [
                {
                    "status": True,
                    "msg": "Success!",
                    "results": [
                        {
                            "intent": "intentName",
                            "pattern": "matchPattern",
                            "utterance": "matchUtterance",
                            "argument": ["arg1", "arg2", ... "argN"]
                        },
                        ...
                    ]
                },
                {
                    "status": False,
                    "msg": "No matching Intent."
                }
            ]
        }
"""

from requests import post
from requests import codes
import math
import re
try:
    from intent import Loki_BigBig_Person
    from intent import Loki_BigGod_Person
except:
    from .intent import Loki_BigBig_Person
    from .intent import Loki_BigGod_Person


LOKI_URL = "https://api.droidtown.co/Loki/BulkAPI/"
USERNAME = ""
LOKI_KEY = ""
# 意圖過濾器說明
# INTENT_FILTER = []        => 比對全部的意圖 (預設)
# INTENT_FILTER = [intentN] => 僅比對 INTENT_FILTER 內的意圖
INTENT_FILTER = []
INPUT_LIMIT = 20

class LokiResult():
    status = False
    message = ""
    version = ""
    balance = -1
    lokiResultLIST = []

    def __init__(self, inputLIST, filterLIST):
        self.status = False
        self.message = ""
        self.version = ""
        self.balance = -1
        self.lokiResultLIST = []
        # filterLIST 空的就採用預設的 INTENT_FILTER
        if filterLIST == []:
            filterLIST = INTENT_FILTER

        try:
            result = post(LOKI_URL, json={
                "username": USERNAME,
                "input_list": inputLIST,
                "loki_key": LOKI_KEY,
                "filter_list": filterLIST
            })

            if result.status_code == codes.ok:
                result = result.json()
                self.status = result["status"]
                self.message = result["msg"]
                if result["status"]:
                    self.version = result["version"]
                    if "word_count_balance" in result:
                        self.balance = result["word_count_balance"]
                    self.lokiResultLIST = result["result_list"]
            else:
                self.message = "{} Connection failed.".format(result.status_code)
        except Exception as e:
            self.message = str(e)

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message

    def getVersion(self):
        return self.version

    def getBalance(self):
        return self.balance

    def getLokiStatus(self, index):
        rst = False
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["status"]
        return rst

    def getLokiMessage(self, index):
        rst = ""
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["msg"]
        return rst

    def getLokiLen(self, index):
        rst = 0
        if index < len(self.lokiResultLIST):
            if self.lokiResultLIST[index]["status"]:
                rst = len(self.lokiResultLIST[index]["results"])
        return rst

    def getLokiResult(self, index, resultIndex):
        lokiResultDICT = None
        if resultIndex < self.getLokiLen(index):
            lokiResultDICT = self.lokiResultLIST[index]["results"][resultIndex]
        return lokiResultDICT

    def getIntent(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["intent"]
        return rst

    def getPattern(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["pattern"]
        return rst

    def getUtterance(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["utterance"]
        return rst

    def getArgs(self, index, resultIndex):
        rst = []
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["argument"]
        return rst

def runLoki(inputLIST, filterLIST=[]):
    # 將 intent 會使用到的 key 預先設爲空列表
    resultDICT = {
       #"key": []
    }
    lokiRst = LokiResult(inputLIST, filterLIST)
    if lokiRst.getStatus():
        for index, key in enumerate(inputLIST):
            for resultIndex in range(0, lokiRst.getLokiLen(index)):
                # BigBig_Person
                if lokiRst.getIntent(index, resultIndex) == "BigBig_Person":
                    resultDICT = Loki_BigBig_Person.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # BigGod_Person
                if lokiRst.getIntent(index, resultIndex) == "BigGod_Person":
                    resultDICT = Loki_BigGod_Person.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

    else:
        resultDICT = {"msg": lokiRst.getMessage()}
    return resultDICT

def execLoki(content, filterLIST=[], splitLIST=[]):
    """
    input
        content       STR / STR[]    要執行 loki 分析的內容 (可以是字串或字串列表)
        filterLIST    STR[]          指定要比對的意圖 (空列表代表不指定)
        splitLIST     STR[]          指定要斷句的符號 (空列表代表不指定)
                                     * 如果一句 content 內包含同一意圖的多個 utterance，請使用 splitLIST 切割 content

    output
        resultDICT    DICT           合併 runLoki() 的結果，請先設定 runLoki() 的 resultDICT 初始值

    e.g.
        splitLIST = ["！", "，", "。", "？", "!", ",", "
", "；", "　", ";"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？")                      # output => ["今天天氣"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？", splitLIST=splitLIST) # output => ["今天天氣", "後天氣象"]
        resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"])                # output => ["今天天氣", "後天氣象"]
    """
    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    resultDICT = {}
    if contentLIST:
        if splitLIST:
            # 依 splitLIST 做分句切割
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            inputLIST = []
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # 去除空字串
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # 不做分句切割處理
            inputLIST = contentLIST

        # 依 INPUT_LIMIT 限制批次處理
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            lokiResultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)
            if "msg" in lokiResultDICT:
                return lokiResultDICT

            # 將 lokiResultDICT 結果儲存至 resultDICT
            for k in lokiResultDICT:
                if k not in resultDICT:
                    resultDICT[k] = []
                if type(lokiResultDICT[k]) == list:
                    resultDICT[k].extend(lokiResultDICT[k])
                else:
                    resultDICT[k].append(lokiResultDICT[k])

    return resultDICT

def testLoki(inputLIST, filterLIST):
    INPUT_LIMIT = 20
    for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
        resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)

    if "msg" in resultDICT:
        print(resultDICT["msg"])

def testIntent():
    # BigBig_Person
    print("[TEST] BigBig_Person")
    inputLIST = ['LP大大','116大大','大大們','大大與','大大變','張大大','有大大','橘大大','油大大','習大大','taoys大大','大大高hp','傑森大大','先進大大','其他大大','冨樫大大','勇者大大','台中大大','各位大大','哪位大大','大大似乎','大大你懂','大大只是','大大名稱','大大如何','大大幫助','大大您好','大大晚安','大大朋友','大大煩請','大大玩過','大大畢業','大大當您','大大的田','大大請問','大大請進','大大進來','大大關於','太子大大','客服大大','家族大大','工友大大','張大大是','張大大被','張大大說','想找大大','感恩大大','我方大大','拜託大大','有大大住','有大大有','有大大用','有大大租','有大大能','有無大大','板上大大','某某大大','根據大大','求救大大','版上大大','葉大大的','許多大大','請問大大','謝謝大大','请问大大','豬目大大','這位大大','郵焗大大','鄉民大大','鍾馗大大','開放大大','狐狸大大PO','DIY派的大大','其他位大大','可以請大大','各位大大們','各位大大好','和大大訂購','大大也找來','大大來報到','大大及前輩','大大就沒有','大大是老大','大大有推薦','大大有沒有','大大的相機','大大請幫忙','大大請幫我','好心的大大','就沒有大大','希望大大有','幫各位大大','張大大是個','愛合購大大','我建議大大','拜託大大ㄇ','最後大大把','有大大可以','有大大知道','板上的大大','柯基犬大大','求更新大大','湊了大大們','葉大大其實','請問大大们','請問大大們','請問大大幫','請大大告知','請大大幫忙','請大大救命','請大大解答','請教大大們','請站上大大','謝各位大大','謝謝大大們','谢谢大大了','塔羅師E大大','轉貼kent大大','25個大大評價','謝謝12味大大','也請大大代為','人人都是大大','再請教大大們','各位先進大大','各位大大們好','各位大大救命','各位資深大大','各位高手大大','員林大大請進','因為大大開始','大大可以幫忙','大大能幫一下','好心的大大幫','感謝各位大大','感謝大大分享','懂風水的大大','昨天張大大的','是衛生紙大大','會泰文的大大','有數據的大大','求求各位大大','流行用語大大','漫畫編輯大大','生活全配大大','目前大大讀書','英文大大請進','請問各位大大','請問工友大大','請問楊子大大','請問無敵大大','請大大們指導','請大大幫幫忙','請教各位大大','請教板上大大','請求大大解題','請知道的大大','謝謝pinoir大大','跪求大大解答','釣具店的大大','麥大大萬人迷','改70缸UP的大大','借用某大大的圖','動物森友會大大','各位大大也知道','各位大大注意囉','大大可幫忙一下','大大有沒有推薦','希望大大能提點','張大大老婆是誰','想請問諸位大大','感謝YAN大大分享','感謝綠到底大大','感謝起低ㄟ大大','懂電工的大大們','或是各位大大對','是否有大大認識','有大大有經驗嗎','有戴眼鏡的大大','有沒有大大買了','有養四趾的大大','歡迎各位大大來','當個母老虎大大','祝奧索網眾大大','給冨樫大大鼓掌','請各位大大幫忙','請各位大大賜教','請各位大大鑑賞','請問有大大是在','請問有大大知道','請大大要細察哦','請知道的大大們','請買傢大大放心','輸過頭大大今日','麻煩各位大大囉','麻煩大大們指點','亲爱的tggametw大大','請教各位大大SAMPO','超愛祈INORY大大啊','各位有經驗的大大','各大大誰能告訴我','因大大們反應熱烈','大大們能請告知嗎','希望大大們能提拔','感謝各位大大回復','我便是自己的大大','我發現大大的錯誤','有在玩底片的大大','有想水草的大大嗎','有裝無線電的大大','有請各位大大解惑','求求大大作一把圖','老游的朋友葉大大','請各位大大幫幫忙','請問一下版上大大','請問那位大大認識','請大大們幫我看看','請教一下客位大大','請教各位大大一下','請教各位房東大大','請教大大一些問題','請教會配電的大大','非常感謝大大留學','驅疫大神鍾馗大大','麻煩好心的大大們','麻煩站上大大一下','以增進大大幸福訣竅','傑森大大的最新文章','創作者大大狼的頭像','只是成名的只有大大','各位大大種過辣木嗎','各位有養四趾的大大','幾首祈大大翻唱的歌','玩很久的大大也可以','相信很多多核的大大','分紅保單坑殺保戶記者大大變保誠人壽的','請問小法令大大關於郵局外勤面試的自傳']
    testLoki(inputLIST, ['BigBig_Person'])
    print("")

    # BigGod_Person
    print("[TEST] BigGod_Person")
    inputLIST = ['G大神','AI大神','CG大神','Z9大神','大神F2','AI 大神','JS 大神','PPT大神','PS 大神','com大神','劉大神','大神666','大神ost','大神櫻','大神澪','帆大神','愛大神','柳大神','洪大神','甘大神','貓大神','金大神','陳大神','陸大神','DIY 大神','ESTi大神','G大神來','K8s 大神','PONY大神','Vee 大神','大神Dark','大神PONY','查G大神','Blaze大神','Kitty大神','NIGO 大神','iT邦大神','okami大神','time 大神','大神Danny','大神OGAMI','Googel大神','Google大神','google大神','中天大神','乖乖大神','人資大神','估狗大神','修圖大神','健身大神','凌玨大神','古狗大神','各位大神','咕狗大神','喬丹大神','單車大神','嘎嘎大神','堪比大神','大神ミオ','大神一郎','大神代言','大神手繪','大神教你','大神晃牙','大神涼子','大神穿去','大神語錄','大神貳號','大神金剛','大神雄子','大神零以','女籃大神','孤狗大神','巧虎大神','強化大神','彩妝大神','惡搞大神','感恩大神','抬槓大神','拜查大神','時尚大神','木村大神','木瓜大神','末廣大神','李安大神','毒舌大神','滑板大神','爆料大神','甘柳大神','產業大神','男單大神','科技大神','科普大神','箍狗大神','綜藝大神','美妝大神','耽美大神','股市大神','股溝大神','股狗大神','脫稿大神','腹黑大神','色彩大神','英文大神','葉秋大神','蔬果大神','請教大神','讓劉大神','谷哥大神','谷歌大神','買車大神','資安大神','辜狗大神','配樂大神','野狼大神','鍵盤大神','阿呆大神','電競大神','音樂大神','馬汀大神','驅魔大神','麥可大神','黑心大神','AI 大神Jeff','ASMR大神們','Arduino大神','GitHub 大神','Google 大神','G大神一下','SEO大神Rand','google 大神','連PONY大神','開啟G大神','AI 大神Demis','CG大神競賽','DK大神也有','IG筆記大神','PS大神自製','RT大神賜與','Xelloss 大神','不是PS大神','台灣AI大神','大神Norakura','大神幫我PS','捕魚大神OL','看看Z9大神','眾位CH大神','跪求PS大神','DON驅鬼大神','PTE大神回應','不過XDA大神','凱因斯大神','劉在石大神','劉在錫大神','劉大神激推','區塊鏈大神','問google大神','大神哀哀叫','大神工程師','大神幫幫忙','大神級作者','大神美化後','大神訪談篇','大神話家常','大神雄子說','或是大神們','找google大神','技術圈大神','拜google大神','新手到大神','新谷歌大神','日本大神級','是google大神','晶片大神Jim','有大神快拜','有大神推薦','業界的大神','求大神幫忙','看了大神們','網編圈大神','網路大神的','華爾街大神','要成為大神','請各位大神','超人氣大神','這木村大神','遇到大神了','達文西大神','那荒木大神','PONY大神來了','PONY大神公開','Photoshop 大神','XDA 大神推薦','不輸PONY大神','先知Woj 大神','問Google 大神','整理Dogg大神','曝料大神Evan','業界大神Rand','求大神幫P個','潮流大神NIGO','用Google 大神','AI大神吳恩達','B-boy大神Hong10','DK大神部落格','JavaScript 大神','Keras大神帶你','Keras大神歸位','PS大神耍任性','Z9大神都推薦','和你的IT大神','時尚大神Kanye','有請YAHOO大神','漫畫大神River','越獄大神Luca ','跑酷大神Jason','跪請excel大神','ATB大神召喚ing','CPU設計大神Jim','Google 大神dpkg ','Google大神翻成','Google大神變成','iPhone越獄大神','一位攝影大神','一位農產大神','世界頂尖大神','乖乖大神怒了','五個健身大神','交給估狗大神','使用google大神','來自野狼大神','做設計的大神','先拜google大神','利用Google大神','創新教學大神','劉大神又再次','募資大神開講','去拜Google大神','各位印度大神','各路大神見諒','問了google大神','問題請教大神','善逸圈粉大神','在google大神上','大神木村拓哉','大神等級人物','孤狗大神可以','密室逃脫大神','巧虎大神駕到','很多攝影大神','感謝Google大神','找了估狗大神','拖稿大神欽定','拜了估狗大神','拜了孤狗大神','拜見股溝大神','拜請Google大神','拜請google大神','拜請大神修圖','拜請孤狗大神','探討木村大神','推薦大神作家','日本搖滾大神','本站提供大神','根據Google大神','根據股溝大神','楊洋就是大神','樂高大神幫你','求各位大神們','求大神將照片','求救Google大神','求救各位大神','獨立遊戲大神','玩遊戲傍大神','用google大神找','用了Google大神','看到gslin 大神','社群行銷大神','祭出巧虎大神','福克斯大神教','精選大神ミオ','絕對科普大神','臺灣在地大神','色彩大神教你','萬分感謝大神','被大神治癒了','語音大神ミオ','請出google大神','請出孤狗大神','請問臉書大神','請問鈕扣大神','請大神們幫忙','谷哥大神創造','貓大神的頭像','超越google大神','這裡不要大神','還有Google大神','釣到極品大神','關於臉書大神','難得大神過境','館際合作大神',' ATB大神在一篇','GaryVee網路大神','GitHub 大神開課','Kaggle 大神創辦','Pony大神也愛用','P圖大神又來了','來問Google 大神','入坑7年的大神','問了Google 大神','國外PS大神James','大神ミオTwitter','安裝AlexxIT大神','拜了google 大神','於是就用G大神','有用G大神查過','求助Google 大神','網路大神GaryVee','請示Google 大神','谷哥大神 Google','FB社團謎片大神','GaryVee 網路大神','PS大神全員出動','Twitter 大神ミオ','Youtube大神Brandon','在特技大神Danny','托GIGO 大神福氣','而 meetissai 大神','與大神JQ的日子','請求PS大神幫忙','Google大神告訴你','Google大神好用心','Google大神非萬能','Google真的是大神','Google真的變大神','Youtube大神 Brandon','google大神都搞錯','不愧是木村大神','世界狼人殺大神','乖乖大神的行規','井柏然不夠大神','估狗大神也果然','估狗大神來解答','修圖大神kanahoooo','修圖大神出作業','修護大神積雪草','倚靠大神來開發','前些日子和大神','劉在石大神代言','參考google大神後','台灣在地大神們','國外大神的作品','在Google大神麾下','大神健身也要潮','大神級簡報製作','大神級耽美作者','大神級資安服務','媲美木村大神的','學會你就是大神','巧虎大神到我家','所以叫他劉大神','拜一下Google大神','拜一下google大神','拜一下辜狗大神','拜了拜谷歌大神','收羅了這些大神','改程式碼的大神','整理大神必殺技','於GOOGLE大神找到','晚上查估狗大神','木村大神很長情','某奉為本命大神','爆料大神曝光了','甚至令Google大神','由木村大神領軍','發現好立克大神','看過你就是大神','矽谷大神都來了','綜藝大神劉在錫','網路大神幫解答','網路大神治不好','網路大神讓你光','網路遍地有大神','美肌大神范冰冰','臉書大神很好用','與木村大神合作','許久不見的大神','請各位大神幫忙','請各位大神推薦','請教了辜狗大神','谷歌大神幫你醫','追蹤師大神東馬','這些大神的作品','酷狗大神找一下','除了Google大神外','電競大神帶回家','電競大神愛上我','電競大神暗戀我','靈感大神有眷顧','麻煩各位大神了','黑霧大神劉光仲','Google 大神動起來','Google 大神只能說','Google 大神太恐怖','Google 大神幫我在','Google 大神的商道','Pony大神如何駕馭','P圖大神又出招啦','以大神test520為例','修圖大神出3難題','快皈依Carb大神吧','恭送宇宙大神GIGO','招換大神時間 Sun','改搜尋Google 大神','求大神幫P帥氣點','等哪天Google 大神','讓Google 原本大神','Karma大神規範著你','ai由Kaggle大神Jeremy','不用再跪求PS大神','南韓首爾B-boy大神','跪求PS大神幫修圖','鋼琴大神AnimenzA叔','Clubhouse大神都來了','Google 大神9 月慶生','Google大神帶給我的','Google大神更多拜法','Google大神絕非虛名','google大神救回來了','一個是XDA大神推薦','上網求助孤狗大神','不過卻有韓國大神','也有大神們的碾壓','也讓木村拓哉大神','個人語音大神ミオ','假如劉大神被畫進','全省十大神祗之一','凡事求助網路大神','別再問Google大神了','又拜請了咕狗大神','只要提起孤狗大神','吾之駕前什府大神','呼叫館際合作大神','問了一下Google大神','土豪大神就了不起','在拜Google大神所賜','大神主線完全攻略','大神傳的價格推薦','大神國際有限公司','大神娛樂公司圖片','大神的正確捕捉法','大神的設計素材庫','大神真的改寫網速','平日都躺著的大神','徹底輸給栗子大神','想問各位飲料大神','我們這裡沒有大神','手辦大神最新力作','技術大神祕訣分享','把福克斯大神移動','投資大神講座門票','拜託大神們幫幫忙','數位行銷大神開講','文藝大神岩井俊二','於是求助Google大神','日劇大神木村拓哉','日本創作大神降臨','日本木村拓哉大神','是大神才能享有的','林信良大神簡報檔','根據GOOGLE大神指示','爆料大神釋出iPhone','知名YEEZY 爆料大神','華爾街教父級大神','裴揚大神大鋁交換','請出Google大神幫忙','請古狗Google大神查','請問各位前輩大神','請問各位印度大神','請問各位大神老手','請問這裡的大神們','讓你從小白變大神','谷歌大神啥都知道','頂尖大神開線上課','Mobile 科技大神培育','YouTube頻道大神ミオ','依據Google 大神找到','PS大神的明星刺青照','Staff發佈有大神快拜','下定決心要變成大神','來自網上的一位大神','大神ミオフィギュア','尾田大神創作的地方','彷彿沒有了孤狗大神','找google大神求教一番','某大神轉發了一條博','歡迎來到大神哈啦板','綜藝大神劉在錫領軍','請問大神要怎麼解決','入坑7年大神分享經驗','在Google 大神的指示下','經過Google 大神的指點','3 位Google 前大神來助戰','像大神一樣畫網路漫畫','沒有不可能的孤狗大神','現在竟然已經變成大神','Automator 大神再度請出場','Google 大神快要無所不能','又是Google 大神拯救了我','搜尋引擎老大Google 大神','根據偉大的咕狗大神表示','大神的LOGO 草圖是這樣畫的','每天打開陸綜看看楊洋大神','爆料大神釋出高清晰渲染圖','網路大神讓你光買零件就能','總經大神愛瑞克將傾囊相授','葉秋大神十年間最大的變化','要跟傾慕已久的大神面基啦','解謎PTT爆紅大神的都市傳說','請大神幫忙我解決語音問題','這招請出巧虎大神來帶領她','通常大神懶得跟你打高空砲','還是得到了大神指點的緣故','鄉民給了Google大神這個暱稱','Google 大神到底是怎麼運作的','並且雖然大神自己沒有意識到','劉大神主播妻當媽身材賽model ','劉大神再度聯手長頸鹿李光洙','阿帕契大神給我們的十個教訓','Google 大神竟然給了我一盞明燈','大神點兵Google庶民AI布局超展開','真的是天降即時箱大神來救我了','網友想像大神是蓄勢待發的鋼彈','被視為AI大神級人物的傑夫．迪恩']
    testLoki(inputLIST, ['BigGod_Person'])
    print("")


if __name__ == "__main__":
    # 測試所有意圖
    testIntent()

    # 測試其它句子
    filterLIST = []
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    resultDICT = execLoki("今天天氣如何？後天氣象如何？", filterLIST)            # output => ["今天天氣"]
    resultDICT = execLoki("今天天氣如何？後天氣象如何？", filterLIST, splitLIST) # output => ["今天天氣", "後天氣象"]
    resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"], filterLIST)      # output => ["今天天氣", "後天氣象"]
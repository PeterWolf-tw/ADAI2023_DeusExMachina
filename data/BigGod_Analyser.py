#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
import json
import os
import tempfile

accountDICT = {"user":"", "apikey":""}
try:
    with open("./account.info", encoding="utf-8") as f:
        accountDICT = json.load(f)
    if accountDICT["user"] == "" or accountDICT["apikey"] == "":
        print("使用每小時 2000 字免費額度中…")
except:
    print("找不到 account.info 設定檔！")


articut = Articut(accountDICT["user"], accountDICT["apikey"])

def main(dataFILE):
    """"""
    resultLIST = []
    tempDICT = tempfile.NamedTemporaryFile(mode="w+")
    json.dump({"_userDefined":["大神"]}, tempDICT)
    tempDICT.flush()
    with open(dataFILE, encoding="utf-8") as f:
        dataLIST = json.load(f)
    for data_d in dataLIST:
        articutDICT = articut.parse(data_d["text"].replace(" ", ""), userDefinedDictFILE=tempDICT.name)
        resultLIST.extend(articutDICT["result_pos"])
    return resultLIST


if __name__ == "__main__":
    targetDIR = "./大神"
    fileLIST = os.listdir(targetDIR)
    for i in fileLIST:
        resultLIST = []
        resultLIST = main("{}/{}".format(targetDIR, i))

        with open("{}".format(i.replace(".json", "_info.json")), encoding="utf-8", mode="a+") as f:
            json.dump(resultLIST, f, ensure_ascii=False)
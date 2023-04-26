#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
import json
import os
import re
from requests import post
import tempfile

tempDICT = tempfile.NamedTemporaryFile(mode="w+")
json.dump({"_userDefined":["大神"]}, tempDICT)
tempDICT.flush()

purgePat = re.compile("</?\w+(_\w+)?>")

accountDICT = {"user":"", "apikey":""}
with open("../account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)
articut = Articut(username=accountDICT["user"], apikey=accountDICT["apikey"])

def main():
    """"""
    return None


if __name__ == "__main__":
    targetSTR = "大神"
    srcDIR = "./src"
    fileLIST = os.listdir(srcDIR)
    for i_f in fileLIST:
        toAddLIST = []
        contentLIST = json.load(open("{}/{}".format(srcDIR, i_f)))
        for c_d in contentLIST:
            if targetSTR in c_d["title"]:
                titleResultDICT = articut.parse(c_d["title"], userDefinedDictFILE=tempDICT.name)
                for u_l in titleResultDICT["result_pos"]:
                    if "<UserDefined>{}</UserDefined>".format(targetSTR) in u_l:
                        toAddLIST.append(re.sub(purgePat, "", u_l))
                    else:
                        pass
            if targetSTR in c_d["text"]:
                titleResultDICT = articut.parse(c_d["text"], userDefinedDictFILE=tempDICT.name)
                for u_l in titleResultDICT["result_pos"]:
                    if "<UserDefined>{}</UserDefined>".format(targetSTR) in u_l:
                        toAddLIST.append(re.sub(purgePat, "", u_l))
                    else:
                        pass
            print(toAddLIST, len(toAddLIST))


        utteranceURL = "https://api.droidtown.co/Loki/Utterance/"
        payload = {
            "username" : accountDICT["user"],
            "loki_key" : "kU&emf+@9x2wUl*s*AgN4KR1^NluEN3",
            "intent_list": ["BigGod_Person"]
        }

        response = post(utteranceURL, json=payload).json()
        toAddLIST = list(set(toAddLIST)-set(response["results"]["BigGod_Person"]))

        for index_i in range(0, len(toAddLIST), 20):
            payload = {
                "username" : accountDICT["user"],
                "loki_key" : "kU&emf+@9x2wUl*s*AgN4KR1^NluEN3",
                "intent"   : "BigGod_Person",
                "utterance": toAddLIST[index_i:index_i+20],
                "func": "insert"
            }
            url = "https://api.droidtown.co/Loki/Command/"
            try:
                response = post(url, json=payload).json()
                print(response)
            except:
                with open("error.log", encoding="utf-8", mode="a+") as f:
                    json.dump(payload, f, ensure_ascii=False)







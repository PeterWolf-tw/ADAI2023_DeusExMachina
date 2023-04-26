#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import requests
import urllib
from requests_html import HTMLSession
from time import sleep
from random import choice


def parse_results(response):

    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".VwiC3b"

    results = response.html.find(css_identifier_result)

    output = []

    for result in results:

        item = {
            'title': result.find(css_identifier_title, first=True).text,
            'link': result.find(css_identifier_link, first=True).attrs['href'],
            'text': result.find(css_identifier_text, first=True).text
        }

        output.append(item)

    return output

def get_source(url):
    """Return the source code for the provided URL.

    Args:
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html.
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)

def get_results(query, minDate, maxDate):
    resultLIST = []
    PageCounter = 0
    query = urllib.parse.quote_plus(query)
    urlSTR = "https://www.google.co.uk/search?q=" + query + "&lr=lang_zh-TW&cr=countryTW&hl=zh_TW&tbs=ctr:countryTW,lr:lang_1zh-TW,cdr:1,cd_min:"+minDate+",cd_max:"+maxDate+"&start={0}&sa=N".format(PageCounter)
    #urlSTR = "https://www.googleapis.com/customsearch/v1?key=AIzaSyCun9vqeWGcTckJCf0pC0oytM2jyVTwRgA&cx=926e888071c474ecb:omuauf_lfve&q=lectures"+ query + "&lr=lang_zh-TW&cr=countryTW&hl=zh_TW&tbs=ctr:countryTW,lr:lang_1zh-TW,cdr:1,cd_min:"+minDate+",cd_max:"+maxDate
    print(urlSTR)
    response = get_source(urlSTR)
    print(response)
    sleep(3)
    resultLIST.extend(parse_results(response))
    while parse_results(response) !=[]:
        resultLIST.extend(parse_results(response))
        print(resultLIST[-1])
        print("Page: {}".format(PageCounter/10))
        PageCounter = PageCounter + 10
        urlSTR = "https://www.google.co.uk/search?q=" + query + "&lr=lang_zh-TW&cr=countryTW&hl=zh_TW&tbs=ctr:countryTW,lr:lang_1zh-TW,cdr:1,cd_min:"+minDate+",cd_max:"+maxDate+"&sxsrf=APwXEde5-uioIecu3pw9kuHzW0jOEdV80w:1682127546341&ei=ujpDZP3HFIOQ-Aar-bbgAQ&start={0}&sa=N&ved=2ahUKEwj9jPe2rbz-AhUDCN4KHau8DRw4KBDy0wN6BAgFEAQ&biw=1872&bih=933&dpr=1".format(PageCounter)
        #urlSTR = "GET https://www.googleapis.com/customsearch/v1?key=AIzaSyCun9vqeWGcTckJCf0pC0oytM2jyVTwRgA&cx=926e888071c474ecb:omuauf_lfve&q=lectures"+ query + "&lr=lang_zh-TW&cr=countryTW&hl=zh_TW&tbs=ctr:countryTW,lr:lang_1zh-TW,cdr:1,cd_min:"+minDate+",cd_max:"+maxDate
        response = get_source(urlSTR)
        sleep(choice([3, 4, 5]))
    return resultLIST



def google_search(query, minDate, maxDate):
    resultLIST = get_results(query, minDate, maxDate)
    return resultLIST


if __name__ == "__main__":
    querySTR = "大大"
    yearSTR = "2008"
    resultLIST = google_search(querySTR, "1/1/{}".format(yearSTR), "12/31/{}".format(yearSTR))
    print(resultLIST)
    with open("{}_{}.json".format(yearSTR, querySTR), encoding="utf-8", mode="w") as f:
        json.dump(resultLIST, f, ensure_ascii=False)
# /usr/bin/python
# -*- coding:utf-8 -*-
import requests
def getpage(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
        reponse = requests.get(url,headers=headers)
        if reponse.status_code == 200:
            return reponse.text
    except Exception as e:
        return None
    

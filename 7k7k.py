#!/usr/bin/evn python
# -*- coding: utf-8 -*-
'''
Created on 2016年8月9日

@author: hstking hstking@hotmail.com
'''

import urllib2
from bs4 import BeautifulSoup
from mylog import MyLog as mylog
import re
import random
import time
import codecs
import json
import datetime

Agents1 = [
  "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
  "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
  "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
  "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
  "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
  "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
  "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
  "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
  "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
  "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
  "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
  "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
  "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
  "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
  "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

PROXIES = [
'58.20.238.103:9797',
'123.7.115.141:9797',
'121.12.149.18:2226',
'176.31.96.198:3128',
'61.129.129.72:8080',
'115.238.228.9:8080',
'124.232.148.3:3128',
'124.88.67.19:80',
'60.251.63.159:8080',
'118.180.15.152:8102'
]


class relpy(object):
    Author = None
    Publish_time = None
    title = None
    content = None

class Item(object):
    title = None  # 帖子标题
    firstAuthor = None  # 帖子创建者
    firstPublish_time = None  # 帖子创建时间
    content = None  # 主题内容
    reply = []  # 回复内容



def getResponseContent(url):
    try:
        response = urllib2.urlopen(url.encode('utf8'))
    except:
        print (u'Python 返回URL:%s  数据失败' % url)
    else:
        print (u'Python 返回URL:%s  数据成功' % url)
        return response.read()

def GetPageUrl(url):
    htmlContent_p = getResponseContent(url)
    soup = BeautifulSoup(htmlContent_p, 'lxml')
    pageNumber = soup.find_all('a', attrs={'class': 'last'})
    pageNumber = pageNumber[0].get_text().strip().strip('.')
    pageNumber = 200

    urls = []
    url_array = url.split('-')
    url_constant = "8.7k7k.com/"

    for i in range(27,pageNumber,1):
        url_sub_array = url_array[2].split('.')
        url_sub_array[0] = str(i)
        url_array[2] = url_sub_array[0] + '.' + url_sub_array[1]
        url = url_array[0] + '-' + url_array[1] + '-' + url_array[2]
        htmlContent_p = getResponseContent(url)
        soup = BeautifulSoup(htmlContent_p,'lxml')
        Tag = soup.find_all('a',attrs={'onclick':'atarget(this)','class':'xst'})
        for link in Tag:
            href = link.get('href')
            urls.append(url_constant + href)

    return urls



class Get7k7kInfo(object):
    def __init__(self, url):
        self.url = url
        self.log = mylog()
        self.pageSum = self.getPageNumber(self.url)
        self.urls1 = self.getUrls(self.pageSum)
        self.items = self.spider(self.urls1)
        self.pipelines(self.items)

    def getPageNumber(self, url):
        htmlContent = self.getResponseContent(url)
        soup = BeautifulSoup(htmlContent, 'lxml')
        htmlContent = urllib2.urlopen(url.encode('utf8'))
        soup = BeautifulSoup(htmlContent, 'lxml')

        str = re.compile(u'共 \d+ 页')
        pageNumber_array = soup.find_all('span', attrs={'title': str})
        if (len(pageNumber_array) != 0):
            pageNumber = pageNumber_array[0].get_text().strip()
            pageNumber = int(re.sub("\D", "", pageNumber))
        else:
            pageNumber = 1

        self.log.info(pageNumber)
        return pageNumber

    def getUrls(self, pageSum):
        urls1 = []
        ul = self.url.split('-')
        for pn in range(pageSum):
            ul[2] = pn + 1
            url = ul[0] + '-' + ul[1] + '-' + str(ul[2]) + '-' + ul[3]
            self.log.info(u'解析%s' % url)
            urls1.append(url)
        self.log.info(u'获取URLS成功')
        return urls1

    def timeFormat(self, publish_time):
        text = publish_time.split(' ')[1]
        text_array = text.split('-')
        if(len(text_array) <= 1):
            today = time.strftime('%Y%m%d', time.localtime())
            delta = int(re.sub("\D", "", text_array[0]))
            if u'昨天' in text_array[0]:
                delta = datetime.timedelta(days=1)
            elif u'前天' in text_array[0]:
                delta = datetime.timedelta(days=2)
            else:
                delta = datetime.timedelta(days=delta)
            today = datetime.datetime.strptime(today, '%Y%m%d')
            firstPublish_time = today - delta
            return firstPublish_time.strftime('%Y%m%d')
        else:
            if (int(text_array[1]) < 10):
                text_array[1] = '0' + str(text_array[1])
            if (int(text_array[2] < 10)):
                text_array[2] = '0' + str(text_array[2])

            firstPublish_time = text_array[0] + text_array[1] + text_array[2]
            return firstPublish_time



    def spider(self, urls):
        item = Item()
        del item.reply[:]
        # item.firstAuthor = None
        # item.firstPublish_time = None
        # item.title = None
        # item.content = None
        j = 1
        for url in urls:
            htmlContent = self.getResponseContent(url)
            soup = BeautifulSoup(htmlContent, 'lxml')
            title = soup.find_all('a', attrs={'id': 'thread_subject'})
            if(len(title) == 0):
                return item
            item.title = title[0].get_text().strip()

            authorlist = soup.find_all('a',attrs={'target':'_blank','class':'xi2'})
            others = soup.find_all('a',attrs={'target':'_blank','class':'xi2','sc':'1'})
            authorlist = [ i for i in authorlist if i not in others ]
            contentlist = soup.find_all('td',attrs={'class':'t_f'})
            publish_timelist = soup.find_all('em', attrs={'id':re.compile('authorposton\d+')})

            print "Success!"
            time.sleep(3)

            if(j == 1):
                item.firstAuthor = authorlist[0].get_text().strip()
                item.content = contentlist[0].get_text().strip()
                firstPublish_time_text = publish_timelist[0].get_text()
                item.firstPublish_time = self.timeFormat(firstPublish_time_text)

                for k in range(1,len(contentlist),1):
                    replies = relpy()
                    replies.title = item.title
                    replies.Author = authorlist[2*k].get_text().strip()
                    replies.Publish_time = self.timeFormat(publish_timelist[k].get_text())
                    replies.content = contentlist[k].get_text().strip()
                    item.reply.append(replies)
                j = j + 1
            else:
                for k in range(len(contentlist)):
                    replies = relpy()
                    replies.title = item.title
                    replies.Author = authorlist[2*k].get_text().strip()
                    replies.Publish_time = self.timeFormat(publish_timelist[k].get_text())
                    replies.content = contentlist[k].get_text().strip()
                    item.reply.append(replies)
                j = j + 1

        return item

        #     for tag in tagsli:
        #         item = Item()
        #         item.title = tag.find('a', attrs={'class': 'j_th_tit'}).get_text().strip()
        #         item.firstAuthor = tag.find('span', attrs={'class': 'frs-author-name-wrap'}).a.get_text().strip()
        #         item.firstTime = tag.find('span', attrs={'title': u'创建时间'.encode('utf8')}).get_text().strip()
        #         item.reNum = tag.find('span', attrs={'title': u'回复'.encode('utf8')}).get_text().strip()
        #         item.content = tag.find('div',
        #                                 attrs={'class': 'threadlist_abs threadlist_abs_onlyline '}).get_text().strip()
        #         item.lastAuthor = tag.find('span',
        #                                    attrs={'class': 'tb_icon_author_rely j_replyer'}).a.get_text().strip()
        #         item.lastTime = tag.find('span', attrs={'title': u'最后回复时间'.encode('utf8')}).get_text().strip()
        #         items.append(item)
        #         self.log.info(u'获取标题为<<%s>>的项成功 ...' % item.title)
        # return items

    def pipelines(self, items):
        if(items.content == None):
            return
        GMT_FORMAT = '%d %b %Y %H%M%S GMT'
        today = datetime.datetime.utcnow().strftime(GMT_FORMAT)
        fileName =  today + '.json'
        fileName1 =  today + '.txt'
        with codecs.open(fileName1,'a',encoding='utf8') as fp1:
            line1 = items.firstAuthor + '\n' + u'author' + '\n' + items.content + '\n' + u'content' + '\n' + items.firstPublish_time + '\n' + u'publish_date' + '\n' + items.title + '\n' + u'title' '\n'
            for replys in items.reply:
                line1 = line1 + replys.Author + '\n' + u'author' + '\n' + replys.content + '\n' + u'content' + '\n' + replys.Publish_time + '\n' + u'publish_date' + '\n' + replys.title + '\n' + u'title'
            fp1.write(line1)

        with codecs.open(fileName, 'a', encoding='utf8') as fp:
            line = '{' + '\"post\":' + json.dumps(items.__dict__, ensure_ascii=False) + ',\"replys\":['
            for reply in items.reply:
                line = line + json.dumps(reply.__dict__, ensure_ascii=False)
            line = line + ']}'
            fp.write(line)
        print today + ' Finished'

    def getRandomProxy(self):
        return random.choice(PROXIES)

    def getRandomHeaders(self):
        return random.choice(Agents1)

    def getResponseContent(self, url):
        # fakeHeaders = {'User-Agent': self.getRandomHeaders()}
        # request = urllib2.Request(url.encode('utf8'), headers=fakeHeaders)
        #
        # proxy = urllib2.ProxyHandler({'http': 'http://' + self.getRandomProxy()})
        # opener = urllib2.build_opener(proxy)
        # urllib2.install_opener(opener)
        try:
            response = urllib2.urlopen(url.encode('utf8'))
        except:
            self.log.error(u'Python 返回URL:%s  数据失败' % url)
        else:
            self.log.info(u'Python 返回URL:%s  数据成功' % url)
            return response.read()


if __name__ == '__main__':
    url = 'http://8.7k7k.com/forum-1356-14.html'
    urls = GetPageUrl(url)
    for url in urls:
        try:
            GTI = Get7k7kInfo('http://' + url)
        except:
            continue




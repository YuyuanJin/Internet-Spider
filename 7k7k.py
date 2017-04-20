#!/usr/bin/evn python
# -*- coding: utf-8 -*-
'''
Created on April 10th, 2017

@author: Zonglin DI
'''


# Import the necessary package which will be used in this program
# urllib is for url connection
# BeautifulSoup is for returning the elements
# mylog is a custom class for logging
# re is for regular expression
# codecs is for encoding
# json is for put the elements in order
# datetime is for getting the time to name the file

import urllib2
from bs4 import BeautifulSoup
from mylog import MyLog as mylog
import re
import time
import codecs
import json
import datetime


#The elements we want to classify is a post and n replies, we created two classes seperately

class relpy(object):
    Author = None
    Publish_time = None
    title = None
    content = None

class Item(object):
    title = None  # posting title
    firstAuthor = None  # posting author
    firstPublish_time = None  # posting publishing time
    content = None  # Post content
    reply = []  # A post could have many replies so a list is more proper

# Create a class about get 8.7k7k.com
# When the class is created, call these function

class Get7k7kInfo(object):
    def __init__(self, url):
        self.url = url
        # url we used to resolve

        self.log = mylog()
        # instantiate a mylog class for logging

        self.pageSum = self.getPageNumber(self.url)
        # get how many pages for one post

        self.urls1 = self.getUrls(self.pageSum)
        # get the number of post or replies on one page

        [self.items, self.all_list, self.rubbish_list] = self.spider(self.urls1)
        # The spider function is to get the class which includes one Item, all the words on the page for predict and the rubbish for negative

        self.pipelines(self.items,  self.all_list, self.rubbish_list)
        # To output the item, all the words and rubbish to the .txt for following TensorFlow


    # Function getPageNumber is to get the number of posting pages
    # 1 posting consists of 1 post, M replies and N pages
    # There are 20 repies (post) on 1 page
    # So, the N = ⌈(1+M)/20⌉
    
    def getPageNumber(self, url):
        htmlContent = self.getResponseContent(url)
        soup = BeautifulSoup(htmlContent, 'lxml')
        
        # use regular expression to resolve the page number
        str = re.compile(u'共 \d+ 页')
        pageNumber_array = soup.find_all('span', attrs={'title': str})
        if (len(pageNumber_array) != 0):
            pageNumber = pageNumber_array[0].get_text().strip()
            pageNumber = int(re.sub("\D", "", pageNumber))
        else:
            pageNumber = 1 # If there is no such struct, 1+M <= 20. So there is only 1 page
            
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
    
    # Transfer the time to the format we need
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
        all_list = []
        del all_list[:]
        rubbish_list = []
        del rubbish_list[:]
        j = 1
        for url in urls:
            htmlContent = self.getResponseContent(url)
            soup = BeautifulSoup(htmlContent, 'lxml')
            block_list = soup.find_all('div',attrs={'id':re.compile('post_\d{7}')})

            for block in block_list:
                all_list.append(block.get_text().strip())

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

                rubbish_list.append(all_list[0].strip(item.firstAuthor).strip(item.content).strip(item.firstPublish_time).strip(item.title))

                for k in range(1,len(contentlist),1):
                    replies = relpy()
                    replies.title = item.title
                    replies.Author = authorlist[2*k].get_text().strip()
                    replies.Publish_time = self.timeFormat(publish_timelist[k].get_text())
                    replies.content = contentlist[k].get_text().strip()
                    item.reply.append(replies)

                    rubbish_list.append(all_list[k].strip(replies.title).strip(replies.Author).strip(replies.Publish_time).strip(replies.content))
                j = j + 1
            else:
                for k in range(len(contentlist)):
                    replies = relpy()
                    replies.title = item.title
                    replies.Author = authorlist[2*k].get_text().strip()
                    replies.Publish_time = self.timeFormat(publish_timelist[k].get_text())
                    replies.content = contentlist[k].get_text().strip()
                    item.reply.append(replies)

                    rubbish_list.append(all_list[19 + k].strip(replies.title).strip(replies.Author).strip(replies.Publish_time).strip(replies.content))

                j = j + 1

        return item, all_list, rubbish_list


    def pipelines(self, items, all_list, rubbish_list):
        GMT_FORMAT = '%a%d%b%Y%H%M%SGMT'
        today = datetime.datetime.utcnow().strftime(GMT_FORMAT)
        
        # Ubuntu file path
        fileName = '/home/elegant/Downloads/weather/weather/json/' + today + '.json'
        fileName_validate = '/home/elegant/Downloads/weather/weather/validate/' + today + '_validate.txt'
        fileName_all_list = '/home/elegant/Downloads/weather/weather/all1/' + today + '_all1.txt'
        fileName_rubbish_list = '/home/elegant/Downloads/weather/weather/rubbish1/' + today + '_rubbish1.txt'
        
        # # Windows file path
        # fileName = 'C:/Users/Administrator/PycharmProjects/Spider/json/' + today + '.json'
        # fileName_validate = 'C:/Users/Administrator/PycharmProjects/Spider/_validate/' + today + '_validate.txt'
        # fileName_all_list = 'C:/Users/Administrator/PycharmProjects/Spider/_all1/' + today + '_all1.txt'
        # fileName_rubbish_list = 'C:/Users/Administrator/PycharmProjects/Spider/_rubbish1/' + today + '_rubbish1.txt'
        
        with codecs.open(fileName_validate, 'a', encoding='utf8') as fp1:
            line1 = items.firstAuthor + '\n' + u'author' + '\n'  + items.content + '\n' + u'content' + '\n' + items.firstPublish_time + '\n' + u'publish_date' + '\n' + items.title + '\n'  + u'title' '\n'
            for replys in items.reply:
                line1 = line1 + replys.Author + '\n' + u'author' + '\n' + replys.content + '\n' + u'content' + '\n' + replys.Publish_time + '\n' + u'publish_date' + '\n' +  replys.title + '\n' + u'title'
            fp1.write(line1)

        with codecs.open(fileName_all_list, 'a', encoding='utf8') as fp4:
            line_all = ''
            for all in all_list:
                line_all = line_all + u'TONGJI_UNIVERSITY\n' + all;
            fp4.write(line_all)

        with codecs.open(fileName_rubbish_list,'a',encoding='utf8') as fp5:
            line_rubbish = ''
            for rubbish in rubbish_list:
                line_rubbish = line_rubbish + 'TONGJI_UNIVERSITY\n' +  rubbish
            fp5.write(line_rubbish)

        with codecs.open(fileName, 'a', encoding='utf8') as fp:
            line = '{' + '\"post\":' + json.dumps(items.__dict__, ensure_ascii=False) + ',\"replys\":['
            for reply in items.reply:
                line = line + json.dumps(reply.__dict__, ensure_ascii=False)
            line = line + ']}'
            fp.write(line)

        print today + ' Finished'


    def getResponseContent(self, url):
        try:
            response = urllib2.urlopen(url.encode('utf8'))
        except:
            self.log.error(u'Python 返回URL:%s  数据失败' % url)
        else:
            self.log.info(u'Python 返回URL:%s  数据成功' % url)
            return response.read()


def getResponseContent(url):
    try:
        response = urllib2.urlopen(url.encode('utf8'))
    except:
        print (u'Python 返回URL:%s  数据失败' % url)
    else:
        print (u'Python 返回URL:%s  数据成功' % url)
        return response.read()

# Function GetPageUrl is to resolve for every posting's 1st url
def GetPageUrl(url):
    htmlContent_p = getResponseContent(url)
    soup = BeautifulSoup(htmlContent_p, 'lxml')
    pageNumber = soup.find_all('a', attrs={'class': 'last'})
    pageNumber = pageNumber[0].get_text().strip().strip('.')
    pageNumber = 100

    urls = []
    url_array = url.split('-')
    url_constant = "8.7k7k.com/"

    for i in range(42,pageNumber,1):
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

if __name__ == '__main__':
    url = 'http://8.7k7k.com/forum-1409-1.html'
    urls = GetPageUrl(url)
    for url in urls:
        try:
            GTI = Get7k7kInfo('http://' + url)
        except:
            continue




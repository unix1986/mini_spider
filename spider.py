#!/usr/local/bin/env python
# -*- coding: utf-8 -*-

import Queue
import threading
import urllib
import hashlib
import sys
import os
import time
import re
import color


class Spider(threading.Thread):

    def __init__(self, url_pool, path):
        threading.Thread.__init__(self);
        self._url_pool = url_pool
        self._queue = Queue.Queue()
        self._md5 = hashlib.md5()
        self._counter = 0
        self._path = path

    def run(self):
        while True:
            url, flag = self._queue.get()
            if url == '':
                self._counter += 1
                break
            try:
                self._url = url.strip()
                print "[%s] %s: %s" % (color.y(color.B(self.getName())), color.r(color.B("Get")), self._url)
                self._url_content = urllib.urlopen(self._url).read()
                print "[%s] %s: %s %s" % (color.y(color.B(self.getName())), color.g(color.B("Get")), self._url, color.g(color.B("Done")))
            except:
                # todo logging
                self._counter += 1
                continue

            if flag == 1:    # crawl, save and not push
                self._do_save()
            elif flag == 2:  # crawl, not save and push
                self._do_push()
            elif flag == 3:  # crawl, save and push
                self._do_save()
                self._do_push()
            else:
                # todo logging
                pass
            self._counter += 1

    def add_url(self, url, flag = 2):
        self._queue.put((url, flag))

    def get_url_num(self):
        return self._counter

    def _do_save(self):
        try: 
            url_file = open(self._path + "/" + self._digest_file_name(), 'wb')
            url_file.write(self._url_content)
            url_file.close()
        except:
            # todo logging
            pass

    def _do_push(self):
        # parse self._url
        # self._url_pool.put(todo: parsed url)
        pass

    def _digest_file_name(self):
        self._md5.update(self._url)
        return self._md5.hexdigest()


class UrlQueue(Queue.Queue):
    def __init__(self, maxsize = 0):
        Queue.Queue.__init__(self, maxsize)
        self._cur_level = 0

    def put(self, item, block = True, timeout = None):
        Queue.Queue.put(self, (item, self._cur_level), block, timeout)

    def get(self, block = True, timeout = None):
        item, level = Queue.Queue.get(self, block, timeout)
        return (item, level == self._cur_level)

    def mark_next_level(self):
        self._cur_level += 1


class SpiderManager(object):
    def __init__(self, config):
        self._output_directory = config['output_directory']
        self._max_depth = config['max_depth']
        self._cur_depth = 0
        self._crawl_interval = config['crawl_interval']
        self._crawl_timeout = config['crawl_timeout']
        self._target_url = config['target_url']
        self._thread_count = config['thread_count']
        self._counter = 0
        self._url_queue = UrlQueue()
        self._spiders = []
        for i in range(self._thread_count):
            self._spiders.append(Spider(self._url_queue, self._output_directory)) 
            self._spiders[-1].setName("Spider-%d" % (i + 1))
            self._spiders[-1].start()
        with open(config['url_list_file'], 'r') as file:
            for line in file:
                self._url_queue.put(line[:-1])
            self._url_queue.mark_next_level()
        if not os.path.exists(self._output_directory):
            try:
                os.makedirs(self._output_directory)
            except Exception as err:
                print str(err)
                pass

    def run(self):
        crawl_done = False
        while True:
            while not crawl_done:
                try:
                    url, level_done = self._url_queue.get(True, 3)
                    break
                except:
                    dead_spiders_num = 0
                    for spider in self._spiders:
                        if (not spider.isAlive()):
                            dead_spiders_num += 1
                    if dead_spiders_num == self._thread_count and self._url_queue.empty():
                        crawl_done = True
                    if self._counter == self._all_counter() and self._url_queue.empty():
                        self._kill_all_spiders()
                        crawl_done = True
                    
            if crawl_done:
                break
            if level_done:
                if self._cur_depth == self._max_depth:
                    self._kill_all_spiders()
                    break
                self._cur_depth += 1
                while self._counter != self._all_counter():
                    time.sleep(0.001)
                self._url_queue.mark_next_level()
            flag = self._parse_flag(url)     
            pos = self._counter % self._thread_count 
            spider = self._spiders[pos]
            spider.add_url(url, flag)
            self._counter += 1
        print color.g(color.B("Crawl Done!"))

    def _all_counter(self):
        cnt = 0
        for spider in self._spiders:
            cnt += spider.get_url_num()
        return cnt

    def _parse_flag(self, url):
        if re.match(self._target_url, url):
            flag = 1
        else:
            flag = 2
        return flag
    
    def _kill_all_spiders(self):
        for spider in self._spiders:
            spider.add_url("")
            spider.join()

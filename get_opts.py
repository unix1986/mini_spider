#!/usr/local/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import ConfigParser

MINI_SPIDER_VERSION = '1.0'

def usage():
    print
    print "usage: python mini_spider.py -c <config_file>"
    print "       python mini_spider.py [options]"
    print
    print "-c\tspecify configuration file"
    print "-v\tprint version info"
    print "-h\tprint help info"
    print

def parse_config(config_file):
    try:
        parser = ConfigParser.RawConfigParser()
        parser.read(config_file);
        configs = {}
        configs['url_list_file'] = parser.get('spider', 'url_list_file')
        configs['output_directory'] = parser.get('spider', 'output_directory')
        configs['max_depth'] = parser.getint('spider', 'max_depth')
        configs['crawl_interval'] = parser.getint('spider', 'crawl_interval')
        configs['crawl_timeout'] = parser.getint('spider', 'crawl_timeout')
        configs['target_url'] = parser.get('spider', 'target_url')
        configs['thread_count'] = parser.getint('spider', 'thread_count')
    except ConfigParser.Error as err:
        print str(err)
        sys.exit(3)
    return configs


def parse_opts(params):
    try:
        opts, args = getopt.getopt(params, 'c:vh')
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(1)
    for opt, val in opts:
        if opt == '-c':
            file = val.strip()
            if len(file) == 0 or not os.path.exists(file):
                print "invalid file [%s], empty or not exists" % file
                sys.exit(2)
            return parse_config(file)

        elif opt == '-v':
            print "mini spider by hanlu: version-%s" % MINI_SPIDER_VERSION
            sys.exit(0)
        elif opt == '-h':
            usage()
            sys.exit(0)
        else:
            print 'unhandled option!'
            sys.exit(4)


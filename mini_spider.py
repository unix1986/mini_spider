#!/usr/local/bin/env python
# -*- coding: utf-8 -*-

import sys
import get_opts
import spider

if __name__ == '__main__':
    configs = get_opts.parse_opts(sys.argv[1:])
    manager = spider.SpiderManager(configs)
    manager.run()

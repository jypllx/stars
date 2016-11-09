#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parser.podcastparser import PodcastParser
import json

def parse_json(pp, feed):
  with open(feed) as fd:
    data = json.load(fd)

  for el in data:
    if el['rss'] is not None:
        pp.parse(el['rss'])  

if __name__ == "__main__":

  pp = PodcastParser()

  parse_json(pp, './spiders/france_inter.feeds.json')
  parse_json(pp, './spiders/rmc.feeds.json')
  
  pp.parse('http://feeds.serialpodcast.org/serialpodcast')
  pp.parse('http://arteradio.com/podcast')

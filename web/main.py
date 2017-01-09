#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parser.podcastparser import PodcastParser
import json

def parse_json(pp, feed, source, country):
  with open(feed) as fd:
    data = json.load(fd)

  for el in data:
    if el['rss'] is not None:
        try:
          pp.parse(el['rss'], source, country)
        except:
          pass

if __name__ == "__main__":

  pp = PodcastParser()

  parse_json(pp, './spiders/france_inter.feeds.json', 'France Inter', 'France')
  parse_json(pp, './spiders/rmc.feeds.json', 'RMC', 'France')
  parse_json(pp, './spiders/europe1.feeds.json', 'Europe1', 'France')
  parse_json(pp, './spiders/france_culture.feeds.json', 'France Culture', 'France')
  
  pp.parse('http://feeds.serialpodcast.org/serialpodcast', 'This American Life', 'USA')
  pp.parse('http://arteradio.com/podcast', 'Arte', 'France')

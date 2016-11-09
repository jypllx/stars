#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict
import urllib
import os
from app import db
from models import *

class PodcastParser:

  def parse(self, url):
    """Parses an XML feed and stores it to the db"""

    print('Parsing %s' % url)
    tmp_file = "rss.xml"
    urllib.request.urlretrieve (url, tmp_file)
  
    with open(tmp_file) as fd:
      rss = xmltodict.parse(fd.read())['rss']

    channel = self.getChannel(rss['channel'], url)
    if channel is None:
      channel = self.saveChannel(rss['channel'], url)
      
    print("Channel id : %s %s" % (channel.id, rss['channel']['title']))

    if 'item' not in rss['channel']:
      return
    elif not isinstance(rss['channel']['item'], (list, tuple)):
        rss['channel']['item'] = [rss['channel']['item']]
    for item in rss['channel']['item']:
      if self.existsItem(channel.id, item):
        pass
      else:
        self.saveItem(channel.id, item)

    os.remove(tmp_file)


  def getChannel(self, channel, url):
    ch = Channel.query.filter(Channel.name.like(channel['title']), 
      Channel.url.like(url)).first()
    return ch


  def saveChannel(self, channel, url):
    if 'itunes:category' not in channel and 'category' in channel:
      channel['itunes:category'] = {}
      channel['itunes:category']['@text'] = channel['category']

    if isinstance(channel['itunes:category'], (list, tuple)):
      channel['itunes:category'] = channel['itunes:category'][0]

    ch=Channel(channel['title'],
      channel['description'],
      channel['itunes:category']['@text'],
      channel['language'],
      url,
      channel['link'],
      channel['itunes:image']['@href'])
    db.session.add(ch)
    db.session.commit()
     
    return ch


  def existsItem(self, channel_id, item):
    it = Item.query.filter(Item.channel_id==channel_id, Item.audio_url.like(item['enclosure']['@url'])).first()
    if it is not None:
      return True
    else:
      return False

    
  def saveItem(self, channel_id, item):
    it = Item(item['title'], item['description'], channel_id, item['itunes:duration'], item['enclosure']['@url'], item['pubDate'])
    db.session.add(it)
    db.session.commit()
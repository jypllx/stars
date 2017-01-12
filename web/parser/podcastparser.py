#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict
import urllib
import os
from app import db
from models import *
import traceback

class PodcastParser:

  def parse(self, url, source, country):
    """Parses an XML feed and stores it to the db"""
    try:
      print('Parsing %s' % url)
      tmp_file = "rss.xml"
      urllib.request.urlretrieve (url, tmp_file)

      with open(tmp_file) as fd:
        rss = xmltodict.parse(fd.read())['rss']

      channel = self.getChannel(rss['channel'], url)
      if channel is None:
        channel = self.saveChannel(rss['channel'], url, source, country)
      
      print("Channel id : %s %s" % (channel.id, rss['channel']['title']))

      if 'item' not in rss['channel']:
        return
      elif not isinstance(rss['channel']['item'], (list, tuple)):
          rss['channel']['item'] = [rss['channel']['item']]
      for item in rss['channel']['item']:
        if self.existsItem(channel.id, item):
          pass
        else:
          self.saveItem(channel, item)

      os.remove(tmp_file)
    except Exception as e:
      traceback.print_exc()


  def getChannel(self, channel, url):
    ch = Channel.query.filter(Channel.title_.like(channel['title']), 
      Channel.link_.like(url)).first()
    return ch


  def saveChannel(self, channel, url, source, country):

    if 'itunes:category' not in channel and 'category' in channel:
      itunes_category = channel['category']
    elif 'itunes:category' not in channel:
      itunes_category = None
    elif isinstance(channel['itunes:category'], (list, tuple)):
      channel['itunes:category'][0]
    else:
      itunes_category = channel['itunes:category']['@text']

    mood = Mood.query.filter_by(itunes_category_=itunes_category).first()
    if mood is None:
      mood = Mood(itunes_category)
      db.session.add(mood)
      db.session.commit()

    last_build_date = channel['lastBuildDate'] if 'lastBuildDate' in channel.keys() else None

    ch=Channel(channel['title'],
      url,
      None if 'description' not in channel else channel['description'],
      itunes_category,
      mood.mood,
      channel['language'],
      channel['itunes:author'],
      channel['itunes:image']['@href'],
      last_build_date,
      source,
      country)
    db.session.add(ch)
    db.session.commit()
     
    return ch


  def existsItem(self, channel_id, item):
    it = Item.query.filter(Item.channel_id==channel_id, Item.audio_url_.like(item['enclosure']['@url'])).first()
    if it is not None:
      return True
    else:
      return False

    
  def saveItem(self, channel, item):
    it = Item(item['title'], 
      None if 'description' not in item else item['description'],
      channel.id, 
      None if 'itunes:duration' not in item else item['itunes:duration'],
      item['enclosure']['@url'], 
      item['pubDate'], 
      channel.itunes_category_,
      channel.mood,
      channel.source,
      channel.country,
      channel.image)
    db.session.add(it)
    db.session.commit()
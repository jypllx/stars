#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict
import urllib
import os
from app import db
from models import *
import traceback
import json
import dateparser
from datetime import datetime

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
    db.session.commit

  def parse_college(self, feed):
    with open(feed) as fd:
      data = json.load(fd)

    print('Chargé')

    channel = Channel.query.filter_by(title_='Collège de France').first()
    print(channel)
    if not channel:
      channel = Channel('Collège de France', 
          'College-de-france.fr', 
          'Le Collège de France est un établissement public d’enseignement supérieur, institution unique en France, sans équivalent à l’étranger. Depuis le XVIe siècle, le Collège de France répond à une double vocation : être à la fois le lieu de la recherche la plus audacieuse et celui de son enseignement. Voué à la recherche fondamentale, le Collège de France possède cette caractéristique singulière : il enseigne « le savoir en train de se constituer dans tous les domaines des lettres, des sciences ou des arts », en partenariat avec le CNRS, l’INSERM et plusieurs autres grandes institutions.', 
          None,
          None,
          'fr',
          'Collège de France',
          'https://www.college-de-france.fr/images/subject/institution-cover.jpg',
          '2017-01-18', 
          'Collège de France',
          'France')
      db.session.add(channel)
      db.session.commit()
      print('Ajouté channel')

    for el in data:
      item = Item.query.filter_by(audio_url_=el['audio_url_']).filter_by(channel_id=channel.id).first()
      if not item:
        pubdate_ = datetime.now()
        if el['day'] and el['hour']:
          pubdate_ = dateparser.parse(el['day']+ ' '+el['hour'])
        elif el['day']:
          pubdate_ = dateparser.parse(el['day'])

        item = Item(el['title_'], None, channel.id, 
        None, el['audio_url_'], pubdate_, None, None, 
        'Collège de France', 'France', el['image'])
        db.session.add(item)
        db.session.commit()
        print('Ajouté item '+el['title_'])
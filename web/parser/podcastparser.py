#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict
import urllib
import psycopg2
import os

class PodcastParser:
 
  def __init__(self, config):

    self.conn = psycopg2.connect("host=%s dbname=%s user=%s port=%s" % (
      config.DB_SERVICE, config.DB_NAME, config.DB_USER, config.DB_PORT))

  def __del__(self):
    self.conn.close()

  def parse(self, url):
    """Parses an XML feed and stores it to the db"""

    print('Parsing %s' % url)
    tmp_file = "rss.xml"
    urllib.request.urlretrieve (url, tmp_file)
  
    with open(tmp_file) as fd:
      rss = xmltodict.parse(fd.read())['rss']

    channel_id = self.getChannel(rss['channel'], url)
    if channel_id == None:
      channel_id = self.saveChannel(rss['channel'], url)
      
    print("Channel id : %s %s" % (channel_id, rss['channel']['title']))

    if 'item' not in rss['channel']:
      return
    elif not isinstance(rss['channel']['item'], (list, tuple)):
        rss['channel']['item'] = [rss['channel']['item']]
    for item in rss['channel']['item']:
      if self.existsItem(channel_id, item):
        pass
      else:
        self.saveItem(channel_id, item)

    os.remove(tmp_file)

  def getChannel(self, channel, url):
    cur = self.conn.cursor()
    cur.execute("SELECT id FROM channels WHERE name = %s AND url = %s;", (channel['title'], url))
    res = cur.fetchall()
    self.conn.commit()
    cur.close
    if (len(res) > 1):
      print('More than one podcast for %s, %s' % (channel['title'], url))
      raise Exception('Merde!!')
    elif (len(res) == 1):
      return res[0][0]
    else:
      return None

  def saveChannel(self, channel, url):
    cur = self.conn.cursor()
    sql = "INSERT INTO channels (url, name, genre, language, link, description, img_url) VALUES (%s, %s, %s, %s, %s, %s, %s);"

    if 'itunes:category' not in channel and 'category' in channel:
      channel['itunes:category'] = {}
      channel['itunes:category']['@text'] = channel['category']

    if isinstance(channel['itunes:category'], (list, tuple)):
      channel['itunes:category'] = channel['itunes:category'][0]

    cur.execute(sql, (url, 
      channel['title'], 
      channel['itunes:category']['@text'], 
      channel['language'], 
      channel['link'],
      channel['description'],
      channel['itunes:image']['@href']))
    self.conn.commit()
    cur.execute("SELECT id FROM channels WHERE name = %s AND url = %s;", (channel['title'], url))
    res = cur.fetchall()
     
    channel_id = res[0][0]
    cur.close()
    return channel_id

  def existsItem(self, channel_id, item):
    cur = self.conn.cursor()
    query = "SELECT id FROM items WHERE channel_id=%s AND audio_url=%s"
    cur.execute(query, (channel_id, item['enclosure']['@url']))
    res = cur.fetchall()
    self.conn.commit()
    cur.close
    if (len(res) > 1):
      print('More than one podcast for %s, %s' % (channel_id, item.title))
      raise Exception('Merde!!')
    elif (len(res) == 1):
      return True
    else:
      return False
    
  def saveItem(self, channel_id, item):
    cur = self.conn.cursor()
    sql="INSERT INTO items (channel_id, name, description, duration, audio_url, published) VALUES (%s, %s, %s, %s, %s, %s);"
    cur.execute(sql, (channel_id, 
                      item['title'], 
                      item['description'],
                      item['itunes:duration'], 
                      item['enclosure']['@url'],
                      item['pubDate']))
    self.conn.commit()
    cur.close()

if __name__ == "__main__":
  p = PodcastParser('spaces', 'spaces')
  # p.parse('http://feeds.serialpodcast.org/serialpodcast')
  p.parse('http://radiofrance-podcast.net/podcast09/rss_11739.xml')
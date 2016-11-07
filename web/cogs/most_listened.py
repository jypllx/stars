#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2

if __name__ == "__main__":
    conn = psycopg2.connect("dbname=spaces user=spaces")
    cur = conn.cursor()

    cur.execute("SELECT plays.item_id, count(*) AS nb FROM plays ON items.id=plays.item_id GROUP BY plays.item_id ORDER BY nb DESC;")
    res = cur.fetchall()
    
    cur.execute("SELECT")
    cur.close()    
    conn.close()
    print(str(res))
# -*- coding: utf_8 -*-

from bs4 import BeautifulSoup
from urllib2 import urlopen
import sqlite3
import os
import time

siteurl = 'http://www.bundesverfassungsgericht.de'
baseurl = 'http://www.bundesverfassungsgericht.de/entscheidungen/'
years = range(1998,2014)
months = range(1,13)

dbfilename = "bverfg.db"

error_log = []

# falls Datenbank schon existiert, löschen
if dbfilename in os.listdir("."):
    os.remove(dbfilename)

# mit Datenbank verbinden und Tabelle anlegen, falls es sie noch nicht gibt
conn = sqlite3.connect(dbfilename)
cursor = conn.cursor()
# war
# cursor.execute("""CREATE TABLE IF NOT EXISTS decisions
# aber hier soll die bestehende Tabelle ja überschrieben werden 
cursor.execute("""CREATE TABLE decisions
                  (year int, month int, filename text, url text, html text)
               """)


rownumber = 1
# Seiten scrapen und in Datenbank speichern 
for year in years:
    for month in months:
        url = baseurl + str(year) + "/" + str(month)
        try:
            monthpage = urlopen(url)
        except Exception as e:
            error_log.append(e)
            print e
            continue
        monthsoup = BeautifulSoup(monthpage)
        links = monthsoup.find_all('a')
        for link in links:
            if ('/entscheidungen/' in link['href']) and ('.html' in link['href']):
                decision_url = siteurl + link['href']
                decisionpage = urlopen(decision_url)
                html = decisionpage.read().decode('iso-8859-1')
                filename = link['href'].split('/')[-1]
                # Datenbank um neuen Eintrag ergänzen
                cursor.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (year, month, filename, decision_url, html))
                conn.commit()
                print str(rownumber) + ": " + link['href']
                time.sleep(0.5)
                rownumber += 1
                #if rownumber == 11: # Begrenzung zum Testen
                    #raise SystemExit(0)
if error_log:
    for error in error_log:
        print error
print "Fertig!"
# -*- coding: utf_8 -*-

from bs4 import BeautifulSoup, Comment
import sqlite3
import re
#import html5lib

"""
* einstimmigkeit bei entscheidungen
* GG-artikel, auf die bezug genommen wird
* dauer zwischen dem "angefochtenen" urteil und der entscheidung des bverfg
* länge der begründung
* die entscheidung selbst
* angemahnte gesetzesänderungen
* welcher senat fällt mehr urteile?
* Welche Personen, Schriften, Urteile werden zitiert?


to do:
* englische komplett rausschmeißen
* RegEx: auch Art. 53a, 115l etc. berücksichtigen

"""

article_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "12a", "13", "14", "15", "16", "16a", "17", "17a", "18", "19", "20", "20a", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "45a", "45b", "45c", "45d", "46", "47", "48", "49", "50", "51", "52", "53", "53a", "54", "55", "56", "57", "58", "59", "59a", "60", "61", "62", "63", "64", "65", "65a", "66", "67", "68", "69", "70", "71", "72", "73", "74", "74a", "75", "76", "77", "78", "79", "80", "80a", "81", "82", "83", "84", "85", "86", "87", "87a", "87b", "87c", "87d", "87e", "87f", "88", "89", "90", "91", "91a", "91b", "91c", "91d", "91e", "92", "93", "94", "95", "96", "97", "98", "99", "100", "101", "102", "103", "104", "104a", "104b", "105", "106", "106a", "106b", "107", "108", "109", "109a", "110", "111", "112", "113", "114", "115", "115a", "115b", "115c", "115d", "115e", "115f", "115g", "115h", "115i", "115k", "115l", "116", "117", "118", "118a", "119", "120", "120a", "121", "122", "123", "124", "125", "125a", "125b", "125c", "126", "127", "128", "129", "130", "131", "132", "133", "134", "135", "135a", "136", "137", "138", "139", "140", "141", "142", "142a", "143", "143a", "143b", "143c", "143d", "144", "145", "146"]
decision_list = {}
decisions_with_articles = {}

row_num = 0
err_count = 0
err_log = []

article_mentions = []

conn = sqlite3.connect("bverfg.db")
cursor = conn.cursor()

fh = open("bverfg.csv", "w")

def get_date(DecisionSoup):
    "Datum in Zitierung suchen"
    global err_log
    global err_count
    # Angaben zur Zitierung im Seitenkopf 
    try:
        zitierung = DecisionSoup.find("p", "zitierung").contents[0].rstrip(", ").lstrip("Zitierung: ")
    except Exception as e:
        err_log.append(e)
        print e
        err_count += 1
        return

    try:
        decision_match = re.search('vom (.*), ', zitierung)
    except Exception as e:
        err_log.append(e)
        print e
        return

    if decision_match:
        return decision_match.group(1)
    else:
        err_log.append("Kein Datum in Zitierung: %s" % row[2])    
        return

def get_rationale(DecisionSoup):        
    decision_text = []
    inside_decision = False
    plain_divs = DecisionSoup.find("div", id="text").find_all("div", "links") # nur Text, keine Absatznummerierungen (class="rechts")
    for div in plain_divs:
        for text in div.strings:
            text = re.sub('[\t\r\n]', '', text) # weg mit newlines etc.
            if text: # weg mit leeren Zeilen
                #print text
                if not inside_decision: # nur checken wenn False
                    inside_decision = text == "Gründe:"
                if inside_decision:
                    decision_text.append(text)
    return ' '.join(decision_text)


def get_articles(rationale):
    art_pattern = re.compile('Art\..([0-9]+[a-z]?)') # \s umfasst Leerzeichen und nicht-umbrechende Leerzeichen
    art_found = art_pattern.findall(rationale)
    if art_found:
        return set(art_found) # mehrfache Nennungen eliminieren

        

test_run = 0
for row in cursor.execute("SELECT * FROM decisions"):
    # debug:
    #test_run += 1
    #if test_run > 100: break

    decision_length = 0
    
    html = row[4]
    
    print("--- %s ---" % row[2])
    
    # Pythons interner Parser scheint überfordert mit
    # http://www.bundesverfassungsgericht.de/entscheidungen/ls19981124_2bvl002691.html 
    try:
        DecisionSoup = BeautifulSoup(html, "html.parser")
    except:
        try:
            DecisionSoup = BeautifulSoup(html, "html5lib") # Fallback, viel langsamer
        except Exception as e:
            err_log.append(e)
            print "Auch html5lib scheitert am Parsen!"
            print e
            continue
    
    # Magie, um die Kommentare in DecisionSoup (!) zu entfernen
    comments = DecisionSoup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

    decision_date = get_date(DecisionSoup)
    decision_list.update({row[2]:decision_date})
    
    
    # reinen Text der Begründung heraussieben
    rationale = get_rationale(DecisionSoup)
    rationale_length = len(rationale)
    if rationale: # nicht immer werden Gründe angegeben
        
        # Datum und erwähnte GG-Artikel in article_mentions sammeln
        gg_articles = get_articles(rationale)
        if gg_articles:
            decisions_with_articles.update({row[2]:gg_articles})
            print row[2] + " " + str(gg_articles) # debug

        
        # CSV-Datei mit Datum und Begründungslänge
        fh.write('"%s";"%s"\n' % (decision_date, str(rationale_length)))
    #fh.flush()
    row_num += 1
    print('%s. %s: %s' % (row_num, decision_date, rationale_length))
  
fh.close()


# Daten und GG-Artikel in CSV-Datei speichern
fh = open("bverfg_gg_art.csv", "w")
# Spaltennamen in oberste Zeile
fh.write('"URL";"Datum')
for article_name in article_names:
    fh.write('";"Art. %s' % article_name)
fh.write('"\n')
# alle weiteren Zeilen schreiben
for decision_url in decision_list:
    # URL und Datum schreiben
    fh.write('"%s";"%s' % (decision_url, decision_list[decision_url])) # URL und Datum
    for article_name in article_names:
        if decision_url in decisions_with_articles:
            if article_name in decisions_with_articles[decision_url]:
                fh.write('";"1')
            else:
                fh.write('";"0')
        else:
            fh.write('";"0')
    fh.write('"\n')    
fh.close()

# Fehler ausgeben
print "==== FEHLER ===="
if err_log:
    x = 0
    for error in err_log:
        x += 1
        print("%i. %s" % (x, error))
print("Fehlende Zitierungsangaben: %s" % (err_count))    
print "\nFertig!"

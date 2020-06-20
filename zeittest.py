import random
import csv
import datetime as uhr
from time import sleep
i = 0
messwerte = [['Datum', 'Uhrzeit', 'Spannung', 'Strom', 'Leistung']]

def simuMess():
    #messwerte = [['Spannung', 'Strom', 'Leistung']]
    for i in range(0,50):
        jetzt = uhr.datetime.now()
        datum = jetzt.strftime("%d.%m.%Y")
        zeit = jetzt.strftime("%H:%M:%S")
        text1 = random.randrange(16)
        text2 = random.randrange(6)
        text3 = random.randrange(11)
        print('{} @ {}: {}V;{}A;{}W'.format(datum, zeit, text1, text2, text3))
        messwerte.append([datum, zeit, text1, text2, text3])
        sleep(1)
    # print(type(messwerte))
    # print(messwerte)
    
def csv_schreiben(filename, werte):
    with open('{}.csv'.format(filename), 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(werte)
  

simuMess()
csv_schreiben('zeitlog', messwerte)
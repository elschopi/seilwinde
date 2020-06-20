import random
import csv
i = 0
messwerte = [['Spannung', 'Strom', 'Leistung']]

def simuMess():
    #messwerte = [['Spannung', 'Strom', 'Leistung']]
    for i in range(0,50):
        text1 = random.randrange(16)
        text2 = random.randrange(6)
        text3 = random.randrange(11)
        # print('{};{};{}'.format(text1, text2, text3))
        messwerte.append([text1, text2, text3])
    # print(type(messwerte))
    # print(messwerte)
    
def csv_schreiben(werte):
    with open('foobarfile.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(werte)
  

simuMess()
csv_schreiben(messwerte)
# folgender Code nur rauskopiert und somit bereits vorhanden

import brickpi3 # benötigt für Kommunikation mit Brick Pi / importiert BrickPi3-Methoden
import sys # für sys.exit()
import time # für time.sleep

BP = brickpi3.BrickPi3() # es wird eine Instanz der BrickPi3-Klasse erzeugt # BP wird als BrickPi-Objekt festgelegt

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 1
BP.set_sensor_type(BP.PORT_2, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 2


# diese doIfHigh-Funktion nur für Start über input-Befehl "Start" erstellt - wird dann durch Taster ersetzt
# Funktionsansatz für Taster siehe adstest_.py
def doIfHigh():
    start = input("Bitte Geben Sie den Begriff - START - ein :")
    
    if start in ["START", "start", "Start"]:
        value = 1
        return value
    else:
        print("Wiederholen Sie die Eingabe: ")
        return doIfHigh()    

#gibt value von unterem Sensor (zum Starten bisher nur verwendet) wieder - value mit 1/0 kann eigentlich rausfallen - nur
#True/False wichtig
def set_sensor_unten():
    value = 0
    if BP.get_sensor(BP.PORT_2):
        if value == 0:
            return True
        else:
            return False
    # über erster if-Ebene eventuell noch try und anschließende except - welchenError siehe rest.py

def set_sensor_oben():
    value = 0
    if BP.get_sensor(BP.PORT_1):
        if value == 0:
            return True
        else:
            return False
    #über erster if-Ebene eventuell noch try und anschließende except - welchenError siehe rest.py

def set_stop_unten():                         # für signalempfang am schluss- syntax ist aber identisch zu
    if BP.get_sensor(BP.PORT_2):              # set_sensor_unten() - daher diese Funktion eigentlich übrig und aus code unten zu entfernen!                                      
        return True
    else:
        return False


def move(value, starter):#als zweites argument wird hier dann noch der GPIO-channel für Funktion doIfHigh hinzugefügt werden!!
    
    start_unten = set_sensor_unten()
    print(start_unten)
    
    if start_unten and starter:
        print("Start unten")
        BP.set_motor_power(BP.PORT_A, value)
    
    while True:
        umkehr_oben = set_sensor_oben()                     #hier wird nun ständig oberer Sensor abgefragt - nicht sehr 
        if umkehr_oben and starter:                         #ellegant - es gibt aber keine detect event funktion in brickpi
            BP.set_motor_power(BP.PORT_A, (value * -1))     #umkehren an sich funktioniert aber
      
        stop_unten = set_stop_unten()  
        if umkehr_oben and stop_unten and starter:
            BP.set_motor_power(BP.PORT_A, 0)          #dies funktioniert noch nicht zuverlässig - nochmals prüfen wieso!!
        
        # Code Messung hier einfügen
        
        time.sleep(0.1)
        
#main-Schleife für Legoprogramm:
begin = doIfHigh()
move(100, begin)    

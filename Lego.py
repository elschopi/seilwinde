# Imports
import brickpi3 # benötigt für Kommunikation mit Brick Pi / importiert BrickPi3-Methoden
import time # für time.sleep
import RPi.GPIO as GPIO


# Objektdeklarierung
BP = brickpi3.BrickPi3() # es wird eine Instanz der BrickPi3-Klasse erzeugt # BP wird als BrickPi-Objekt festgelegt
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 1
BP.set_sensor_type(BP.PORT_2, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 2

taster = 18 # Pin Nummer des zu verwendenden GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(taster, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO konfigurieren


#Funktionsdefinitionen

def doIfHigh1(): # diese doIfHigh-Funktion nur für Start über input-Befehl "Start" erstellt - wird dann durch Taster ersetzt
    start = input("Bitte Geben Sie den Begriff - START - ein :")
    if start in ["START", "start", "Start"]:
        value = 1
        return value
    else:
        print("Wiederholen Sie die Eingabe: ")
        return doIfHigh1()    
    
def doIfHigh2(): # tatsächliche doIfHigh-Funktion für Tasterabfrage
    
    #hier könnte noch try & except eingefügt werden - nur wie und welchen Fahler auffangen?
    
    status = 0 # Setze ein 'status' flag als Zustandsspeicher für den Taster
    
    global taster
    buttonState = GPIO.input(taster) # Abfrage des GPIO Status
    #print(buttonState)
  
    # Wenn der Status 0 ist, ist der Taster gedrückt worden (das liegt daran, dass der GPIO mit Pullup auf 3.3V gezogen wird 
    # und gegen GND schaltet)
    if buttonState == 0:
      time.sleep(0.5)
      # Diese Zeilen toggeln den Zustand. 
      if status==0:
        status=1
      else:
        status=0
        # Hier wird bestimmt, was gemacht werden soll (Programmaufruf, LED ein/aus, usw)
    if status==1:
        return 1
    else:
        print("Wiederholen Sie die Eingabe: ")
        return doIfHigh2()
        
def set_sensor_unten(): #gibt value von unterem Sensor wieder 
    try:
        value = 0
        if BP.get_sensor(BP.PORT_2):
            if value == 0:
                return True
            else:
                return False
    except:
        print("Fehler Signal Sensor unten. Bitte prüfen!")
        BP.reset_all()        

def set_sensor_oben():
    try:
        value = 0
        if BP.get_sensor(BP.PORT_1):
            if value == 0:
                return True
            else:
                return False
    except:
        print("Fehler Signal Sensor oben. Bitte prüfen!")
        BP.reset_all()  

def stop_unten():
    try:
        if BP.get_sensor(BP.PORT_2):                                                
            return True
        else:
            return False
    except:
        print("Fehler Signal Stop. Bitte prüfen!")
        BP.reset_all() 
        
def move(value, starter):#als zweites argument wird hier dann noch der GPIO-channel für Funktion doIfHigh hinzugefügt werden!!
    try:
        while True:
            if set_sensor_oben() and starter:                         
                BP.set_motor_power(BP.PORT_A, (value * -1))
            else:
                BP.set_motor_power(BP.PORT_A, 0)                      # PRÜFEN OB DIES SO MACHBAR

            if set_sensor_oben() and stop_unten() and starter:
                BP.set_motor_power(BP.PORT_A, 0)
            else:
                BP.reset_all()                                         # PRÜFEN OB DIES SO MACHBAR

            # Code Messung hier einfügen

            time.sleep(0.1)
    except:
        print("Fehler im Bewegungsablauf. Bitte prüfen!")
        BP.reset_all()

#Funktionsaufruf / main-Schleife für Legoprogramm:
while True:
    begin = doIfHigh1()  #wenn Taster entsprechend integriert, durch doIfHigh2() ersetzen
    
    value = 100
    if set_sensor_unten() and begin:
        print("Start unten")
        BP.set_motor_power(BP.PORT_A, value)
    move(value, begin) 

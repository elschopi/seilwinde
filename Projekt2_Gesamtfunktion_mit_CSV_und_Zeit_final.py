# Imports
import brickpi3 # benötigt für Kommunikation mit Brick Pi / importiert BrickPi3-Methoden
import time # für time.sleep
import RPi.GPIO as GPIO #für die GPIO des Raspberry
from lib_oled96 import ssd1306 # Bibliothek für das Display
from smbus import SMBus # Bibliothek für I2C Kommunikation
from ADS1x15 import ADS1115 # Bibliothek für AD-Wandler
import csv #wird benötigt für die Logdatei
import datetime as uhr # Zur Zeitmessung
import plotter # kleines Modul zur Ausgabe der Messung als Graph - benötigt matplotlib



# Objektdeklarierung
BP = brickpi3.BrickPi3() # es wird eine Instanz der BrickPi3-Klasse erzeugt # BP wird als BrickPi-Objekt festgelegt
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 1
BP.set_sensor_type(BP.PORT_2, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 2

i2cbus = SMBus(1) # I2C Bus 1 am Raspberry Pi an Pins 2 & 3         
oled = ssd1306(i2cbus) # OLED Objekt erstellen
adc1 = ADS1115(address=0x48, busnum=1) # den AD-Wandler auf dem I2C Bus mit der angegebenen Addresse initialisieren

GAIN = 1 # Gain vom ADS einstellen. Mögliche Werte siehe Library
# Für Hauptplatine
main_faktor = 0.188 # Auflösung des ACS712 einstellen. Grundwert nach Datenblatt ist 0.185V/A. Durch Messung mit Last ermittelt.
main_r1 = 47148 # Widerstand R1 für den Spannungsteiler Eingangsspannung. Nominal 12V auf 3.3V
main_r2 = 18152 # Widerstand R2 für den Spannungsteiler Eingangsspannung. Nominal 12V auf 3.3V

# Initialisiere den Header für die Logdatei
messwerte =[]
messwerte = [['Datum','Uhrzeit','Spannung (V)', 'Strom (A)', 'Leistung (P)']]
# Funktionsdefinitionen
# Schreibt die Werte in die Logdatei
def csv_schreiben(werte):
    with open('messwerte_reihe3_22072020.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(werte)

# Mit der Funktion wird die Leistungsmessung durchgeführt
def Messung(adcnr):
    if adcnr == adc1: # Es besteht die Möglicheit, eine weitere Messplatine zu verwenden (nicht genutzt)
        ad1_spannung = ((float(ACS_EingangsMessung_raw(adc1)[0])*4.096)/32768.0)/((float(main_r2)/(float(main_r1) + float(main_r2)))) # aus dem "rohen" Messwert des AD-Wandlers die Eingangsspannung rückrechnen
        ad1_strom = ((float(ACS_EingangsMessung_raw(adc1)[1])*4.096)/32768.0)/float(main_faktor) # aus dem "rohen" Messwert des AD-Wandlers den Strom berechnen
        ad1_strom = ad1_strom * (-1) # leider nötig, da der Stromwert negativ ist. Ist im Prinzip eine rein optische Sache
        power = ad1_spannung * ad1_strom # Da die Leistung nicht direkt abgefragt wird, wird sie berechnet
        # Uhrzeit und Datum für die Logdatei
        jetzt = uhr.datetime.now() 
        datum = jetzt.strftime("%d.%m.%Y")
        zeit = jetzt.strftime("%H:%M:%S")
        # Messwerte auf dem Diplay ausgeben -  zeilenweise in den Displaybuffer laden
        Anzeige('ADC1: {:.2f}V'.format(ad1_spannung), 0) 
        Anzeige('ADC1: {:.2f}A'.format(ad1_strom), 10)
        Anzeige('ADC1: {:.2f}W'.format(power), 20)
        oled.display() # Displaybuffer auf dem Display ausgeben
        messwerte.append([datum, zeit, ad1_spannung, ad1_strom, power]) # Messwerte an die Logdatei anhängen
        # print('U: {:.2f}V, I: {:.2f}A'.format(ad1_spannung, ad1_strom))
        return ad1_spannung, ad1_strom
    elif adcnr == adc2: # nicht verwendet
        ad2_spannung = ((float(ACS_EingangsMessung_raw(adc2)[0])*4.096)/32768.0)/((float(exp1_r2)/(float(exp1_r1) + float(exp1_r2))))
        ad2_strom = ((float(ACS_EingangsMessung_raw(adc2)[1])*4.096)/32768.0)/float(exp1_faktor)
        power = ad2_spannung * ad2_strom
        return ad2_spannung, ad2_strom, power

taster = 23 # Pin Nummer des zu verwendenden GPIO für den Start-Taster
GPIO.setmode(GPIO.BCM) # Nummerierungsschema BCM verwenden
GPIO.setup(taster, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO konfigurieren

# Bereitschaftsmeldung bei Programmstart auf dem Display
oled.canvas.text((15,10), 'Warte', fill=1)
oled.canvas.text((15,20), 'auf', fill=1)
oled.canvas.text((15,30), 'Start...', fill=1)
oled.display()

# kleine Helferfunktion für die Displayausgabe
def Anzeige(text, zeilenr): 
    oled.canvas.text((5,zeilenr), text, fill=1)

# Rohdaten vom AD-Wandler abfragen (Digits)
def ACS_EingangsMessung_raw(adcnr):
    if adcnr == adc1: # Es besteht die Möglicheit, eine weitere Messplatine zu verwenden (nicht genutzt)
        #print('ADC1:')
        ad1_spannung_raw = adcnr.read_adc(2,gain=GAIN, data_rate=128) # read_adc(ADC-Kanal, Gain, Abtastrate) fragt "normalen" AD Eingang ab
        ad1_strom_raw = adcnr.read_adc_difference(0, gain=GAIN, data_rate=None) # differentieller Kanal 0 ist AIN 0 + AIN1
        # volt = (float(raw)*4.096)/32768.0
        # volt_diff = (float(raw_diff)*4.096)/32768.0
        return ad1_spannung_raw, ad1_strom_raw
    elif adcnr == adc2:
        #print('ADC2:')
        ad2_spannung_raw = adcnr.read_adc(2,gain=GAIN, data_rate=128)
        ad2_strom_raw = adcnr.read_adc_difference(0, gain=GAIN, data_rate=None)
        return ad2_spannung_raw, ad2_strom_raw

# Simulation von Start-Taster
def doIfHigh1(): # diese doIfHigh-Funktion nur für Start über input-Befehl "Start" erstellt - wird dann durch Taster ersetzt
    start = input("Bitte Geben Sie den Begriff - START - ein :")
    if start in ["START", "start", "Start"]:
        value = 1
        return value
    else:
        print("Wiederholen Sie die Eingabe: ")
        return doIfHigh1()    

# in dieser Funktion soll der Start-Taster abgefragt werden. Drücken des Tasters toggelt den Zustand und ermöglicht das Losfahren
def doIfHigh2(): # tatsächliche doIfHigh-Funktion für Tasterabfrage
    
    status = 0 # Setze ein 'status' flag als Zustandsspeicher für den Taster (bei Aufruf der Funktion auf 0 setzen -> definierter Startzustand)
    while True: 
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
            print('Start über Taster erkannt..')
            return 1
        
def set_sensor_unten(): #gibt Value von unterem Sensor wieder 
    #try:
        value = False
        sensor = 0
        if BP.get_sensor(BP.PORT_2):
            if value == False:
                print('Signal unten erkannt...')
                return True
            else:
                time.sleep(0.1)
                return False

# gibt den Wert des oberen Sensors wieder
def set_sensor_oben():
    #try:
        obenvalue = False
        if BP.get_sensor(BP.PORT_1):
            if obenvalue == False:
                global oben_time # globale Variable, um in anderen Funktionen damit arbeiten zu können
                oben_time = uhr.datetime.now() # speichere den zeitpunkt, an dem der obere Anschlag erkannt worden ist
                diff = oben_time - begin_time # benötigte Zeit für den Weg nach oben berechnen
                print('Benötigte Zeit nach oben: {:.4f}s'.format(diff))
                print("Oben erkannt, drehe um...")
                return True
            else:
                return False


# gibt den Wert des unteren Sensors wieder
def stop_unten():
    try:
        value = False
        if BP.get_sensor(BP.PORT_2):
            if value == False:
                value = True
                print("Stop unten aktiviert")
                return value
    except:
        print("Fehler Signal Stop. Bitte prüfen!")
        #BP.reset_all() 

# Bewegungssteuerung, steuert die Umkehr und das Abschalten des Motors
def move(value, starter):
    #try:
        status = False # Status
        stat = True # Hilfsstatusflag, um die Abfrageschleife bei Erreichen des unteren Anschlags sauber zu verlassen
        while stat: # 
            oled.cls() # lösche den Displayinhalt
            Messung(adc1) # Messung von AD-Wandler 1
            # Der Wagen ist oben angekommen und muss nun umkehren
            if set_sensor_oben() and starter:                         
                BP.set_motor_power(BP.PORT_A, (value * -1))
                if status == False:
                    status = True
            # nachdem der Wagen oben angekommen ist: Motor abschalten, wenn der Wagen wieder unten ankommt
            if status and stop_unten() and starter:
                BP.set_motor_power(BP.PORT_A, 0) # Motor abschalten
                time.sleep(0.5)
                global end_time # globale Variable, um in anderen Funktionen damit arbeiten zu können 
                end_time = uhr.datetime.now() # Zeitpunkt des Programmendes speichern
                # alle Messwerte in die csv Datei schreiben. Werden aber ein paar viele werden.
                # eventuell muss mit der Position des Aufrufs noch gespielt werden, also wann das aufgerufen wird
                #
                difftime = end_time - begin_time # benötigte Zeit für die gesamte Wegstrecke
                print('Wagen wieder unten angekommen. Schalte Motor aus.')
                print('Benötigte Zeit für Gesamtstrecke: {:.4f}s'.format(difftime))
                csv_schreiben(messwerte) # Logdatei schreiben
                #BP.reset_all()                                         
                # aus der schleife raus
                stat = False # damit wird die Schleife beendet
                # Starte den Plotter mit der angegebenen Messreihe
                plotter.plot_graph('messwerte_reihe3_bat_22072020.csv')
            time.sleep(0.05)
    #except:
        #print("Fehler im Bewegungsablauf. Bitte prüfen!")              
        #BP.reset_all()

# Funktionsaufruf
try:
    while True:
        print('Warte auf Start-Taster...')
        begin = doIfHigh2()  # schaltet das Programm auf "Bereitschaft" -> Warten auf drücken des Start Knopfes
        # Motordrehzahl = 100
        value = 100
        
        # Nur starten, wenn der Wagen am unteren Anschlag liegt
        if set_sensor_unten() and begin:
            print("Startbedingung erfüllt, starte Motor...")
            global begin_time # globale Variable, um in anderen Funktionen damit arbeiten zu können 
            begin_time = uhr.datetime.now() # Startzeitpunkt speichern
            BP.set_motor_power(BP.PORT_A, value) # Motor auf Port A mit der gewünschten Drehzahl starten
        move(value, begin)
        
except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.

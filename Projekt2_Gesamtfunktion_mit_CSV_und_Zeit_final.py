# Imports
import brickpi3 # benötigt für Kommunikation mit Brick Pi / importiert BrickPi3-Methoden
import time # für time.sleep
import RPi.GPIO as GPIO
from lib_oled96 import ssd1306
from smbus import SMBus
from ADS1x15 import ADS1115
import csv
import datetime as uhr



# Objektdeklarierung
BP = brickpi3.BrickPi3() # es wird eine Instanz der BrickPi3-Klasse erzeugt # BP wird als BrickPi-Objekt festgelegt
BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 1
BP.set_sensor_type(BP.PORT_2, BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 2

i2cbus = SMBus(1) # i2c Bus 1 am Raspberry Pi an Pins 2 & 3         
oled = ssd1306(i2cbus) # OLED Objekt erstellen
adc1 = ADS1115(address=0x48, busnum=1)

GAIN = 1 # Gain vom ADS einstellen. Mögliche Werte siehe Library
# Für Hauptplatine
main_faktor = 0.188 # Auflösung des ACS712 einstellen. Grundwert nach Datenblatt ist 0.185V/A. Durch Messung mit Last ermittelt.
main_r1 = 47148 # Widerstand R1 für den Spannungsteiler Eingangsspannung. Nominal 12V auf 3.3V
main_r2 = 18152

messwerte =[]
messwerte = [['Datum','Uhrzeit','Spannung (V)', 'Strom (A)', 'Leistung (P)']]

def csv_schreiben(werte):
    with open('messwerte_reihe5_160720.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(werte)

def Messung(adcnr):
    if adcnr == adc1:
        ad1_spannung = ((float(ACS_EingangsMessung_raw(adc1)[0])*4.096)/32768.0)/((float(main_r2)/(float(main_r1) + float(main_r2))))
        ad1_strom = ((float(ACS_EingangsMessung_raw(adc1)[1])*4.096)/32768.0)/float(main_faktor)
        ad1_strom = ad1_strom * (-1)
        power = ad1_spannung * ad1_strom
        jetzt = uhr.datetime.now()
        datum = jetzt.strftime("%d.%m.%Y")
        zeit = jetzt.strftime("%H:%M:%S")
        Anzeige('ADC1: {:.2f}V'.format(ad1_spannung), 0)
        Anzeige('ADC1: {:.2f}A'.format(ad1_strom), 10)
        Anzeige('ADC1: {:.2f}W'.format(power), 20)
        oled.display()
        messwerte.append([datum, zeit, ad1_spannung, ad1_strom, power])
        # print('U: {:.2f}V, I: {:.2f}A'.format(ad1_spannung, ad1_strom))
        return ad1_spannung, ad1_strom
    elif adcnr == adc2:
        ad2_spannung = ((float(ACS_EingangsMessung_raw(adc2)[0])*4.096)/32768.0)/((float(exp1_r2)/(float(exp1_r1) + float(exp1_r2))))
        ad2_strom = ((float(ACS_EingangsMessung_raw(adc2)[1])*4.096)/32768.0)/float(exp1_faktor)
        power = ad2_spannung * ad2_strom
        return ad2_spannung, ad2_strom, power

taster = 23 # Pin Nummer des zu verwendenden GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(taster, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO konfigurieren

oled.canvas.text((5,10), 'LOS...', fill=1)
oled.display()
#Funktionsdefinitionen

def Anzeige(text, zeilenr):
    oled.canvas.text((5,zeilenr), text, fill=1)

def ACS_EingangsMessung_raw(adcnr):
    if adcnr == adc1:
        #print('ADC1:')
        ad1_spannung_raw = adcnr.read_adc(2,gain=GAIN, data_rate=128)
        ad1_strom_raw = adcnr.read_adc_difference(0, gain=GAIN, data_rate=None)
        # volt = (float(raw)*4.096)/32768.0
        # volt_diff = (float(raw_diff)*4.096)/32768.0
        return ad1_spannung_raw, ad1_strom_raw
    elif adcnr == adc2:
        #print('ADC2:')
        ad2_spannung_raw = adcnr.read_adc(2,gain=GAIN, data_rate=128)
        ad2_strom_raw = adcnr.read_adc_difference(0, gain=GAIN, data_rate=None)
        return ad2_spannung_raw, ad2_strom_raw

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
        #else:
         #   print("Wiederholen Sie die Eingabe: ")
          #  return doIfHigh2()
        
def set_sensor_unten(): #gibt value von unterem Sensor wieder 
    
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
    #except:
    #    print("Fehler Signal Sensor unten. Bitte prüfen!")
        #BP.reset_all()

def set_sensor_oben():
    #try:
        obenvalue = False
        if BP.get_sensor(BP.PORT_1):
            if obenvalue == False:
                global oben_time
                oben_time = uhr.datetime.now()
                diff = oben_time - begin_time
                print(diff)
                print("oben erkannt")
                return True
            else:
                return False
    #except:
    #    print("Fehler Signal Sensor oben. Bitte prüfen!")
        #BP.reset_all() 


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
        
def move(value, starter):
    #try:
        status = False
        stat = True
        while stat:
            oled.cls()
            Messung(adc1)
            if set_sensor_oben() and starter:                         
                BP.set_motor_power(BP.PORT_A, (value * -1))
                if status == False:
                    status = True
            
            if status and stop_unten() and starter:
                BP.set_motor_power(BP.PORT_A, 0)
                time.sleep(0.5)
                global end_time
                end_time = uhr.datetime.now()
                # alle Messwerte in die csv Datei schreiben. Werden aber ein paar viele werden.
                # eventuell muss mit der Position des Aufrufs noch gespielt werden, also wann das aufgerufen wird
                #
                difftime = end_time - begin_time
                print(difftime)
                csv_schreiben(messwerte)
                #BP.reset_all()                                         
                # aus der schleife raus
                stat = False
            time.sleep(0.05)
    #except:
        #print("Fehler im Bewegungsablauf. Bitte prüfen!")              
        #BP.reset_all()

#Funktionsaufruf / main-Schleife für Legoprogramm:
try:
    while True:
        begin = doIfHigh2()  #wenn Taster entsprechend integriert, durch doIfHigh2() ersetzen
        # print(begin)
        value = 100
        
        if set_sensor_unten() and begin:
            print("Start unten")
            global begin_time
            begin_time = uhr.datetime.now()
            BP.set_motor_power(BP.PORT_A, value)
        move(value, begin)
        
except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.

import click
import RPi.GPIO as GPIO
import time
import csv
from ADS1x15 import ADS1115 # um die AD Wandler zu deklarieren
from lib_oled96 import ssd1306 # Bibliothek für SSD1306 OLED Displays (spezielle Version für 0.96 Zoll Version mit 128x64 Pixel)
from smbus import SMBus # alle Peripherie nutzt den i2c Bus -> SMBus auf dem Raspberry
import brickpi3 # benötigt für Kommunikation mit Brick Pi / importiert BrickPi3-Methoden

GPIO.setmode(GPIO.BCM)  # setze Namensschema für GPIO Pins
GPIO.setwarnings(False)  # Keine Warnungen bei Mehrfachdeklaration durch andere Programme

#i2cbus = SMBus(1) # i2c Bus 1 am Raspberry Pi an Pins 2 & 3         

#oled = ssd1306(i2cbus) # OLED Objekt erstellen

#adc1 = ADS1115(address=0x48, busnum=1) # ADS auf Hauptplatine initialisieren. Addresse 0x48 ist ADDR->GND



class Seilwinde:
    
    def __init__(self, csvfile):
        self.csvfile = csvfile
        self.csvwriter = None
        if self.csvfile:
            self.csvwriter = csv.writer(self.csvfile)
        self.i2cbus = SMBus(1) # i2c Bus 1 am Raspberry Pi an Pins 2 & 3         
        self.oled = ssd1306(i2cbus) # OLED Objekt erstellen
        self.adc1 = ADS1115(address=0x48, busnum=1) # ADS auf Hauptplatine initialisieren. Addresse 0x48 ist ADDR->GND
        
    def Messung(self, adcnr):
        if adcnr == adc1:
            ad1_spannung = ((float(ACS_EingangsMessung_raw(self.adc1)[0])*4.096)/32768.0)/((float(self.main_r2)/(float(self.main_r1) + float(self.main_r2))))
            ad1_strom = ((float(ACS_EingangsMessung_raw(self.adc1)[1])*4.096)/32768.0)/float(self.main_faktor)
            power = ad1_spannung * ad1_strom
            Anzeige('ADC1: {:.2f}V'.format(ad1_spannung), 0)
            Anzeige('ADC1: {:.2f}A'.format(ad1_strom), 10)
            Anzeige('ADC1: {:.2f}W)'.format(power), 20)
            self.write_csvline(ad1_spannung, ad1_strom, power)
            return ad1_spannung, ad1_strom
        elif adcnr == adc2:
            ad2_spannung = ((float(ACS_EingangsMessung_raw(adc2)[0])*4.096)/32768.0)/((float(exp1_r2)/(float(exp1_r1) + float(exp1_r2))))
            ad2_strom = ((float(ACS_EingangsMessung_raw(adc2)[1])*4.096)/32768.0)/float(exp1_faktor)
            power = ad2_spannung * ad2_strom
            #self.write_csvline(ad2_spannung, ad2_strom, power)
            return ad2_spannung, ad2_strom, power
    
    def Anzeige(self, text, zeilenr):
        oled.canvas.text((5,zeilenr), text, fill=1)
    
    def setup(self):
        Anzeige('Seilwinde bereit...', 10)
        # Variablen & Konstanten
    #
        self.GAIN = 1 # Gain vom ADS einstellen. Mögliche Werte siehe Library
    # Für Hauptplatine
        self.main_faktor = 0.188 # Auflösung des ACS712 einstellen. Grundwert nach Datenblatt ist 0.185V/A. Durch Messung mit Last ermittelt.
        self.main_r1 = 47148 # Widerstand R1 für den Spannungsteiler Eingangsspannung. Nominal 12V auf 3.3V
        self.main_r2 = 18152 # Widerstand R2 für den Spannungsteiler Eingangsspannung
        # Objektdeklarierung
        self.BP = brickpi3.BrickPi3() # es wird eine Instanz der BrickPi3-Klasse erzeugt # BP wird als BrickPi-Objekt festgelegt
        BP.set_sensor_type(self.BP.PORT_1, self.BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 1
        BP.set_sensor_type(self.BP.PORT_2, self.BP.SENSOR_TYPE.TOUCH) # Konfiguration Touch-Sensor an Port 2
        self.taster = 18 # Pin Nummer des zu verwendenden GPIO
        GPIO.setup(self.taster, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO konfigurieren

    def cleanup(self):
        for pin in self.pins:
            # Gehe die Liste an Pins durch, und entferne den event callback
            GPIO.remove_event_detect(pin)
    # Funktion für Datenlogging
    def write_csv_line(self, volt, amp, power):
        if self.csvwriter:
            self.csvwriter.writerow([volt, amp, power])

    def callback(self, channel):
        # hier die Callback Funktion einfügen (also das Motor / Taster usw)
        print('Hallo Callback!')
        
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
            
    

@click.command()
@click.option('--csvfile', '-c', type=click.File('w'))
    
def main(csvfile):
    sw = Lichtschranke(csvfile)
    sw.setup()
    while True:
        begin = doIfHigh1()  #wenn Taster entsprechend integriert, durch doIfHigh2() ersetzen
    
        value = 100
        if set_sensor_unten() and begin:
            print("Start unten")
            BP.set_motor_power(BP.PORT_A, value)
        move(value, begin) 


if __name__ == '__main__':
    main()
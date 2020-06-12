# Imports
#
import time #benötigt für sleep etc
from ADS1x15 import ADS1115 # um die AD Wandler zu deklarieren
from lib_oled96 import ssd1306 # Bibliothek für SSD1306 OLED Displays (spezielle Version für 0.96 Zoll Version mit 128x64 Pixel)
from smbus import SMBus # alle Peripherie nutzt den i2c Bus -> SMBus auf dem Raspberry

# Objektdeklarationen
#
i2cbus = SMBus(1) # i2c Bus 1 am Raspberry Pi an Pins 2 & 3         

oled = ssd1306(i2cbus) # OLED Objekt erstellen

adc1 = ADS1115(address=0x48, busnum=1) # ADS auf Hauptplatine initialisieren. Addresse 0x48 ist ADDR->GND

# Variablen & Konstanten
#
GAIN = 1 # Gain vom ADS einstellen. Mögliche Werte siehe Library
# Für Hauptplatine
main_faktor = 0.188 # Auflösung des ACS712 einstellen. Grundwert nach Datenblatt ist 0.185V/A. Durch Messung mit Last ermittelt.
main_r1 = 47148 # Widerstand R1 für den Spannungsteiler Eingangsspannung. Nominal 12V auf 3.3V
main_r2 = 18152 # Widerstand R2 für den Spannungsteiler Eingangsspannung
  
# Funktionen
# ACS messen, Werte berechnen, als Print ausgeben
def Messung(adcnr):
    if adcnr == adc1:
        ad1_spannung = ((float(ACS_EingangsMessung_raw(adc1)[0])*4.096)/32768.0)/((float(main_r2)/(float(main_r1) + float(main_r2))))
        ad1_strom = ((float(ACS_EingangsMessung_raw(adc1)[1])*4.096)/32768.0)/float(main_faktor)
        power = ad1_spannung * ad1_strom
        Anzeige('ADC1: {:.2f}V'.format(ad1_spannung), 0)
        Anzeige('ADC1: {:.2f}A'.format(ad1_strom), 10)
        Anzeige('ADC1: {:.2f}W)'.format(power), 20)
        return ad1_spannung, ad1_strom
    elif adcnr == adc2:
        ad2_spannung = ((float(ACS_EingangsMessung_raw(adc2)[0])*4.096)/32768.0)/((float(exp1_r2)/(float(exp1_r1) + float(exp1_r2))))
        ad2_strom = ((float(ACS_EingangsMessung_raw(adc2)[1])*4.096)/32768.0)/float(exp1_faktor)
        return ad2_spannung, ad2_strom
       
def Anzeige(text, zeilenr):
    oled.canvas.text((5,zeilenr), text, fill=1)
    

oled.cls()
oled.canvas.text((5,5),    'Messmodul Projekt 2', fill=1)
oled.display()

# main Schleife
while True:
#to do


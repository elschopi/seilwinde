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
adc2 = ADS1115(address=0x49, busnum=1) # ADS auf Erweiterungsplatine initialisieren. Addresse 0x49 ist ADDR -> VCC

# Variablen & Konstanten
#
GAIN = 1 # Gain vom ADS einstellen. Mögliche Werte siehe Library
# Für Hauptplatine
main_faktor = 0.188 # Auflösung des ACS712 einstellen. Grundwert nach Datenblatt ist 0.185V/A. Durch Messung mit Last ermittelt.
main_r1 = 47148 # Widerstand R1 für den Spannungsteiler Eingangsspannung. Nominal 12V auf 3.3V
main_r2 = 18152 # Widerstand R2 für den Spannungsteiler Eingangsspannung
# Für Erweiterungsplatine
exp1_faktor = 0.185 # Auflösung des ACS712 einstellen. Grundwert nach Datenblatt ist 0.185V/A. Durch Messung mit Last ermittelt.
exp1_r1 = 51000 # Widerstand R1 für den Spannungsteiler Eingangsspannung. Nominal 9V auf 3.3V
exp1_r2 = 27000 # Widerstand R2 für den Spannungsteiler Eingangsspannung


  
# Funktionen
# Mit dieser Funktion werden Strom und Spannung von der gewünschten Platine abgerufen
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

# ACS messen, Werte berechnen, als Print ausgeben
def Messung(adcnr):
    if adcnr == adc1:
        ad1_spannung = ((float(ACS_EingangsMessung_raw(adc1)[0])*4.096)/32768.0)/((float(main_r2)/(float(main_r1) + float(main_r2))))
        ad1_strom = ((float(ACS_EingangsMessung_raw(adc1)[1])*4.096)/32768.0)/float(main_faktor)
        return ad1_spannung, ad1_strom
    elif adcnr == adc2:
        ad2_spannung = ((float(ACS_EingangsMessung_raw(adc2)[0])*4.096)/32768.0)/((float(exp1_r2)/(float(exp1_r1) + float(exp1_r2))))
        ad2_strom = ((float(ACS_EingangsMessung_raw(adc2)[1])*4.096)/32768.0)/float(exp1_faktor)
        return ad2_spannung, ad2_strom
       

oled.cls()
oled.canvas.text((5,5),    'Messmodul Projekt 2', fill=1)
oled.display()

# main Schleife
while True:
    oled.cls()
    oled.canvas.text((5,0),    'ADC1: {:.2f}V, {:.2f}A'.format(Messung(adc1)[0],Messung(adc1)[1]), fill=1)
    oled.canvas.text((5,10),    'ADC2: {:.2f}V, {:.2f}A'.format(Messung(adc2)[0],Messung(adc2)[1]), fill=1)
    oled.canvas.text((5,20),    '.', fill=1)
    oled.canvas.text((5,30),    '.', fill=1)
    oled.canvas.text((5,40),    '.', fill=1)
    oled.canvas.text((5,50),    '.', fill=1)
    oled.display()
    time.sleep(1)
#to do
import RPi.GPIO as GPIO
import time

# Pin Nummer des zu verwendenden GPIO
taster = 18

# GPIO konfigurieren
GPIO.setmode(GPIO.BCM)
GPIO.setup(taster, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setze ein 'status' flag als Zustandsspeicher für den Taster
status = 0

while True:
    # Abfrage des GPIO Status
    buttonState = GPIO.input(taster)
    print(buttonState)
    
    # Wenn der Status 0 ist, ist der Taster gedrückt worden (das liegt daran, dass der GPIO mit Pullup auf 3.3V gezogen wird und gegen GND schaltet)
    if buttonState == 0:
        time.sleep(0.5)
        # Diese Zeilen toggeln den Zustand. 
        if status==0:
            status=1
        else:
            status=0
    # Hier wird bestimmt, was gemacht werden soll (Programmaufruf, LED ein/aus, usw)
    if status==1:
        print('AN')
    else:
        print('AUS')
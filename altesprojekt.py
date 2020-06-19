import click
import RPi.GPIO as GPIO
import time
import csv

GPIO.setmode(GPIO.BCM)  # setze Namensschema für GPIO Pins
GPIO.setwarnings(False)  # Keine Warnungen bei Mehrfachdeklaration durch andere Programme


class Lichtschranke:
    # Definition der Lichtschranken Pins:
    pins = (13, 19, 26, 16)
    # Definition der Strecken zwischen den einzelnen Lichtschranken (in cm):
    strecken = (0.1, 0.3, 0.5)

    def __init__(self, csvfile):
        self.csvfile = csvfile
        self.csvwriter = None
        if self.csvfile:
            self.csvwriter = csv.writer(self.csvfile)
        # Initialisiere eine Liste mit gemessenen Zeiten mit der selben Anzahl wie die Anzahl an Pins:
        self.times = [0.0, ] * len(self.pins)
        # Initialisiere eine Liste mit gemessenen Geschwindigkeiten die um 1 kleiner ist als die Anzahl Pins,
        # da es immer einen Abschnitt weniger als die begrenzenden Lichtschranken gibt.
        self.speeds = [0.0, ] * (len(self.pins) - 1)

    def setup(self):
        for pin in self.pins:
            # Gehe die Liste an Pins durch, und setze die GPIO einstellungen und den event callback
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(pin, GPIO.RISING, callback=self.callback, bouncetime=200)

    def cleanup(self):
        for pin in self.pins:
            # Gehe die Liste an Pins durch, und entferne den event callback
            GPIO.remove_event_detect(pin)

    def write_csv_line(self, index, pin, length, abstime, reltime):
        if self.csvwriter:
            self.csvwriter.writerow([index, pin, length, abstime, reltime])


    def callback(self, channel):
        if not GPIO.input(channel):
            # Ist keiner unserer Eingänge, ignorieren.
            return
        # Die variable index gibt die 0-basierte nummer des Pins in der liste an.
        index = self.pins.index(channel)
        self.times[index] = time.time()
        if index == 0:
            # Der 1. Pin!
            print("Starte Zeiterfassung!")
            # Erfasse für jeden Pin eine Zeit mit dem selben index wie der Pin selbst.
            self.write_csv_line(index, channel, 0, self.times[index], 0)
        if index > 0:
            # Ab dem 2. Pin haben wir Unterschiede zum messen
            # Berechne die zeitdifferenz zwischen dem aktuellen Pin und dem vorhergehenden
            tdiff = self.times[index] - self.times[index - 1]
            # Da die Strecken um eines kürzer sind, müssen wir für den Pin mit Index 1 die Strecke 0 verwenden usw.
            self.speeds[index - 1] = self.strecken[index - 1] / tdiff
            # Hier geben wir Abschnitt 1 basiert aus, da der Erste pin 0 basiert ist können wir direkt index verwenden.
            print("Abschnitt {}: {}".format(index, tdiff))
            print("v{}: {} cm/s".format(index, self.speeds[index - 1]))
            self.write_csv_line(index, channel, self.strecken[index - 1], self.times[index], tdiff)
        if index == len(self.pins) - 1:
            print("Durchschnittsgeschwindigkeit: {} cm/s".format(sum(self.speeds) / len(self.speeds)))


@click.command()
@click.option('--csvfile', '-c', type=click.File('w'))
def main(csvfile):
    ls = Lichtschranke(csvfile)
    ls.setup()
    while True:
        try:
            while True:
                time.sleep(0.01)
        finally:
            ls.cleanup()


if __name__ == '__main__':
    main()

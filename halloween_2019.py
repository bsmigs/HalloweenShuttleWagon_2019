import RPi.GPIO as GPIO
from signal import pause
import time
from subprocess import call

# define LED pins
leftHeadlightLed = 33
rightHeadlightLed = 35
thruster1Led = 29
thruster2Led = 31
thruster3Led = 32

# define button pins
headlightButtonPin = 13
thrusterButtonPin = 12
nasaSoundsButtonPin = 11

nasaSounds = ["569462main_eagle_has_landed.wav", "574928main_houston_problem.wav", "590325main_ringtone_kennedy_WeChoose.wav", 
              "590318main_ringtone_135_launch.wav", "640392main_STS-26_Liftoff.wav"]

numWavFiles = len(nasaSounds)
wavFileCounter = 0

headlightLedStatus = True
thrusterLedStatus = True

def setup():
    # use physical pin numbering
    GPIO.setMode(GPIO.BOARD)

    GPIO.setup(headlightButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(thrusterButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(nasaSoundsButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # define headlight pins to be output pins
    GPIO.setup(leftHeadlightLed, GPIO.OUT)
    GPIO.setup(rightHeadlightLed, GPIO.OUT)
    GPIO.setup(thruster1Led, GPIO.OUT)
    GPIO.setup(thruster2Led, GPIO.OUT)
    GPIO.setup(thruster3Led, GPIO.OUT)

    # set initial state of headlights to be low
    GPIO.output(leftHeadlightLed, GPIO.LOW)
    GPIO.output(rightHeadlightLed, GPIO.LOW)
    GPIO.output(thruster1Led, GPIO.LOW)
    GPIO.output(thruster2Led, GPIO.LOW)
    GPIO.output(thruster3Led, GPIO.LOW)

def toggleHeadlights(ev=None):
    global headlightLedStatus

    # temporarily disable other events
    GPIO.remove_event_detect(thrusterButtonPin)
    GPIO.remove_event_detect(nasaSoundsButtonPin)

    GPIO.output(leftHeadlightLed, headlightLedStatus)
    GPIO.output(rightHeadlightLed, headlightLedStatus)

    if (headlightLedStatus == 1):
        print("headlights on...\n")
    else:
        print("headlights off...\n")

    headlightLedStatus = not headlightLedStatus

    # reenable other events
    GPIO.add_event_detect(thrustersButtonPin, GPIO.RISING, callback=operateThrusters, bouncetime=25000)
    GPIO.add_event_detect(nasaSoundsButtonPin, GPIO.RISING, callback=playNasaSounds, bouncetime=25000)

def operateThrusters(ev=None):
    global thrusterLedStatus

    # temporarily disable other events
    GPIO.remove_event_detect(headlightButtonPin)
    GPIO.remove_event_detect(nasaSoundsButtonPin)

    # set LEDs high
    GPIO.output(thruster1Led, GPIO.HIGH)
    GPIO.output(thruster2Led, GPIO.HIGH)
    GPIO.output(thruster3Led, GPIO.HIGH)

    print("thrusters on...\n")

    # play the sound
    call(["aplay", "590318main_ringtone_135_launch.wav"])

    # turn off LEDs again
    GPIO.output(thruster1Led, GPIO.LOW)
    GPIO.output(thruster2Led, GPIO.LOW)
    GPIO.output(thruster3Led, GPIO.LOW)

    # reenable other events
    GPIO.add_event_detect(headlightButtonPin, GPIO.RISING, callback=toggleHeadlights, bouncetime=200)
    GPIO.add_event_detect(nasaSoundsButtonPin, GPIO.RISING, callback=playNasaSounds, bouncetime=25000)

def playNasaSounds(ev=None):
    global wavFileCounter

    # temporarily disable other events
    GPIO.remove_event_detect(thrusterButtonPin)
    GPIO.remove_event_detect(headlightButtonPin)

    call(["aplay", nasaSounds[wavFileCounter]])
    wavFileCounter = (wavFileCounter + 1) % numWavFiles

    # reenable other events
    GPIO.add_event_detect(headlightButtonPin, GPIO.RISING, callback=toggleHeadlights, bouncetime=200)
    GPIO.add_event_detect(thrusterButtonPin, GPIO.RISING, callback=operateThrusters, bouncetime=25000)

def loop():
    GPIO.add_event_detect(headlightButtonPin, GPIO.RISING, callback=toggleHeadlights, bouncetime=200)
    GPIO.add_event_detect(thrustersButtonPin, GPIO.RISING, callback=operateThrusters, bouncetime=25000)
    GPIO.add_event_detect(nasaSoundsButtonPin, GPIO.RISING, callback=playNasaSounds, bouncetime=25000)

    while True:
        time.sleep(1)

def destroy():
    GPIO.output(leftHeadlightLed, GPIO.LOW)
    GPIO.output(rightHeadlightLed, GPIO.LOW)
    GPIO.output(thruster1Led, GPIO.LOW)
    GPIO.output(thruster2Led, GPIO.LOW)
    GPIO.output(thruster3Led, GPIO.LOW)

if __name__ = "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

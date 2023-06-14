import RPi.GPIO as pi
from picamera import PiCamera
from time import sleep

pi.setmode(pi.BCM)
pi.setwarnings(False)

class Laser:
    MIN_DELAY=0
    def __init__(self, pin):
        self.pin=pin

    def turn_on(self):
        pi.output(self.pin,True)

    def turn_off(self):
        pi.output(self.pin,False)


class Motor:
    STEPS=512
    MIN_DELAY=100/1000.0
    STEP_ANGLE=360/512.0
    def __init__(self, enable_pin, coilA1_pin, coilA2_pin, coilB1_pin, coilB2_pin):
        self.enable_pin=enable_pin
        self.coilA1_pin=coilA1_pin
        self.coilA2_pin=coilA2_pin
        self.coilB1_pin=coilB1_pin
        self.coilB2_pin=coilB2_pin
        pi.output(enable_pin, True)

    def fw_step(self,delay):
        self.setStep(1, 0, 1, 0)
        sleep(delay)
        self.setStep(0, 1, 1, 0)
        sleep(delay)
        self.setStep(0, 1, 0, 1)
        sleep(delay)
        self.setStep(1, 0, 0, 1)
        sleep(delay)

    def bw_step(self,delay):
        self.setStep(1, 0, 0, 1)
        sleep(delay)
        self.setStep(0, 1, 0, 1)
        sleep(delay)
        self.setStep(0, 1, 1, 0)
        sleep(delay)
        self.setStep(1, 0, 1, 0)
        sleep(delay)

    def release(self):
        self.setStep(0,0,0,0)

    def setStep(self,a, b, c, d):
        pi.output(self.coilA1_pin, a)
        pi.output(self.coilA2_pin, b)
        pi.output(self.coilB1_pin, c)
        pi.output(self.coilB2_pin, d)

class Camera:
    def __init__(self, resolution):
        self.camera=PiCamera()
        self.camera.resolution=resolution

class Raspberry:
    def set_outputs(self, pins):
        for i in range(len(pins)):
            pi.setup(pins[i], pi.OUT)

    def set_inputs(self, pins):
        for i in range(len(pins)):
            pi.setup(pins[i], pi.IN)

    def clean(self, pins):
        for i in range(len(pins)):
            pi.output(pins[i], False)
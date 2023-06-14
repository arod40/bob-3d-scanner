import device_control as dc
#import numpy as np
import picamera.array as arr
#import cv2 as cv
import time
from picamera import PiCamera
from matplotlib import pyplot as plt
import image as im
import sys

enable_pin = 18
coil_A_1_pin = 4
coil_A_2_pin = 17
coil_B_1_pin = 23
coil_B_2_pin = 24
laser_pin = 22
resolution = (320,240)
calibration=im.calibration()

#setting Raspberry up
rpi=dc.Raspberry()
rpi.set_outputs([enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin, laser_pin])


#devices controllers
camera=PiCamera()
camera.resolution=resolution
motor=dc.Motor(enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin)
laser=dc.Laser(laser_pin)
image_proc=im.image_processor(calibration)

def Makescan():
    steps = motor.STEPS
    delay = motor.MIN_DELAY/10
    _3D_points=[]
    for i in range(steps):
        print(str(i)+"\n")
        image = arr.PiRGBArray(camera)
        camera.capture(image, 'rgb')
        laser.turn_on()
        image_laser = arr.PiRGBArray(camera)
        camera.capture(image_laser, 'rgb')
        laser.turn_off()
        _3D_points+=image_proc.process(image.array, image_laser.array, i)
        motor.fw_step(delay)
    image_proc.write_ply(_3D_points)

    rpi.clean([enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin, laser_pin])


def Calibrate():
    #camera.start_preview()
    image = arr.PiRGBArray(camera)
    camera.capture(image, 'rgb')
    plt.imshow(image.array)
    plt.show()
    x=raw_input("Laser-Camera Distance?")
    im.calibration.laser_dist=float(x)
    x=raw_input("Platform-Camera Distance?")
    im.calibration.pltfrm_dist=float(x)
    print "Put the laser over the axis frame detector on the platform and press a key to continue..."
    laser.turn_on()
    x=raw_input()
    image_l = arr.PiRGBArray(camera)
    camera.capture(image_l, 'rgb')
    laser.turn_off()
    plt.imshow(image_l.array)
    plt.show()
    x=raw_input("Axis-Line?")
    im.calibration.axis_line=float(x)
    x=raw_input ("Remove the axis frame detector and put the floor line detector on the platform.Press any key to continue ...")
    laser.turn_on()
    image_l = arr.PiRGBArray(camera)
    camera.capture(image_l, 'rgb')
    laser.turn_off()
    plt.imshow(image_l.array)
    plt.show()
    x1=raw_input("x1?")
    y1=raw_input("y1?")
    x2=raw_input("x2?")
    y2=raw_input("y2?")
    x=image_proc.get_floor_line(float(x1),float(y1),float(x2),float(y2))
    im.calibration.floor_line=x
    print "Remove the floor line detector and put the object on the platform."
    while(True):
        x=raw_input("Threshold Value?")
        im.calibration.threshold=float(x)
        laser.turn_on()
        image_l = arr.PiRGBArray(camera)
        camera.capture(image_l, 'rgb')
        laser.turn_off()
        image = arr.PiRGBArray(camera)
        camera.capture(image, 'rgb')
        ret,img=image_proc.detect_laser(image.array,image_l.array)
        plt.imshow(img,'gray')
        plt.show()
        x=raw_input("Nice? y/n")
        if x=="y":
            break
    print "ROI?"
    image = arr.PiRGBArray(camera)
    camera.capture(image, 'rgb')
    plt.imshow(image.array)
    plt.show()
    x=raw_input("Top?")
    im.calibration.top=float(x)
    x=raw_input ("Bottom?")
    im.calibration.bottom=float(x)
    x=raw_input ("Left?")
    im.calibration.left=float(x)
    x=raw_input( "Right?")
    im.calibration.right=float(x)
    print "Succesfully Calibrated"
    print "Laser-Camera Distance"
    print im.calibration.laser_dist
    print "Platform-Camera Distance"
    print im.calibration.pltfrm_dist
    print "Axis line"
    print im.calibration.axis_line
    print "Floor line (m,n)"
    print im.calibration.floor_line
    print "Threshold"
    print im.calibration.threshold
    print "Top"
    print im.calibration.top
    print "Bottom"
    print im.calibration.bottom
    print "Left"
    print im.calibration.left
    print "Right"
    print im.calibration.right

def calibrate():
    print(calibration.msgs["welcome"]

    calibration.execute_steps(motor,camera,laser):

    print(calibration.msgs["sure"]
    print(calibration.__str__)
    print(calibration.msgs["save"]
    print(calibration.msgs["finish"]


while(True):
    x=raw_input("Command: ")
    if x=="calibrate":
        Calibrate()
    elif x=="scan":
        Makescan()
    else:
        print "Try Again"

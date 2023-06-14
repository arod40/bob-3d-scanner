import device_control as dc
from picamera import PiCamera
import picamera.array as arr
from matplotlib import pyplot as plt
import  cv2 as cv
from time import sleep

def map_x(img, i,j):
    return img.shape[1]-i

def map_y(img, i,j):
    return j

def mirror(img):
    return cv.remap(img,map_x, map_y,cv.INTER_LINEAR)


enable_pin = 18
coil_A_1_pin = 4
coil_A_2_pin = 17
coil_B_1_pin = 23
coil_B_2_pin = 24
laser_pin = 22
resolution = (320,240)



rpi=dc.Raspberry()
rpi.set_outputs([laser_pin, enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin])
laser=dc.Laser(laser_pin)
motor=dc.Motor(enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin)

rpi.clean([laser_pin, enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin])

while(True):
    print("on")
    laser.turn_on()
    sleep(1)
    print("off")
    laser.turn_off()
    sleep(1)

x=512
delay=dc.Motor.MIN_DELAY
while x:
  print(x)
  motor.fw_step(0.05)
  x=x-1

#image=cv.imread("/home/pi/foo2.jpg")
#plt.imshow(image)
#plt.show()
#camera=PiCamera()
#camera.resolution=resolution
# #camera.exposure_mode='night'
# #camera.shutter_speed=800
# #camera.iso=800
# #camera.start_preview()
#THRESHOLD=30

#capt = arr.PiRGBArray(camera)
#camera.capture(capt, 'rgb')

#laser.turn_on()
#capt2 = arr.PiRGBArray(camera)
#camera.capture(capt2, 'rgb')

laser.turn_off()
#
#red=cv.subtract(capt2.array,capt.array)
#gray=cv.cvtColor(red,cv.COLOR_RGB2GRAY)
#plt.imshow(gray,'gray')
#plt.show()
#

#ret,thresh1 = cv.threshold(gray,THRESHOLD,255,cv.THRESH_BINARY)
# #ret,thresh2 = cv.threshold(red,THRESHOLD,255,cv.THRESH_BINARY_INV)
# ret,thresh3 = cv.threshold(red,THRESHOLD,255,cv.THRESH_TRUNC)
# #ret,thresh4 = cv.threshold(red,THRESHOLD,255,cv.THRESH_TOZERO)
# #ret,thresh5 = cv.threshold(red,THRESHOLD,255,cv.THRESH_TOZERO_INV)
#
# reflect=mirror(capt2.array);
#
# titles = ['Original ImageL','Dif','BINARY','TRUNC']
# images = [reflect,red, thresh1, thresh3]
#
# for i in xrange(4):
#     plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
#     plt.title(titles[i])
#     plt.xticks([]),plt.yticks([])
# plt.show()
#
#plt.imshow(thresh1,'gray')
#plt.show()
#
#
rpi.clean([laser_pin, enable_pin, coil_A_1_pin, coil_A_2_pin, coil_B_1_pin, coil_B_2_pin])


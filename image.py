import cv2 as cv
import  numpy as np
import device_control as dc
from matplotlib import pyplot as plt
import picamera.array as arr

class image_processor:
    def __init__(self, calibration):
        self.calibration=calibration

    def get_axis_line(self,laser_image,image):
        ret, laser = self.detect_laser(image, laser_image)
        _2D_points = self.thin_laser3(laser, image)
        return _2D_points[0][0] 

    def get_floor_line(self,x1,y1,x2,y2):
        m=(y2-y1)/(x2-x1)
        n=y2-m*x2
        return (m,n) 
    
    def process(self, image, laser_image, current_steps):
        image=image[self.calibration.top:self.calibration.bottom, self.calibration.left:self.calibration.right]
        laser_image=laser_image[self.calibration.top:self.calibration.bottom, self.calibration.left:self.calibration.right]
        ret, laser = self.detect_laser(image, laser_image)
        #print(laser)
        #plt.imshow(laser, 'gray')
        #plt.show()
        _2D_points = self.thin_laser2(laser, image)
        return self.get_3D_points(_2D_points, current_steps * dc.Motor.STEP_ANGLE)

    def detect_laser(self, image, image_laser):
        sub=cv.subtract(image_laser,image)
        #no_noise=cv.GaussianBlur(sub,(3,3),0)
        gray=cv.cvtColor(sub,cv.COLOR_RGB2GRAY)
        thr=self.calibration.threshold
        #red=no_noise.array[0:,0:,0]
        return cv.threshold(gray, thr, 255, cv.THRESH_BINARY)

    # def thin_laser_faster(self,thr_image,orig_image):
    #     res=thr_image.
    def thin_laser(self,thr_image, orig_image):
        points = []
        beg = 0
        end = 0
        for i in range(thr_image.shape[0]):
            asig = False
            for j in range(thr_image.shape[1]):
                if thr_image[i, j,0]== 255:
                    if not asig:
                        beg = j
                        asig = True
                else:
                    if asig:
                        end = j - 1
                        y=(beg + end) / 2
                        points.append((y+self.calibration.left, i+self.calibration.top, orig_image[i,y,0], orig_image[i,y,1], orig_image[i,y,2]))
                        asig = False
        return points

    #this works
    def thin_laser2(self,thr_image, orig_image):
        points = []
        for i in range(thr_image.shape[0]):
            for j in range(thr_image.shape[1]):
                if thr_image[i, j] == 255:
                    points.append((j+self.calibration.left, i+self.calibration.top, orig_image[i, j, 0], orig_image[i, j, 1], orig_image[i, j, 2]))
                    break

        return points

    def thin_laser2inv(self,thr_image, orig_image):
        points = []
        for i in range(thr_image.shape[0]):
            for j in range(thr_image.shape[1]):
                if thr_image[i, thr_image.shape[1]-j-1, 0] == 255:
                    points.append((thr_image.shape[1]-j-1+self.calibration.left, i+self.calibration.top, orig_image[i, thr_image.shape[1]-j-1, 0], orig_image[i, thr_image.shape[1]-j-1, 1], orig_image[i, thr_image.shape[1]-j-1, 2]))
                    break

        return points
    
    def thin_laser3(self, thr_image, orig_image):
        points = []
        for i in range(thr_image.shape[0]):
            for j in range(thr_image.shape[1]):
                if thr_image[i, j] == 255:
                    points.append((j+self.calibration.left, i+self.calibration.top, orig_image[i, j, 0], orig_image[i, j, 1], orig_image[i, j, 2]))

        sum=0.0
        total=0
        rec_points=[]
        for i in range(len(points)):
            sum+=points[i][0]
            total+=1
        if total==0:
            total=1

        x=sum/total
        for i in range(len(points)):
            rec_points.append((x, points[i][1], points[i][2], points[i][3], points[i][4]))

        return rec_points

    def get_3D_points(self, _2D_points, alpha):
        _3D_points=[]
        for i in range(len(_2D_points)):
            point=_2D_points[i]
            _3D_points.append(self.get_point(point, alpha))
        return _3D_points

    def get_point(self, _2D_point, alpha):
        laser_dist=self.calibration.laser_dist
        pltfrm_dist=self.calibration.pltfrm_dist
        floor_line=self.calibration.floor_line
        axis_line=calibration.axis_line

        #ratio
        hip = np.sqrt(laser_dist**2 + pltfrm_dist**2)
        k = hip / laser_dist

        distPx = np.abs(axis_line - _2D_point[0])

        r = k * distPx;

        #height
        z=-(_2D_point[1]-(floor_line[0]*_2D_point[0]+floor_line[1])) #h=yP-(m*xP+n)

        #angle
        if axis_line<_2D_point[0]:
            a=(180+alpha)%360
        else:
            a=alpha

        cart=self.cyl_to_cart(r,a,z)
        return {'x':cart[0], 'y':cart[1], 'z':cart[2], 'r': _2D_point[2], 'g': _2D_point[3], 'b': _2D_point[4]}

    def cyl_to_cart(self, r, a, z):
        a=a/180*np.pi
        x = r * np.cos(a)
        y = r * np.sin(a);
        return (x,y,z)

    def write_ply(self, points):
        file = open(self.calibration.name+'.ply', 'w')
        file.write("ply\nformat ascii 1.0\ncomment VCGLIB generated\nelement vertex %u\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nproperty uchar alpha\nelement face 0\nproperty list uchar int vertex_indices\nend_header\n" %(len(points)))
        for i in range(len(points)):
            point=points[i]
            file.write("%f %f %f %u %u %u %u\n" %(point['x'], point['y'], point['z'], point['r'], point['g'], point['b'], 255))
        file.close()
        return


class calibration_network:
    def _send_image(sock, image):
        sock.send(struct.pack("I",len(image)))
        sock.send(image)

    
    def calibrate_network():
        s=socket.socket()
        s.bind(("192.168.56.99", 7777))
        s.listen(1)
        sc,_=s.accept()

        #object's region of interest
        send_image(sc,self.full_image())

        #laser incidence over object
        send_image(sc,self.threshold_image())

        #vertical line calibrator region of interest
        send_image(sc,self.full_image())

        #vertical line calibrator  threshold
        send_image(sc,self.threshold_image)

        #horizontal line calibrator region of interest
        send_image(sc,self.full_image())

        #horizontal line calibrator  threshold
        send_image(sc,self.threshold_image)

    pass

class calibration:
    msgs={
        "welcome":"Hi you're about to calibrate BOB",
        "sure":"This is how your calibration looks. Are you sure this is correct?",
        "type":"Type the name of the parameter you would like to recalculate",
        "save":"Would you like to save this calibration in a file?",
        "type_filename":"Type the correct file path",
        "file_exists":"File already exists",
        "wrong_path":"Path doesn't exists",
        "finish":"You have finished the calibration"
    }
    prop_types={
        "threshold":int,
        "slope":float,
        "intercept":float,
        "axis_line":int,
        "laser_dist":float,
        "pltfrm_dist":float,
        "top":int,
        "left":int,
        "right":int,
        "bottom":int,
        "filename":str
    }

    def __init__(self, path=None, motor, camera, laser):
        self.camera=camera
        self.laser=laser
        self.motor=motor
        if path:
            config=open(path)
            for line in config.readlines():
                line=line[:-1] if line[-1]=='\n' else line
                splt=line.split(':')
                property=splt[0]
                value=calibration.prop_types[splt[0]](splt[1])
                self.__setattr__(property,value)

    def save_in_file(self, path=None):
        path=path if path else self.filename+"_calibration"
        fd=open(path,'x')
        for key in self.__dict__:
            fd.write(key+":"+str(self.__dict__[key])+"\n")

    def _full_image(self):
        image = arr.PiRGBArray(camera)
        self.camera.capture(image, 'rgb')
        cv2.imwrite("picture.jpg", image)
        fd=open("full.jpg", 'rb')
        imageData=fd.read()
        return imageData

    def _threshold_image(self):
        image = arr.PiRGBArray(self.camera)
        self.camera.capture(image, 'rgb')
        self.laser.turn_on()
        image_laser = arr.PiRGBArray(self.camera)
        self.camera.capture(image_laser, 'rgb')
        self.laser.turn_off()
        sub=cv.subtract(image_laser,image)
        cv2.imwrite("picture.jpg", sub)
        fd=open("threshold.jpg", 'rb')
        image_data=fd.read()
        return image_data

    #steps
    def _step_region_of_interest(self):
        print("Put the object on the platform, press a key"+\
        "to watch the it's fitness on the image. Then, introduce the four"+\
        "borders of the Region of Interest")
        image = arr.PiRGBArray(self.camera)
        self.camera.capture(image, 'rgb')
        plt.imshow(image.array)
        plt.show()
        x=raw_input("Top border: ")
        self.top=float(x)
        x=raw_input ("Bottom border: ")
        self.bottom=float(x)
        x=raw_input ("Left border: ")
        self.left=float(x)
        x=raw_input( "Right border: ")
        self.right=float(x)
    
    def _step_fixed_distances(self):
        print("Introduce the Laser-Camera distance and the Platform-Camera distance"+\
        "when asked. Press a key to preview")
        image = arr.PiRGBArray(self.camera)
        self.camera.capture(image, 'rgb')
        plt.imshow(image.array)
        plt.show()
        x=raw_input("Laser-Camera Distance?")
        self.laser_dist=float(x)
        x=raw_input("Platform-Camera Distance?")
        self.pltfrm_dist=float(x)
        
    def execute_steps(self):
        #region of interest



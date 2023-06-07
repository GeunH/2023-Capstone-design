# -*- coding: utf-8 -*-
import time
import threading
import picamera
import os
import cv2
import threading
import RPi.GPIO as GPIO
import io
import numpy as np
import zipfile
import pickle


GPIO.setmode(GPIO.BCM)

STEP_PIN = 21  # arduino 6
DIR_PIN = 20    # arduino 7
EN_PIN = 16    # arduino 8

Car_Wheel_1 = 5    #5
Car_Wheel_2 = 6    #6
Car_Wheel_3 = 3
Car_Wheel_4 = 2
SPEED_2 = 18
SPEED_1 = 12

SERVO_PIN = 13

GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

GPIO.setup(Car_Wheel_1, GPIO.OUT)
GPIO.setup(Car_Wheel_2, GPIO.OUT)
GPIO.setup(Car_Wheel_3, GPIO.OUT)
GPIO.setup(Car_Wheel_4, GPIO.OUT)

GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50) 
pwm.start(0)

GEAR_PIN = 19

GPIO.setup(GEAR_PIN, GPIO.OUT)
g_pwm = GPIO.PWM(GEAR_PIN, 50)
g_pwm.start(0)

GPIO.setup(SPEED_1, GPIO.OUT)
GPIO.setup(SPEED_2, GPIO.OUT) 

go_left = GPIO.PWM(SPEED_1, 1000)
go_left.start(0)

go_right = GPIO.PWM(SPEED_2, 1000)
go_right.start(0)

folder_name = time.strftime('%Y%m%d%H%M%S')
SAVE_DIRECTORY = '/home/pi/capstone/images/'+ folder_name
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)
    os.makedirs(SAVE_DIRECTORY + "/images")


def step_motor(_dir):
    GPIO.output(EN_PIN, GPIO.LOW)
    if(_dir == 1) :  
        GPIO.output(DIR_PIN, GPIO.HIGH)
        for i in range(5000):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0006)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.0006)
        time.sleep(1)
        
    # GPIO LOW 
    elif(_dir == 0):
        GPIO.output(DIR_PIN, GPIO.LOW)
        for i in range(5000):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0006)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.0006)
        time.sleep(1)

class CameraThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        self.camera.resolution = (3280, 2464)
        self.frames = []
        self.stopped = False

    def run(self):
        while not self.stopped:
            frame = self.capture_frame()
            self.frames.append(frame)

    def capture_frame(self):
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        
        flipped_image = cv2.flip(image, 0)
        return flipped_image

    def stop(self):
        self.stopped = True


# �̺�Ʈ ��ü ����
pause_event = threading.Event()

class SaveThread(threading.Thread):
    def __init__(self):
        self.frame_cnt=0
        threading.Thread.__init__(self)
        self.stopped = False


    def run(self):
        while not self.stopped:
            pause_event.wait()  

            if len(camera_thread.frames)>0 :
                if self.frame_cnt % 2 == 0:     
                    filename = f'frame_{self.frame_cnt//2}.jpg'
                    file_path = os.path.join(SAVE_DIRECTORY + "/images", filename)
                    cv2.imwrite(file_path, camera_thread.frames[0])
                self.frame_cnt += 1
                camera_thread.frames = []

    def stop(self):
        self.stopped = True
    def restart(self):
        self.stopped = False

def car_moving():
    # while True:
    GPIO.output(Car_Wheel_1, GPIO.HIGH)
    GPIO.output(Car_Wheel_2, GPIO.LOW)
    GPIO.output(Car_Wheel_3, GPIO.HIGH)
    GPIO.output(Car_Wheel_4, GPIO.LOW)
    go_left.ChangeDutyCycle(87)
    go_right.ChangeDutyCycle(87)

    time.sleep(45) # 35��sleep
    
def car_stop():
    # while True:
    GPIO.output(Car_Wheel_1, GPIO.LOW)
    GPIO.output(Car_Wheel_2, GPIO.LOW)
    GPIO.output(Car_Wheel_3, GPIO.LOW)
    GPIO.output(Car_Wheel_4, GPIO.LOW)
    

def set_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)
    
def gear_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(GEAR_PIN, True)
    g_pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(GEAR_PIN, False)
    g_pwm.ChangeDutyCycle(0)

if __name__ == '__main__':
    try:
       
        camera_thread = CameraThread()
        camera_thread.start()
        
        save_thread = SaveThread()
        save_thread.start()
        
        pause_event.set()
        
        for i in range(0,4):
            set_angle(25 - 5 * i)
            car_moving()
            car_stop()
            pause_event.clear()
            step_motor(0)
            pause_event.set()
    
        
        time.sleep(1)
        gear_angle(68)
        gear_angle(68)
        set_angle(5)
        car_moving()
        car_stop()
        
        pause_event.clear()
        
        for i in range(0,4):
           step_motor(1)
           
        time.sleep(1)
        gear_angle(115)
        gear_angle(115)
        
        
        folder_path = SAVE_DIRECTORY
        zip_directory = '/home/pi/capstone/images/zip'  
        zip_path = os.path.join(zip_directory, folder_name + '.zip')
        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))
        zipf.close()
        
        time.sleep(3)
        pause_event.set()
        camera_thread.stop()
        camera_thread.join()
        
        save_thread.stop()
        save_thread.join()
        pause_event.clear()
        
        GPIO.output(EN_PIN, GPIO.HIGH)
        GPIO.cleanup()   
        
        
    except KeyboardInterrupt:
        GPIO.output(EN_PIN, GPIO.HIGH)
        GPIO.cleanup()

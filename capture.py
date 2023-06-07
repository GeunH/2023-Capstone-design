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
pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터를 제어하기 위해 50Hz의 주파수로 PWM을 설정합니다.
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

#camera = picamera.PiCamera()
folder_name = 'object_img'
SAVE_DIRECTORY = '/home/pi/capstone/images/'+ folder_name
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)


def step_motor(_dir):
    GPIO.output(EN_PIN, GPIO.LOW)
    if(_dir == 1) :  # 아래로 가는 것
        GPIO.output(DIR_PIN, GPIO.HIGH)
        for i in range(5000):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0006)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.0006)
        time.sleep(1)
        
    # GPIO LOW 가 올라가는 코드
    elif(_dir == 0):
        GPIO.output(DIR_PIN, GPIO.LOW)
        for i in range(5000):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0006)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.0006)
        time.sleep(1)

def record_video():
    camera.resolution = (1920, 1080)
    camera.start_preview()
    camera.start_recording('video.h264')
    # time.sleep(10)  # 영상 녹화 시간 (초)


class CameraThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        self.camera.resolution = (3280, 2464)  # 원하는 해상도 설정
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
        return image

    def stop(self):
        self.stopped = True


# 이벤트 객체 생성
pause_event = threading.Event()

class SaveThread(threading.Thread):
    def __init__(self):
        self.frame_cnt=0
        threading.Thread.__init__(self)
        self.stopped = False

    def run(self):
        while not self.stopped:
            pause_event.wait()  # 이벤트가 설정될 때까지 대기

            if len(camera_thread.frames)>0 :
                if self.frame_cnt % 2 == 0:     
                    filename = f'frame_{self.frame_cnt//2}.jpg'
                    file_path = os.path.join(SAVE_DIRECTORY,filename)
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
    go_left.ChangeDutyCycle(60)
    go_right.ChangeDutyCycle(60)

    time.sleep(40) # 35초sleep
    
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
        
        # 카메라 쓰레드 시작
        camera_thread = CameraThread()
        camera_thread.start()
        
        save_thread = SaveThread()
        save_thread.start()
        
        pause_event.set()
        
        set_angle(25)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        set_angle(20)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        set_angle(15)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        
        set_angle(10)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        gear_angle(68)
        gear_angle(68)
        set_angle(5)
        car_moving()
        car_stop()
        
        pause_event.clear()
        
        for i in range(0,4):
            step_motor(1)
        
        
        gear_angle(115)
        gear_angle(115)
        
        creds = None
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        # Google Drive API 클라이언트 생성
        drive_service = build('drive', 'v3', credentials=creds)
        
        # 폴더 경로
        folder_path = '/home/pi/capstone/images/object_img'
        
        # 폴더를 zip 파일로 압축
        folder_name = os.path.basename(folder_path)
        zip_path = os.path.join(os.path.dirname(folder_path), folder_name + '.zip')
        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))
        zipf.close()
        
        # zip 파일 삭제
        os.remove(zip_path)
        # 카메라 쓰레드 중지
        
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
        
        
        
        
        
        
        
        

import time
import threading
import picamera
import os
import cv2
import threading
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

STEP_PIN = 22  # arduino 6
DIR_PIN = 27   # arduino 7
EN_PIN = 17    # arduino 8

Car_Wheel_1 = 5    #5
Car_Wheel_2 = 6    #6
Car_Wheel_3 = 19
Car_Wheel_4 = 13
SPEED = 18

SERVO_PIN = 16

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

GPIO.setup(SPEED, GPIO.OUT) 

go_left = GPIO.PWM(SPEED, 1000)
go_left.start(0)


#camera = picamera.PiCamera()

SAVE_DIRECTORY = '/home/pi/capstone/images/'+ time.strftime('%Y%m%d%H%M%S')
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
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.frames = []
        self.stopped = False

    def run(self):
        while not self.stopped:
            ret, frame = self.camera.read()
            time.sleep(0.1)
            if not ret:
                break
            self.frames.append(frame)

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
                if self.frame_cnt % 10 == 0:     
                    filename = f'frame_{self.frame_cnt//10}.jpg'
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
    go_left.ChangeDutyCycle(70)
    GPIO.output(Car_Wheel_3, GPIO.HIGH)
    GPIO.output(Car_Wheel_4, GPIO.LOW)
    time.sleep(29) # 35초sleep
    
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
    

if __name__ == '__main__':
    try:
        
        # 카메라 쓰레드 시작
        camera_thread = CameraThread()
        camera_thread.start()
        
        save_thread = SaveThread()
        save_thread.start()
        
        pause_event.set()
        
        set_angle(90)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        
        set_angle(100)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        set_angle(110)
        car_moving()
        car_stop()
        pause_event.clear()
        step_motor(0)
        pause_event.set()
        
        set_angle(120)
        car_moving()
        car_stop()
        save_thread.clear()
        #step_motor(0)
        #save_thread.restart()
        
        
        
        # 카메라 쓰레드 중지
        camera_thread.stop()
        camera_thread.join()
        
        save_thread.stop()
        save_thread.join()
        '''


        
        # 저장된 프레임들을 파일로 저장
        for i, frame in enumerate(camera_thread.frames):
            if i%10 == 0:  
              filename = f'frame_{i}.jpg'
              file_path = os.path.join(SAVE_DIRECTORY,filename)
              cv2.imwrite(file_path, frame)
        '''
        
        step_motor(1)
        step_motor(1)
        step_motor(1)
        #step_motor(1)
        
        
    except KeyboardInterrupt:
        
        GPIO.output(EN_PIN, GPIO.HIGH)
        GPIO.cleanup()
        

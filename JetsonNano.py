import serial
import datetime
import time
import busio
from board import SCL, SDA
import argparse

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685

# 함수 logging 정의
def logging(filename):
    # I2C 버스 인터페이스 생성
    i2c_bus = busio.I2C(SCL, SDA)

    # PCA9685 모듈 인스턴스 생성
    pca = PCA9685(i2c_bus)

    # PWM 주파수 설정
    pca.frequency = 90

    # 서보와 스로틀의 초기 위치 설정
    left = 0x1B30
    center = 0x2380
    right = 0x2E60
    forward = 0x2D40
    stop = 0x2140
    backward = 0x1A70

    pca.channels[0].duty_cycle = center
    pca.channels[1].duty_cycle = stop

    # 로그 파일 열기
    f = open(filename, 'w')

    # 시리얼 포트 설정
    with serial.Serial('/dev/ttyACM0', 9600, timeout=10) as ser: # 시리얼 포트 열기
        start = input('Do you want to start logging? ')[0]  # 사용자 입력 대기
        if start in 'yY':
            ser.write(bytes('YES\n', 'utf-8'))  # 'YES' 메시지를 시리얼 포트로 보내기
            while True:
                ser_in = ser.readline().decode('utf-8')  # 시리얼 포트에서 데이터 읽기
                print(ser_in)  # 데이터 출력
                f.write("{} {}".format(datetime.datetime.now(), ser_in))  # 로그 파일에 날짜, 시간 및 데이터 기록
                print("{} {}".format(datetime.datetime.now(), ser_in), end='')

                # 서보 및 스로틀 위치 계산
                steer = int(ser_in.split(' ')[2].split('/')[0])
                throttle = int(ser_in.split(' ')[5].split('/')[0])

                if int(steer) <= 1000:
                    steer = int(0x2380)
                elif int(steer) <= 1444:
                    steer = int(((0x2380 - 0x1B30) / (1444 - 1108)) * (steer - 1444) + 0x2380)
                elif int(steer <= 2000):
                    steer = int(((0x2E60 - 0x2380) / (1888 - 1444)) * (steer - 1444) + 0x2380)
                else:
                    steer = int(center)

                if int(throttle) <= 1000:
                    throttle = int(0x2140)
                elif int(throttle) >= 1352:
                    throttle = int(((0x2D40 - 0x2140) / (1840 - 1352)) * (throttle - 1352) + 0x2140)
                else:
                    throttle = int(((0x2140 - 0x1A70) / (1352 - 1076)) * (throttle - 1352) + 0x2140)

                pca.channels[0].duty_cycle = steer  # 서보 위치 설정
                pca.channels[1].duty_cycle = throttle  # 스로틀 위치 설정

    f.close()  # 로그 파일 닫기

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('log_file_name', metavar='F', type=str, nargs=1, help="log file's name")
    args = parser.parse_args()
    logging(args.log_file_name[0])  # 명령줄에서 전달된 파일 이름을 사용하여 logging 함수 호출

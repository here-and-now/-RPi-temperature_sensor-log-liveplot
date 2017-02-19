import os
import time
import datetime
import csv
import pandas as pd
import numpy as np
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)







os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

temp_sensor = '/sys/bus/w1/devices/10-0008030a4c24/w1_slave'

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()

    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_celsius = float(temp_string) / 1000
        
        log_temp(temp_celsius)
            
        #return temp_celsius

def log_temp(temp):
    with open('temp_log.csv', 'a', newline='') as csvfile:
            temp_log = csv.writer(csvfile, delimiter='\t',quoting = csv.QUOTE_NONE, escapechar='\\')
            temp_log.writerow([datetime.datetime.now().strftime('%Y-%m-%d')] +
                              [datetime.datetime.now().strftime('%H:%M:%S')] +
                              [temp])

def animate(i):
    read_temp()

    df = pd.read_csv('temp_log.csv', delimiter='\t', index_col = 0)


    xar = [datetime.datetime.strptime(time, '%H:%M:%S').time() for time in df['Time'].values]
    yar = df['Temperature'].values

    regsteps = 20
    m, b= np.polyfit(np.arange(regsteps), df['Temperature'].tail(regsteps), 1)
    led_reg(m)

    ax1.clear()
    ax1.plot(xar, yar)

def led_reg(slope):

    if(slope > 0):
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(15, GPIO.LOW)
    if(slope < 0):
        GPIO.output(11, GPIO.LOW)
        GPIO.output(15, GPIO.HIGH)
        


fig = plt.figure('Temperature')
ax1 = fig.add_subplot(111)



ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

    

import tkinter as tk
import threading
import matplotlib.pyplot as plt
import pyfirmata
import time
import numpy as np

plt.close('all')

flag_running = False
flag_exiting = False

root = tk.Tk()
global Database
Database=r'C:\Users\Sten\Documents\EI\2020-2021\EI\A_final_project\Datadata.npz'

# The acquisition is divided into 3 main parts;
# 1) Measuring
#   1.1) Initialisation
#   1.2) Data-acquisition
# 2) Buttons
# 3) Post measuring

#1) Measuring
#   1.1) Initialisation
def measure():
    global flag_running
    global flag_exiting
    global Database
# basic arduino-initiation
    time.sleep(1)
    arduino = pyfirmata.ArduinoNano('COM8')
    time.sleep(1)
    it = pyfirmata.util.Iterator(arduino)
    it.start()
# naming all variables and types of data
    data_gain1 = [[0.,0.,0.]]
    data_gain10 = [[0.,0.,0.]]
    data_gain100 = [[0.,0.,0.]]
    ttime = [[0.,0.,0.]]
    small_delay=0.1
    long_delay=1
# defining in- and outputs
    supplyRED   = arduino.get_pin('d:10:o')
    supplyBLUE  = arduino.get_pin('d:9:o')
    supplyGREEN = arduino.get_pin('d:8:o')
    supplyBUZZER= arduino.get_pin('d:2:o')

    ai0 = arduino.get_pin('a:0:i')
    ai1 = arduino.get_pin('a:1:i')
    ai2 = arduino.get_pin('a:2:i')

    start = time.time()

    ii=0
    while (True):
#       1.2) Data acquisition
        if (flag_running == True):
            time.sleep(long_delay)
            data_gain1=np.append(data_gain1,[[0,0,0]],axis=0)
            data_gain10=np.append(data_gain10,[[0,0,0]],axis=0)
            data_gain100=np.append(data_gain100,[[0,0,0]],axis=0)
            ttime=np.append(ttime,[[0,0,0]],axis=0)
            time.sleep(small_delay)
            for jj in range(3):
                if      jj==0:     supply=supplyBLUE
                elif    jj==1:     supply=supplyGREEN
                elif    jj==2:     supply=supplyRED
                supply.write(1)
                time.sleep(0.2)
                data_gain1[ii,jj]=ai2.read()
                time.sleep(0.2)
                data_gain10[ii,jj]=ai0.read()
                time.sleep(0.2)
                data_gain100[ii,jj]=ai1.read()
                time.sleep(0.2)
                ttime[ii,jj]=time.time()-start
                supply.write(0)
            np.savez(Database,data_gain1,data_gain10,data_gain100,ttime,start,time.time())

            if (data_gain1[ii,0]>=1 or (time.time()-start) > 40000):
                for buz in range(4):
                    supplyBUZZER.write(1)
                    time.sleep(1)
                    supplyBUZZER.write(0)
                    time.sleep(0.1)
                kill()
            ii+=1

        if (flag_exiting == True):
            supply.write(0)
            time.sleep(small_delay)
            arduino.sp.close()
            return

    supply.write(0)
    time.sleep(small_delay)
    arduino.sp.close()

 #Buttons
def switchon():
    global flag_running
    flag_running = True
    print ('on')

def switchoff():
    global flag_running
    flag_running = False
    print ('pause')

def kill():
    global flag_exiting
    flag_exiting = True
    root.destroy()

thread = threading.Thread(target=measure)
thread.start()

onbutton = tk.Button(root, text = "ON", command = switchon)
onbutton.pack()
offbutton =  tk.Button(root, text = "PAUSE", command = switchoff)
offbutton.pack()
killbutton = tk.Button(root, text = "KILL", bg='red', command = kill)
killbutton.pack()

root.mainloop()

#POST-MEASURING
tmp=np.load(Database)
data_gain1=tmp['arr_0']
data_gain10=tmp['arr_1']
data_gain100=tmp['arr_2']
ttime=tmp['arr_3']

plt.plot(ttime[:-1,0],data_gain1[:-1,0],'b--o',
         ttime[:-1,1],data_gain1[:-1,1],'g--o',
         ttime[:-1,2],data_gain1[:-1,2],'r--o')
plt.ylabel('Voltage (in V)')
plt.xlabel('time (in s)')
plt.title('Intensity per colour with Gain 1')
plt.show()

plt.plot(ttime[:-1,0],data_gain10[:-1,0],'b--o',
         ttime[:-1,1],data_gain10[:-1,1],'g--o',
         ttime[:-1,2],data_gain10[:-1,2],'r--o')
plt.ylabel('Voltage (in V)')
plt.xlabel('time (in s)')
plt.title('Intensity per colour with Gain 10')
plt.show()

plt.plot(ttime[:-1,0],data_gain100[:-1,0],'b--o',
         ttime[:-1,1],data_gain100[:-1,1],'g--o',
         ttime[:-1,2],data_gain100[:-1,2],'r--o')
plt.ylabel('Voltage (in V)')
plt.xlabel('time (in s)')
plt.title('Intensity per colour with Gain 100')
plt.show()

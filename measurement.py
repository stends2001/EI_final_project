# Obviously, I chose option2 to take as a basis. I changed the order a little bit
# such that it was more logical for me and I changed some variables as well.
import tkinter as tk
import threading
import matplotlib.pyplot as plt
import pyfirmata
import time
import numpy as np

plt.close('all')

flag_running = False                                                            # running = continue measurement
flag_exiting = False                                                            # exiting = discontinue measurement

root = tk.Tk()                                                                  # create an interactive window
global Database                                                                 # can be used inside loops
Database=r'C:\Users\Sten\Documents\EI\2020-2021\EI\A_final_project\Datadata.npz'# place to store the data. Makes plotting much easier

# The acquisition is divided into 3 main parts;
# 1) Measuring
#   1.1) Initialisation
#   1.2) Data-acquisition
# 2) Buttons
# 3) Post measuring

#1) Measuring
#   1.1) Initialisation
def measure():
    global flag_running                                                         # because we defined the variable before this loop, we can only use it by naming it a global (rather than
    global flag_exiting                                                         # a local) variable
    global Database
# basic arduino-initiation
    time.sleep(1)
    arduino = pyfirmata.ArduinoNano('COM8')
    time.sleep(1)
    it = pyfirmata.util.Iterator(arduino)
    it.start()
# naming all variables and types of data
    data_gain1 = [[0.,0.,0.]]                                                   # for gain = 1, ai2
    data_gain10 = [[0.,0.,0.]]                                                  # for gain = 10, ai0
    data_gain100 = [[0.,0.,0.]]                                                 # for gain = 100, ai1
    ttime = [[0.,0.,0.]]                                                        # mind the ttime, this because "time" is a command and therefore gets mixed up when calling an array "time"
    small_delay=0.1
    long_delay=1
# defining in- and outputs
    supplyRED   = arduino.get_pin('d:10:o')
    supplyBLUE  = arduino.get_pin('d:9:o')
    supplyGREEN = arduino.get_pin('d:8:o')

    ai0 = arduino.get_pin('a:0:i')                                              # 10x gain
    ai1 = arduino.get_pin('a:1:i')                                              # 100x gain
    ai2 = arduino.get_pin('a:2:i')                                              # 1x gain

    start = time.time()                                                         # start of time (axis)

    ii=0                                                                        # measurement number
    while (True):                                                               # this loop is run infinitely until further notice (pressing either of two buttons "kill" or "pause")
#       1.2) Data acquisition
        if (flag_running == True):                                              # this is true after pressing "start" until pressing "pause"
            time.sleep(long_delay)
            data_gain1=np.append(data_gain1,[[0,0,0]],axis=0)                   # appending vertically. Before every measurement, the array gets an additional row. This is slower than defining the 
            data_gain10=np.append(data_gain10,[[0,0,0]],axis=0)                 #size of the matrix beforehand, but of course we do not know the amount of measurements at the start!
            data_gain100=np.append(data_gain100,[[0,0,0]],axis=0)
            ttime=np.append(ttime,[[0,0,0]],axis=0)
            time.sleep(small_delay)
            for jj in range(3):
                if      jj==0:     supply=supplyBLUE                            # Within one round of measurements, the supply switches. This increases speed.
                elif    jj==1:     supply=supplyGREEN
                elif    jj==2:     supply=supplyRED
                supply.write(1)
                time.sleep(0.2)                                                 # I experimented a bit with multiple values of the sleeping-time, but 0.2 seemed to be the most efficient. This doesn't
                data_gain1[ii,jj]=ai2.read()                                    #take too long and is able to reduce the noise.
                time.sleep(0.2)
                data_gain10[ii,jj]=ai0.read()
                time.sleep(0.2)
                data_gain100[ii,jj]=ai1.read()
                time.sleep(0.2)
                ttime[ii,jj]=time.time()-start                                  # it times this moment, but we need to subtract the previous timing in order to get the right values
                supply.write(0)
            np.savez(Database,data_gain1,data_gain10,data_gain100,ttime,start,time.time())#update the data every single time the while loop is run, and thus after each measurement
            ii+=1                                                               # increasing measurement number. Naturally, only when the measurement is actually run (flag_running = TRUE)

        if (flag_exiting == True):                                              # this code is run when kill-button is pressed
            supply.write(0)
            time.sleep(small_delay)
            arduino.sp.close()
            return                                                              # quits (while(TRUE) loop)

    supply.write(0)
    time.sleep(small_delay)
    arduino.sp.close()

#Buttons
def switchon():
    global flag_running                                                         # Again, we need a global variable to use inside loops
    flag_running = True                                                         # such that, upon rerunning "measure()" the loop of the actual measurement is run
    print ('on')

def switchoff():
    global flag_running
    flag_running = False                                                        # upon rerunning "measure()" the loop of the actual measurement is NOT run
    print ('pause')

def kill():
    global flag_exiting
    flag_exiting = True                                                         # upon rerunning "measure()" the loop of the actual measurement is NOT run, and arduino is closed such that any more measuring is not possible
    root.destroy()                                                              # destroys the possibility to press buttons

thread = threading.Thread(target=measure)                                       # Upon pressing a button, a variable will change (flag_running or flag_exiting) and the target (= measure)
thread.start()

onbutton = tk.Button(root, text = "ON", command = switchon)                     # pressing this button results in command switchon, switchon-function will be run
onbutton.pack()                                                                 # giving the button a place in the window
offbutton =  tk.Button(root, text = "PAUSE", command = switchoff)               # pressing this button results in command switchoff, switchoff-function will be run
offbutton.pack()                                                                # giving the button a place in the window
killbutton = tk.Button(root, text = "KILL", bg='red', command = kill)           # pressing this button results in command kill, kill-function will be run
killbutton.pack()                                                               # giving the button a place in the window

root.mainloop()

#POST-MEASURING 
tmp=np.load(Database)                                                           # Database is stores as a couple of "positions". The order is given in line 17
data_gain1=tmp['arr_0']
data_gain10=tmp['arr_1']
data_gain100=tmp['arr_2']
ttime=tmp['arr_3']

plt.plot(ttime[:-1,0],data_gain1[:-1,0],'b--o',                                 # for small measurements, it was easier to see circles than plusses. That's why I changed this
         ttime[:-1,1],data_gain1[:-1,1],'g--o',                                 # I also chose to do 3 seperate plots, just to make more room
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

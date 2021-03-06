import matplotlib.pyplot as plt
import pyfirmata
import time
import numpy as np

time.sleep(1)
arduino = pyfirmata.ArduinoNano('COM8')
time.sleep(1)
it = pyfirmata.util.Iterator(arduino)
it.start()

small_delay=0.1
long_delay=1

supplyRED   = arduino.get_pin('d:10:o')
supplyBLUE  = arduino.get_pin('d:9:o')
supplyGREEN = arduino.get_pin('d:8:o')

ai2 = arduino.get_pin('a:2:i')                                                                              # we now only need 1 pin to measure, as we don't use gain

start = time.time()

number_of_measurements=10                                                                                   # also different to previous code. 10 measurements is more than enough
measurement=0                                                                                               # start at 0

data0 = np.zeros((number_of_measurements,3))                                                                # data per colour when LED is on
data1 = np.zeros((number_of_measurements,1))                                                                # data when LED is off, then of course we only need 1 array
ttime = np.zeros((number_of_measurements,4))                                                                # 4 types of measurements, therefore, 4 columns needed for measurement of time                                                               

for measurement in range(number_of_measurements):
    time.sleep(long_delay)
    time.sleep(small_delay)
    for jj in range(4):
        if      jj==0:     supply=supplyBLUE                                                                # Within one round of measurements, the supply switches. This increases speed
        elif    jj==1:     supply=supplyGREEN
        elif    jj==2:     supply=supplyRED
        if (jj<=2):
            supply.write(1)
            time.sleep(small_delay)
            data0[measurement,jj]=ai2.read()
            time.sleep(small_delay)
            ttime[measurement,jj]=time.time()-start
            supply.write(0)
            time.sleep(long_delay)
        if (jj==3):                                                                                         # only te last within each round of measurements is done without a LED turned on.
            supply.write(0)
            time.sleep(small_delay)
            data1[measurement, 0]=ai2.read()
            time.sleep(small_delay)
            ttime[measurement, jj]=time.time()-start

supply.write(0)
time.sleep(small_delay)
arduino.sp.close()


plt.plot(ttime[:-1,0],data0[:-1,0],'b-o',
         ttime[:-1,1],data0[:-1,1],'g-o',
         ttime[:-1,2],data0[:-1,2],'r-o')
plt.ylabel('Voltage (in V)')
plt.xlabel('time (in s)')
plt.title('Light intensity per colour at gain 1')
plt.show()

plt.plot(ttime[:-1,3],data1[:-1,0],'k--')
plt.ylabel('Voltage (in V)')
plt.xlabel('time (in s)')
plt.title('Background light intensity at gain 1')
plt.show()

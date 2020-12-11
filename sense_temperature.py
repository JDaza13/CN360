import datetime as dt
import concurrent.futures

temp_device_id = '28-01193a3ed4e7'
temp_device_path = '/sys/bus/w1/devices/'+temp_device_id+'/w1_slave'
TEMP_READ_FREQ_SEC = 5

temp_value = '0'

def get_temp(dev_file):
    global temp_value
    f = open(dev_file,"r")
    contents = f.readlines()
    f.close()
    index = contents[-1].find("t=")
    if index != -1 :
        temperature = contents[-1][index+2:]
        cels =float(temperature)/1000
        temp_value = str(cels)
    
try:
    checkpoint = dt.datetime.now()
    while True:
        time_diff = (dt.datetime.now() - checkpoint).seconds
        if time_diff > TEMP_READ_FREQ_SEC:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(get_temp, temp_device_path)
            checkpoint = dt.datetime.now()
        print(temp_value)
except KeyboardInterrupt: 
    print('exit')

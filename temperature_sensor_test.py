import asyncio

temp_device_id = '28-01193a3ed4e7'
temp_value = '0'
counter = 0

async def run_counter():
    global counter
    await asyncio.sleep(1)    
    counter = counter + 1

async def get_temp(dev_file):
    f = await open(dev_file,"r")
    contents = f.readlines()
    f.close()
    index = contents[-1].find("t=")
    if index != -1 :
        temperature = contents[-1][index+2:]
        temp_value = float(temperature)/1000
        return cels
    
async def main():    
    try:
        while True:
            #loop.run_until_complete(print(get_temp('/sys/bus/w1/devices/'+temp_device_id+'/w1_slave')))
            loop = asyncio.get_event_loop()
            counter_task = loop.create_task(run_counter())
            await counter_task
            print(counter)
    except KeyboardInterrupt: 
        print('exit')

asyncio.run(main())
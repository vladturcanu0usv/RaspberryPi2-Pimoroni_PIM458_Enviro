#!/usr/bin/env python3

##### Importing Libraries #####
import requests
import colorsys
import sys
import time
import os
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
    
except ImportError:
    import ltr559
    
import logging
from subprocess import PIPE, Popen
from bme280 import BME280
from pms5003 import PMS5003
from pms5003 import ReadTimeoutError as pmsReadTimeoutError
from pms5003 import SerialTimeoutError
from enviroplus import gas

##### Importing Libraries #####

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s", 
    level=logging.INFO, 
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info
(
    """combined.py - Displays readings from all of Enviro plus' sensorsPress 
    Ctrl+C to exit!"""
)


terminal_width = os.get_terminal_size().columns

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()
# PMS5003 particulate sensor
pms5003 = PMS5003()
time.sleep(1.0)

#url = "https://www.dgnet.ro:5000/data/add"
url = "localhost:5000"
delay = 4  # Debounce the proximity tap
mode = 0  # The starting mode
last_page = 0
light = 1

message = ""

variables = ["temperature","pressure","humidity","light","oxidised","reduced","nh3","pm1","pm25","pm10"]
units = ["C","hPa","%","Lux","kO","kO","kO","ug/m3","ug/m3","ug/m3"]

values = {var: [0] * 60 for var in variables}

# Saves the data to be used in the graphs later and prints to the log
#def save_data(idx, data):
#    variable = variables[idx]
    # Maintain length of list
 #   values[variable] = values[variable][1:] + [data]
  #  unit = units[idx]
 #   message = f"{variable[:4]}: {data:.1f} {unit}"
 #   logging.info(message)
    
# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index("=") + 1:output.rindex("'")])


from datetime import datetime, timedelta


def add_datum_senzor(Senzor_Data, data_ora, valoare_tip_data, index):
    data_ora = data_ora.isoformat()
    datum = [
        data_ora ,
        variables[index] ,
        valoare_tip_data,
        units[index] 
    ]
    Senzor_Data[index] = datum





def main():
    factor = 2.25
    cpu_temps = [get_cpu_temperature()] * 5
    
    delay = 4  # Debounce the proximity tap.  0.5 default value
    mode = 10    # The starting mode
    last_page = 0
    
    
    
    Arithm_Mean_Divider = 3600 / delay
    
    current_datetime = datetime.now()
    # Format date and time
    
    Initial_DataTime = current_datetime

    one_hour = timedelta(hours = 1)
    five_minute = timedelta(minutes = 5)
    one_minute = timedelta(minutes = 1)
    
    # Setting Arithm_Mean Dictionary
    # Senz_D_Arithm_Mean = {}
    
    
    
    print("Press CTRL+C to exit")
    
    while True:
        if ( current_datetime - Initial_DataTime < one_minute ):
            
            current_datetime = datetime.now()
            # Format date and time
            
        
            Senzor_Data = {}  # resseting this dictionary after one hour
        
            try:
                
                    
                proximity = ltr559.get_proximity()
                if proximity > 1500 and time.time() - last_page > delay:
                    mode += 1
                    mode %= (len(variables) + 1)
                    last_page = time.time()
                    
                if mode == 10:
                    # Everything on one screen
                    cpu_temp = get_cpu_temperature()
                    # Smooth out with some averaging to decrease jitter
                    cpu_temps = cpu_temps[1:] + [cpu_temp]
                    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
                    raw_temp = bme280.get_temperature()
                    raw_data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 0 )
                   # save_data(0, raw_data)
                    raw_data = bme280.get_pressure()
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 1 )
                   # save_data(1, raw_data)
                    raw_data = bme280.get_humidity()
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 2 )
                   # save_data(2, raw_data)
                    if proximity < 10:
                        raw_data = ltr559.get_lux()
                    else:
                        raw_data = 1
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 3 )
                  #  save_data(3, raw_data)
                    gas_data = gas.read_all()
                    add_datum_senzor( Senzor_Data, current_datetime, gas_data.oxidising / 1000, 4 )
                   # save_data(4, gas_data.oxidising / 1000)
                    add_datum_senzor( Senzor_Data, current_datetime, gas_data.reducing / 1000, 5 )
                   # save_data(5, gas_data.reducing / 1000)
                    add_datum_senzor( Senzor_Data, current_datetime, gas_data.nh3 / 1000, 6 )
                   # save_data(6, gas_data.nh3 / 1000)
                    pms_data = None
                    try:
                        pms_data = pms5003.read()
                    except (SerialTimeoutError, pmsReadTimeoutError):
                        logging.warning("Failed to read PMS5003")
                    else:
                        add_datum_senzor( Senzor_Data, current_datetime, float(pms_data.pm_ug_per_m3(1.0)), 7 )
                        add_datum_senzor( Senzor_Data, current_datetime, float(pms_data.pm_ug_per_m3(2.5)), 8 )
                        add_datum_senzor( Senzor_Data, current_datetime, float(pms_data.pm_ug_per_m3(10)), 9 )
                        
                  #      save_data(7, float(pms_data.pm_ug_per_m3(1.0)))
                  #      save_data(8, float(pms_data.pm_ug_per_m3(2.5)))
                  #      save_data(9, float(pms_data.pm_ug_per_m3(10)))
                        """ for i in range(10):
                            value_SzData = Senzor_Data[i]
                            value_Arith_SZData = Senz_D_Arithm_Mean[i]
                            value_Arith_SZData[2] += value_SzData[2] # valoare_tip_data
                            Senz_D_Arithm_Mean[i] = value_Arith_SZData """
                    response = requests.post(url, json=Senzor_Data)
                    print(f"Server response: {response.text}")
                        
                
                print("_" * terminal_width)
                time.sleep(delay)
                for key, value in Senzor_Data.items():
                    print(f"ID{key} -> Data {value[0]}, Tip: {value[1]}, Valoare: {value[2]} {value[3]}")
                print(Senzor_Data)

                print(f"Time difference {current_datetime - Initial_DataTime}")
                      
                    
            # Exit cleanly
            except KeyboardInterrupt:
                sys.exit(0)
        else:
            Initial_DataTime = current_datetime
            """ if ( Arithm_Mean_Divider != 0):
                for index in range(10):
                    #Senz_D_Arithm_Mean[index][0] = Senz_D_Arithm_Mean[index][0].timestamp()
                    Senz_D_Arithm_Mean[index][2] = Senz_D_Arithm_Mean[index][2] / Arithm_Mean_Divider
                    valoare_tip_data = round ( Senz_D_Arithm_Mean[index][2], 4)
                    Senz_D_Arithm_Mean[index][2] = valoare_tip_data """
            
                
    
            
            """ else:
                print("Can't find the mean number because it can't be divided by 0!!!") """
    
    
if __name__ == "__main__":
    main()

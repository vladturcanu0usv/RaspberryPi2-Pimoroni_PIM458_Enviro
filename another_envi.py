#!/usr/bin/env python3

##### Importing Libraries #####

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
    datum = {
        "data_ora": data_ora,
        "tip_data": variables[index],
        "valoare_tip_data": valoare_tip_data,
        "unitate_tip_data": units[index]
    }
    Senzor_Data[index] = datum




def main():
    factor = 2.25
    cpu_temps = [get_cpu_temperature()] * 5
    
    delay = 2  # Debounce the proximity tap.  0.5 default value
    mode = 10    # The starting mode
    last_page = 0
    
    CONST_oneHour = 1;
    
    Arithm_Mean_Divider = 3600 / delay
    
    current_datetime = datetime.now()
    # Format date and time
    
    Initial_DataTime = current_datetime

    one_hour = timedelta(hours = 1)
    
    
    # Setting Arithm_Mean Dictionary
    Senz_D_Arithm_Mean = {}
    
    
    
    
    for index in range(10):
        add_datum_senzor(Senz_D_Arithm_Mean, Initial_DataTime + one_hour, 0, index)
    
    
    print("Press CTRL+C to exit")
    
    while True:
        if ( current_datetime - Initial_DataTime < one_hour ):
            
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
                    
                    
                    valur_Tip_Data = list(Senzor_Data[0])
                    
                    
                    Arith_value_Tip_Data = list(Senz_D_Arithm_Mean[0])
                    Arith_value_Tip_Data[2] += valur_Tip_Data[2]
                    
                    Senz_D_Arithm_Mean[variables[0]] += Senzor_Data[variables[0]]
                   # save_data(0, raw_data)
                    raw_data = bme280.get_pressure()
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 1 )
                    Senz_D_Arithm_Mean[variables[1]] += Senzor_Data[variables[1]]
                   # save_data(1, raw_data)
                    raw_data = bme280.get_humidity()
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 2 )
                    Senz_D_Arithm_Mean[variables[2]] += Senzor_Data[variables[2]]
                   # save_data(2, raw_data)
                    if proximity < 10:
                        raw_data = ltr559.get_lux()
                    else:
                        raw_data = 1
                    add_datum_senzor( Senzor_Data, current_datetime, raw_data, 3 )
                    Senz_D_Arithm_Mean[variables[3]] += Senzor_Data[variables[3]]
                  #  save_data(3, raw_data)
                    gas_data = gas.read_all()
                    add_datum_senzor( Senzor_Data, current_datetime, gas_data.oxidising / 1000, 4 )
                    Senz_D_Arithm_Mean[variables[4]] += Senzor_Data[variables[4]]
                   # save_data(4, gas_data.oxidising / 1000)
                    add_datum_senzor( Senzor_Data, current_datetime, gas_data.reducing / 1000, 5 )
                    Senz_D_Arithm_Mean[variables[5]] += Senzor_Data[variables[5]]
                   # save_data(5, gas_data.reducing / 1000)
                    add_datum_senzor( Senzor_Data, current_datetime, gas_data.nh3 / 1000, 6 )
                    Senz_D_Arithm_Mean[variables[6]] += Senzor_Data[variables[6]]
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
                        Senz_D_Arithm_Mean[variables[7]] += Senzor_Data[variables[7]]
                        Senz_D_Arithm_Mean[variables[8]] += Senzor_Data[variables[8]]
                        Senz_D_Arithm_Mean[variables[9]] += Senzor_Data[variables[9]]
                  #      save_data(7, float(pms_data.pm_ug_per_m3(1.0)))
                  #      save_data(8, float(pms_data.pm_ug_per_m3(2.5)))
                  #      save_data(9, float(pms_data.pm_ug_per_m3(10)))
                print
                print("_" * terminal_width)
                time.sleep(delay)
                for key, value in Senzor_Data.items():
                    print(f"ID{key} -> Data {value['data_ora']}, Tip: {value['tip_data']}, Valoare: {value['valoare_tip_data']} {value['unitate_tip_data']}")
                print(f"Len of temp dictionary: {len(Senzor_Data)}")
                      
                    
            # Exit cleanly
            except KeyboardInterrupt:
                sys.exit(0)
        else:
            Initial_DataTime = formatted_datetime
            if ( Arithm_Mean_Divider != 0):
                for index in range(10):
                    Senz_D_Arithm_Mean[variables[index]] = Senz_D_Arithm_Mean[variables[index]] / Arithm_Mean_Divider
            else:
                print("Can't find the mean number because it can't be divided by 0!!!")
    
    
if __name__ == "__main__":
    main()

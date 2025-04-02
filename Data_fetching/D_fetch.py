#!/usr/bin/env python3

##### Importing Libraries #####

import colorsys
import sys
import time
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

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()
# PMS5003 particulate sensor
pms5003 = PMS5003()
time.sleep(1.0)


delay = 0.5  # Debounce the proximity tap
mode = 0  # The starting mode
last_page = 0
light = 1

variables = ["temperature","pressure","humidity","light","oxidised","reduced","nh3","pm1","pm25","pm10"]
units = ["C","hPa","%","Lux","kO","kO","kO","ug/m3","ug/m3","ug/m3"]

values = {var: [0] * 60 for var in variables}

# Saves the data to be used in the graphs later and prints to the log
def save_data(idx, data):
    variable = variables[idx]
    # Maintain length of list
    values[variable] = values[variable][1:] + [data]
    unit = units[idx]
    message = f"{variable[:4]}: {data:.1f} {unit}"
    logging.info(message)
    
# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index("=") + 1:output.rindex("'")])


def main():
    factor = 2.25
    cpu_temps = [get_cpu_temperature()] * 5
    
    delay = 0.5  # Debounce the proximity tap
    mode = 10    # The starting mode
    last_page = 0
    
    try:
        while True:
            if mode == 10:
                        # Everything on one screen
                        cpu_temp = get_cpu_temperature()
                        # Smooth out with some averaging to decrease jitter
                        cpu_temps = cpu_temps[1:] + [cpu_temp]
                        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
                        raw_temp = bme280.get_temperature()
                        raw_data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
                        save_data(0, raw_data)
                        raw_data = bme280.get_pressure()
                        save_data(1, raw_data)
                        raw_data = bme280.get_humidity()
                        save_data(2, raw_data)
                        if proximity < 10:
                            raw_data = ltr559.get_lux()
                        else:
                            raw_data = 1
                        save_data(3, raw_data)
                        gas_data = gas.read_all()
                        save_data(4, gas_data.oxidising / 1000)
                        save_data(5, gas_data.reducing / 1000)
                        save_data(6, gas_data.nh3 / 1000)
                        pms_data = None
                        try:
                            pms_data = pms5003.read()
                        except (SerialTimeoutError, pmsReadTimeoutError):
                            logging.warning("Failed to read PMS5003")
                        else:
                            save_data(7, float(pms_data.pm_ug_per_m3(1.0)))
                            save_data(8, float(pms_data.pm_ug_per_m3(2.5)))
                            save_data(9, float(pms_data.pm_ug_per_m3(10)))
    # Exit cleanly
    except KeyboardInterrupt:
        sys.exit(0)
    
    
    
if __name__ == "__main__":
    main()

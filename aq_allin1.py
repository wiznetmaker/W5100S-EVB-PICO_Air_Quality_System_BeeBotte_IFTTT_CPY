import board
import PM2_5
import aq
import time
import adafruit_dht
import digitalio

#Add PM2.5
PM_test = PM2_5.PM2_5(board.GP4, board.GP5)

#Add air quality
air_q = aq.air_quality(board.GP0, board.GP1)

#Add DHT22
dhtDevice = adafruit_dht.DHT22(board.GP2)

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        print(
            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f, temperature_c, humidity
            )
        )
        #time.sleep(0.5)
        PM1,PM25,PM10 = PM_test.collect_data()
        print ("PM1.0 value = {} ug/m3".format(PM1))
        print ("PM2.5 value = {} ug/m3".format(PM25))
        print ("PM10 value = {} ug/m3".format(PM10))
        time.sleep(1)
        TV0C,CH02,C02 = air_q.collect_data()

        print ("TV0C value = {} ug/m3".format(TV0C))
        print ("CH02 value = {} ug/m3".format(CH02))
        print ("C02 value = {} PPM".format(C02))

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except SyntaxError as error:
        print (error)
        time.sleep(2.0)
        continue
    except TypeError as error:
        print (error)
        time.sleep(0.1)
        continue
    except ValueError as error:
        print (error)
        time.sleep(0.1)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)
    
import board
import PM2_5
import time

PM_test = PM2_5.PM2_5(board.GP4, board.GP5)

while True:
    try:
        PM1,PM25,PM10 = PM_test.collect_data()
        print ("PM1.0 value = {} ug/m3".format(PM1))
        print ("PM2.5 value = {} ug/m3".format(PM25))
        print ("PM10 value = {} ug/m3".format(PM10))
    except TypeError as error:
        time.sleep(0.1)
        continue
    except ValueError as error:
        time.sleep(0.1)
        continue
    
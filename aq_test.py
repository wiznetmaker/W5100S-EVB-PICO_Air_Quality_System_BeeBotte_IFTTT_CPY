import board
import aq
import time

air_q = aq.air_quality(board.GP0, board.GP1)

while True:
    try:
        TV0C,CH02,C02 = air_q.collect_data()
        print ("TV0C value = {} ug/m3".format(TV0C))
        print ("CH02 value = {} ug/m3".format(CH02))
        print ("C02 value = {} PPM".format(C02))
        time.sleep(0.5)
    except TypeError as error:
        time.sleep(0.1)
        print (error)
        continue
    except ValueError as error:
        time.sleep(0.1)
        print (error)
        continue
    except SyntaxError as error:
        time.sleep(0.1)
        print (error)
        continue
    
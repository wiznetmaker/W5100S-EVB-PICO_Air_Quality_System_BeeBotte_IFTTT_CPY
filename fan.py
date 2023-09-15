import board
import digitalio
import time

fan = digitalio.DigitalInOut(board.GP0)
fan.direction = digitalio.Direction.OUTPUT


while True:
    fan.value = True
    #time.sleep(0.1)
    #fan.value = False
    time.sleep(2)
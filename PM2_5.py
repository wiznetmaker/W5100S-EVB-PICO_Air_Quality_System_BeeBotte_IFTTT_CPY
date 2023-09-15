import board
import busio
import time
import gc

class PM2_5:
    
    def __init__(self, TX_pin : pin, RX_pin:pin) -> None:
        self.uart = busio.UART(TX_pin,RX_pin, baudrate = 9600)

    
    def collect_data (self) -> None:
        try:
            self.data  = self.uart.read(32)
            self._check_data()
            PM10 = int.from_bytes((self.data[10].to_bytes(1,'big') + self.data[11].to_bytes(1,'big')),'big')
            PM25 = int.from_bytes((self.data[12].to_bytes(1,'big') + self.data[13].to_bytes(1,'big')),'big')
            PM100 = int.from_bytes((self.data[14].to_bytes(1,'big') + self.data[15].to_bytes(1,'big')),'big')
            gc.collect()
            return PM10, PM25, PM100
        
        except Exception as error:
            raise error
        
    def _check_data(self) -> None:
        check = 0
        self.uart.reset_input_buffer() 
        for i in range (30):
            check = check + self.data[i]
        result = int.from_bytes((self.data[30].to_bytes(1,'big') + self.data[31].to_bytes(1,'big')),'big')
        if result != check:
            raise ValueError ("Data Incorrect")
        
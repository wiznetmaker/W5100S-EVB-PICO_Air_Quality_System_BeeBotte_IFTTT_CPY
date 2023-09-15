import board
import busio
import time
import gc

class air_quality:
    
    def __init__(self, TX_pin : pin, RX_pin:pin) -> None:
        self.uart = busio.UART(TX_pin,RX_pin, baudrate = 9600)
        self.data = {}
        
    def collect_data (self) -> None:
        try:
            for i in range (9):
                self.data[i]  = self.uart.read(1)
            self._check_data()
            TV0C = int.from_bytes((self.data[2] + self.data[3]),'big')
            CH02 = int.from_bytes((self.data[4] + self.data[5]),'big')
            C02 = int.from_bytes((self.data[6] + self.data[7]),'big')
            if TV0C == 0 and CH02 == 0 and C02 == 0:
                raise SyntaxError ("Module not Ready")
            else:
                gc.collect()
                return TV0C, CH02, C02
        
        except Exception as error:
            raise error
        
    def _check_data(self) -> None:
        check = 0
        self.uart.reset_input_buffer() 
        for i in range (8):
            check = check + int.from_bytes(self.data[i],'big')
        final = check.to_bytes(2,'big')
        if final[1].to_bytes(1,'big') != self.data[8]:
            raise ValueError ("Data Incorrect")
        
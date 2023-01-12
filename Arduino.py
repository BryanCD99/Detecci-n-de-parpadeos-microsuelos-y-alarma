import serial,serial.tools.list_ports
import struct
import time
import numpy as np

class ArduinoSerial():
    def __init__(self):
        self.Port = None
        self.Baudrage = 115200
        self.Arduino = serial.Serial()
        self.packer = struct.Struct('>f')
        self.unpacker = struct.Struct('>f')
        self.OpenPort = False
        self.RecivedFloat = 0.0

    def begin(self):
        if self.Port is None:
            return False
        try:
            self.Arduino = serial.Serial(port=self.Port, baudrate=self.Baudrage, timeout=1, write_timeout=1)
            time.sleep(2)
            self.OpenPort = True
            return True
        except:
            return False

    def begin(self, port):
        self.Port = port

        if self.Port is None:
            return False
        try:
            self.Arduino = serial.Serial(port=self.Port, baudrate=self.Baudrage, timeout=1, write_timeout=1)
            time.sleep(2)
            self.OpenPort = True
            return True
        except:
            return False

    def begin(self, port, baudrage):
        self.Port = port
        self.Baudrage = baudrage
        if self.Port is None or self.Port is None:
            return False
        try:
            self.Arduino = serial.Serial(port=self.Port, baudrate=self.Baudrage, timeout=1, write_timeout=1)
            time.sleep(2)
            self.OpenPort = True
            return True
        except:
            return False
    def Close(self):
        self.Arduino.close()
        self.OpenPort = False

    def SendFloat(self, Data):
        if self.OpenPort is False:
            return False
        FDato = float(Data)
        packed_data = self.packer.pack(FDato)
        self.Arduino.write(packed_data)
        return True

    def SendChar(self, Data):
        # Si el puerto serial no esta abierto, entonces se retorna False
        if self.OpenPort is False:
            return False
        # Se envia un caracter codificado en utf-8
        self.Arduino.write(Data.encode('utf-8'))
        return True

    def puertos_seriales(self):
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        #print(myports)
        usb_port_list = [p[0] for p in myports]
        return usb_port_list

    def ReadSingleFloat(self):
        # Si el puerto serial no esta abierto, entonces se retorna None
        if self.OpenPort is False:
            return None
        # Si aun no se han recibido 4 nuevos bytes  en el buffer para leer, se retorna el ultimo numero almacenado en memoria
        if self.Arduino.in_waiting < 4:
            return self.RecivedFloat
        # Si hay 4 bytes en el buffer entonces se procesan y se convierten a float32
        currentBytes = self.Arduino.read(4)
        self.RecivedFloat = float(str(np.float32(self.unpacker.unpack(currentBytes)[0])))
        return self.RecivedFloat


from micropython import const
from time import sleep_ms
import framebuf,ustruct
#屏幕方向旋转需要使用fb-boost的2023年3月以后的固件
class EPD(framebuf.FrameBuffer):   
    def __init__(self, spi, cs, dc, rst, busy, rot=0): 
        self.EPD_WHITE  = const(0)
        self.EPD_RED    = const(1)
        self.EPD_BLACK  = const(2)    
        self.spi = spi
        self.cs = cs
        self.cs.init(self.cs.OUT, value=1)
        self.dc = dc
        self.dc.init(self.dc.OUT, value=0)
        if rst is not None:
            self.rst = rst
            self.rst.init(self.rst.OUT, value=0)
        else:
            self.rst = None
        self.busy = busy
        self.busy.init(self.busy.IN)
        self.rot=rot
        self.width  = 200
        self.height = 200            
        self.FULL    = bytearray(b'\x02\x02\x01\x11\x12\x12\x22\x22\x66\x69\x69\x59\x58\x99\x99\x88\x00\x00\x00\x00\xF8\xB4\x13\x51\x35\x51\x51\x19\x01\x00')
        self.PARTIAL = bytearray(b'\x10\x18\x18\x08\x18\x18\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x14\x44\x12\x00\x00\x00\x00\x00\x00')

        self.buffer = bytearray(self.height * self.width//8)
        if self.rot==0:
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB+framebuf.MX+framebuf.MY)
        elif self.rot==1:
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VMSB+framebuf.MV+framebuf.MX)
        elif self.rot==2:
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)
        else:
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VMSB+framebuf.MV+framebuf.MY)
        #madctl 0 MX 1MY 2MV
        self.reset()
        self.wait_until_idle()
        self.write_cmd(0x12, None)
        self.wait_until_idle()
        self.write_cmd(0x0c, b'\xD7\xD6\x9D'); #Booster Soft start Control
        self.write_cmd(0x2C, b'\xA8')    # VCOM Voltage
        self.write_cmd(0x3A, b'\x1A')    #Set dummy line period 3a3b olny in il3820
        self.write_cmd(0x3B, b'\x08')    #Set Gate line width 
        self.write_cmd(0x01, ustruct.pack(">HB", 200-1, 0)); #Driver output control  ### CHANGED x00 to x01 
        self.write_cmd(0x11,b'\x03')
        self.write_cmd(0x44, ustruct.pack(">BB", 0, (200-1)//8)) #Set RAM X - address Start / End position
        self.write_cmd(0x45, ustruct.pack(">HH", 0, (200-1))) #Set Ram Y- address Start / End position 
        self.mode(0)
        
    def mode(self,mode):
        if mode==0:
            self.write_cmd(0x32,self.FULL)    #Write LUT register 
        else:
            self.write_cmd(0x32,self.PARTIAL)

    def write_cmd(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self.write_data(data)

    def write_data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def wait_until_idle(self):
        sleep_ms(1)
        while self.busy.value() == 1:
            sleep_ms(10)

    def reset(self):
        if self.rst is None:
            self.write_cmd(0x12,None)  #SWRESET
        else:
            self.rst(0)
            sleep_ms(10)
            self.rst(1)
        sleep_ms(20)

    def show(self):
        self.write_cmd(0X4E, b'\x00')      #Set RAM X address counter
        self.write_cmd(0X4F, ustruct.pack(">H", 0))   #Set RAM Y address counter
        self.write_cmd(0x24, self.buffer) #Write RAM
        self.write_cmd(0X22, b'\xc4')     #Display Update Control 2
        self.write_cmd(0X20, None)        #Master Activation
        self.write_cmd(0Xff, None)        #NOP
        self.wait_until_idle()

    def sleep(self):
        self.write_cmd(0x10,b'\x01')

        
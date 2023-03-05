import EDP154_IL3820 as epapar
from machine import Pin, SPI,I2C,lightsleep,deepsleep,freq
import machine,time


spi = SPI(2, baudrate=10000000, sck = Pin(26), mosi = Pin(27), miso = Pin(34))

f=0
while True:
    for i in range(4):
        edp = epapar.EPD(spi, cs = Pin(25), dc = Pin(33), rst = Pin(32), busy = Pin(35), rot = i)
        edp.font_load("GB2312-24.fon")
        edp.font_set(0x23,0,1,0)
        print("清屏")
        time.sleep(1)
        edp.fill(edp.EPD_BLACK)
        print("写数据")
        time.sleep(1)
        edp.text("温度:%4.1f℃"%(25.1+i),0,0,edp.EPD_WHITE)
        edp.text("湿度:%4.1fRh"%(25.1+i),0,30,edp.EPD_WHITE)
        edp.text("气压:%5.1fKpa"%(25.1+i),0,60,edp.EPD_WHITE)
        edp.text("方向:%d"%(i),0,90,edp.EPD_WHITE)
        edp.show_bmp("pic/bw%3.3d.bmp"%(f),1,78,120)
        edp.show()
        edp.sleep()
        time.sleep(3)
        f+=1
        if f>59:
            f=0
        





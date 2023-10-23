import random, math, time
from machine import Pin, SPI
import gc9a01

import vga1_bold_16x32 as font

def draw_dot(tft, x,y,c):
    tft.pixel( x,y, c )
    tft.pixel( x+1, y-1, c )
    tft.pixel( x+1, y+1, c )
    tft.pixel( x-1, y+0, c )
    tft.pixel( x+1, y-1, c )

def main():
    spi = SPI(0, baudrate=60_000_000, sck=Pin(6), mosi=Pin(3))
    tft = gc9a01.GC9A01(
        spi,
        240,
        240,
        reset=Pin(4, Pin.OUT),
        cs=Pin(20, Pin.OUT),
        dc=Pin(5, Pin.OUT),
        rotation=2) # 2 == 180 degrees, because of course it does

    tft.init()

    x,y = 0,0
    r = 60
    phi = 0
    tft.fill(0)

    num_trails = 10
    trails = []

    while True:
        # erase oldest trail element
        if len(trails) > num_trails:
            #print("hit num_trails:", x,y)
            xe,ye = trails.pop(0)  # remove oldest element
            #tft.text( font, "!", xe,ye, gc9a01.color565( 0,0,0), gc9a01.color565(0,0,0) )
            tft.pixel( xe,ye, gc9a01.color565( 0,0,0) )

        # draw trail
        for (xt,yt) in trails:
            #print(x,y)
            #tft.text( font, "!", xt,yt, gc9a01.color565( 100,100,0), gc9a01.color565(0,0,0) )
            tft.pixel( xt,yt, gc9a01.color565( 100,100,0) )

        # get new position
        phi += 0.05
        x = 120 + int(r * math.sin( phi ))
        y = 120 + int(r * math.cos( phi ))
        trails.append( (x,y) )

        #tft.text( font, ".", x,y, gc9a01.color565( 10,255,10), gc9a01.color565(0,0,0) )
        tft.pixel( x,y, gc9a01.color565( 10,255,10) )

        time.sleep(0.01)


main()

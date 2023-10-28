# fake_vectorscope1.py -- a little fakey vectorscope in CircuitPython for 2023HackadaySupercon
# 21 Oct 2023 - @todbot / Tod Kurt
# video demo: https://mastodon.social/@todbot/111275574436711965
import time, math, random
import board, busio
import displayio, vectorio
import adafruit_imageload
import gc9a01

displayio.release_displays()

num_trails = 60   # how long are the trails
a = 0.75   # lissajous A
b = 0.33   # lissajous B
r = 60     # extent from from center
phi_inc = 0.05  # how fast to move through lissajous

dw, dh = 240,240  # display dimensions

# Wiring for Pico wired as 2023Supercon badge is wired
tft_clk  = board.GP2
tft_mosi = board.GP3
tft_rst = board.GP4
tft_dc  = board.GP5
tft_cs  = board.GP1 # no, not wired up but display_bus requires it

# wiring for QT Py, should work on any QT Py or XIAO board
# tft_clk  = board.SCK
# tft_mosi = board.MOSI
# tft_rst = board.MISO
# tft_dc  = board.RX
# tft_cs  = board.TX

spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst, baudrate=60_000_000)
display = gc9a01.GC9A01(display_bus, width=dw, height=dh, rotation=0)
#display.auto_refresh = False

main = displayio.Group()
display.root_group = main

pal = displayio.Palette(num_trails+2)
pal[0] = 0   # background
pal[1] = 0x11ff11  # main dot color
for i in range(num_trails):
    pal[2+i] = (0, int(255-(i*255/num_trails)), 0)  # trails colors

# make the grid lines
for i in range(8):
    main.append(vectorio.Rectangle(pixel_shader=pal, width=1, height=dw, x=20 + i*40, y=0, color_index=num_trails-13))
    main.append(vectorio.Rectangle(pixel_shader=pal, width=dh, height=1, x=0, y=20 + i*40, color_index=num_trails-13))

# make the main dot
dot = vectorio.Circle(pixel_shader=pal, radius=4, x=120, y=120, color_index=1)
main.append(dot)

# make the dot trails
dots = displayio.Group()
main.append(dots)
for i in range(num_trails):
    dots.append( vectorio.Circle(pixel_shader=pal, radius=2, x=120,y=120,color_index=num_trails-i) )

x,y = 0,0
phi = 0
dots_pos = []

while True:

    # erase oldest trail element
    if len(dots_pos) > num_trails:
        dots_pos.pop(0)  # remove oldest element

    # draw trail
    for i, (xt,yt) in enumerate(dots_pos):
        dots[i].x = xt
        dots[i].y = yt

    # get new position
    phi += phi_inc
    x = 120 + int(r * math.sin( a*phi ))
    y = 120 + int(r * math.cos( b*phi ))
    dots_pos.append( (x,y) )
    dot.x = x
    dot.y = y

    #display.refresh()
    time.sleep(0.001)

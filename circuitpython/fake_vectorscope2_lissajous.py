# fake_vectorscope2_lissajous.py -- a little fakey vectorscope in CircuitPython for 2023HackadaySupercon
# 21 Oct 2023 - @todbot / Tod Kurt#
# video demo: https://mastodon.social/@todbot/111279891762130663
import time, math, random
import board, busio
import displayio, vectorio
import gc9a01

displayio.release_displays()

num_shades = 20  # how many shades of green
a = 0.75   # lissajous A
b = 0.53   # lissajous B
r = 70     # extent from from center
phi_inc = 0.05
change_time = 5

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

main = displayio.Group()
display.root_group = main

pal = displayio.Palette(num_shades+2)
pal[0] = 0   # background
pal[1] = 0x11ff11  # main dot color
for i in range(num_shades):
    pal[2+i] = (0, int(255-(i*255/num_shades)), 0)  # trails colors
pal.make_transparent(0)

# make the grid lines
for i in range(8):
    main.append(vectorio.Rectangle(pixel_shader=pal, width=1, height=dw, x=20 + i*40, y=0, color_index=num_shades-3))
    main.append(vectorio.Rectangle(pixel_shader=pal, width=dh, height=1, x=0, y=20 + i*40, color_index=num_shades-3))

# make bitmap we'll scribble on
bitmap = displayio.Bitmap(dw,dh, len(pal))
tg = displayio.TileGrid(bitmap, pixel_shader=pal)
main.append(tg)

x,y = 0,0
phi = 0
last_time = time.monotonic()

display.auto_refresh = True

while True:

    # get new position
    phi += phi_inc
    x = 120 + int(r * math.sin( a*phi ))
    y = 120 + int(r * math.cos( b*phi ))

    c = 1  # bright green in the palette
    bitmap[x,y] = c

    time.sleep(0.001)

    if time.monotonic() - last_time > change_time:
        last_time = time.monotonic()
        bitmap.fill(0)  # clear screen
        a = random.uniform(0.2,0.9)
        b = random.uniform(0.2,0.9)
        print("new a,b %.2f %.2f" % (a,b))

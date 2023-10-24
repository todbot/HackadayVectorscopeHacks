# fake_vectorscope3.py -- a little fakey vectorscope in CircuitPython for 2023HackadaySupercon
# 21 Oct 2023 - @todbot / Tod Kurt#
#
import time, math, random
import board, busio
import keypad
import displayio, vectorio, terminalio
import gc9a01
from adafruit_display_text import bitmap_label as label

displayio.release_displays()

num_trails = 55  # how many shades of green
a = 0.75   # lissajous A
b = 0.53   # lissajous B
r = 70     # extent from from center
phi_inc = 0.025
#phi_inc = 0.05
change_time = 5

dw, dh = 240,240  # display dimensions

# Wiring for Pico wired as 2023Supercon badge is wired
tft_clk  = board.GP2
tft_mosi = board.GP3
tft_rst = board.GP4
tft_dc  = board.GP5
tft_cs  = board.GP1 # no, not wired up but display_bus requires it

# set up keys
#keys_arrows = keypad.Keys( (board.GP16, board.GP17, board.GP18, board.GP19),
#                    value_when_pressed=False, pull=True )
keys = keypad.Keys( (board.GP15,),  # hmm adding more pins make display not work?
                    value_when_pressed=False, pull=True )
# set up display
spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst, baudrate=80_000_000)
display = gc9a01.GC9A01(display_bus, width=dw, height=dh, rotation=0)

main = displayio.Group()
display.root_group = main

pal = displayio.Palette(num_trails+2)
pal[0] = 0   # background
pal[1] = 0x11ff11  # main dot color
for i in range(num_trails):
    pal[2+i] = (0, int(255-(i*255/num_trails)), 0)  # trails colors
pal.make_transparent(0)
pal.make_transparent( num_trails )  # make tail of last color transparent

# make the grid lines
grid_color_idx = int(len(pal) * 0.8)
for i in range(8):
    main.append(vectorio.Rectangle(pixel_shader=pal, width=1, height=dw, x=20 + i*40, y=0, color_index=grid_color_idx))
    main.append(vectorio.Rectangle(pixel_shader=pal, width=dh, height=1, x=0, y=20 + i*40, color_index=grid_color_idx))

# make bitmap we'll scribble on
bitmap = displayio.Bitmap(dw,dh, len(pal))
tg = displayio.TileGrid(bitmap, pixel_shader=pal)
main.append(tg)

# labels showing our values
a_text  = label.Label(terminalio.FONT,text="a:%.2f" % a, x=80, y=220, color=0x11aa11)
b_text  = label.Label(terminalio.FONT,text="b:%.2f" %b, x=140, y=220, color=0x11aa11)
main.append(a_text)
main.append(b_text)

x,y = 0,0
phi = 0
last_time = time.monotonic()

trails_pos = []

display.auto_refresh = True

while True:
    # handle keys
    #while key := keys_arrows.events.get():
    #    print("hi",key)

    # erase oldest trail element
    if len(trails_pos) > num_trails:
        trails_pos.pop(0)  # remove oldest element

    # draw trail
    for i, (xt,yt) in enumerate(trails_pos):
        bitmap[xt,yt] = num_trails - i  # palette is arranged in order of brightness

    # move to new position
    phi += phi_inc
    x = 120 + int(r * math.sin( a*phi ))
    y = 120 + int(r * math.cos( b*phi ))

    bitmap[x,y] = 1 # bright green in the palette

    trails_pos.append( (x,y) )

    time.sleep(0.001)

    # if time.monotonic() - last_time > change_time:
    #     last_time = time.monotonic()
    #     bitmap.fill(0)  # clear screen
    #     trails_pos = []
    #     a = random.uniform(0.2,0.9)
    #     b = random.uniform(0.2,0.9)
    #     print("new a,b %.2f %.2f" % (a,b))
    #     a_text.text = "a:%.2f" % a
    #     b_text.text = "b:%.2f" % b



###################################################################

# fake_vectorscope1.py -- a little fakey vectorscope in CircuitPython for 2023HackadaySupercon
# 21 Oct 2023 - @todbot / Tod Kurt
#
import time, math, random
import board, busio
import displayio, vectorio
import gc9a01

displayio.release_displays()

num_trails = 60   # how long are the trails
a = 0.75   # lissajous A
b = 0.33   # lissajous B
r = 60     # extent from from center

dw, dh = 240,240  # display dimensions

# wiring for QT Py, should work on any QT Py or XIAO board
tft_clk  = board.SCK
tft_mosi = board.MOSI

tft_rst = board.MISO
tft_dc  = board.RX
tft_cs  = board.TX

spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst, baudrate=60_000_000)
display = gc9a01.GC9A01(display_bus, width=dw, height=dh, rotation=0)

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
phi_inc = 0.08
dots_pos = []

display.auto_refresh = False
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

    display.refresh()
    #time.sleep(0.001)



##################################################################

# qteye.py - a stand-alone GC9A01 round LCD "eye" on a QTPy
# 23 Oct 2022 - @todbot / Tod Kurt
# Part of circuitpython-tricks/larger-tricks/eyeballs
# also see: https://todbot.com/blog/2022/05/19/multiple-displays-in-circuitpython-compiling-custom-circuitpython/

import time, math, random
import board, busio
import displayio
import adafruit_imageload
import gc9a01

displayio.release_displays()

dw, dh = 240,240  # display dimensions

# load our eye and iris bitmaps
eyeball_bitmap, eyeball_pal = adafruit_imageload.load("imgs/eye0_ball2.bmp")
iris_bitmap, iris_pal = adafruit_imageload.load("imgs/eye0_iris0.bmp")
iris_pal.make_transparent(0)
#eyelid_bitmap = displayio.OnDiskBitmap(open("/imgs/eyelid_spritesheet2.bmp", "rb"))
eyelid_bitmap, eyelid_pal = adafruit_imageload.load("/imgs/eyelid_spritesheet.bmp")
eyelid_sprites = 8 # 16
#eyelid_pal = eyelid_bitmap.pixel_shader
eyelid_pal.make_transparent(1)
# lid_up_bitmap, lid_up_pal = adafruit_imageload.load("imgs/upper.bmp")
# lid_lo_bitmap, lid_lo_pal = adafruit_imageload.load("imgs/upper.bmp")
# lid_up_pal.make_transparent(0)
# lid_lo_pal.make_transparent(0)

# compute or declare some useful info about the eyes
iris_w, iris_h = iris_bitmap.width, iris_bitmap.height  # iris is normally 110x110
iris_cx, iris_cy = dw//2 - iris_w//2, dh//2 - iris_h//2
r = 20  # allowable deviation from center for iris

# wiring for QT Py, should work on any QT Py or XIAO board
tft0_clk  = board.SCK
tft0_mosi = board.MOSI

tft_L0_rst = board.MISO
tft_L0_dc  = board.RX
tft_L0_cs  = board.TX

spi0 = busio.SPI(clock=tft0_clk, MOSI=tft0_mosi)

# class to help us track eye info (not needed for this use exactly, but I find it interesting)
class Eye:
    def __init__(self, spi, dc, cs, rst, rot=0, eye_speed=0.25, twitch=2):
        display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=rst, baudrate=32_000_000)
        display = gc9a01.GC9A01(display_bus, width=dw, height=dh, rotation=rot)
        display.auto_refresh = False
        main = displayio.Group()
        display.root_group = main
        self.display = display
        self.eyeball = displayio.TileGrid(eyeball_bitmap, pixel_shader=eyeball_pal)
        self.iris = displayio.TileGrid(iris_bitmap, pixel_shader=iris_pal, x=iris_cx,y=iris_cy)
        self.lids = displayio.TileGrid(eyelid_bitmap, pixel_shader=eyelid_pal, x=0, y=0, tile_width=240, tile_height=240)
        #self.lid_up = displayio.TileGrid(lid_up_bitmap, pixel_shader=lid_up_pal, x=0, y=0)
        #self.lid_lo = displayio.TileGrid(lid_lo_bitmap, pixel_shader=lid_lo_pal, x=0, y=-30)
        main.append(self.eyeball)
        main.append(self.iris)
        main.append(self.lids)
        #main.append(self.lid_up)
        #main.append(self.lid_lo)
        self.x, self.y = iris_cx, iris_cy
        self.tx, self.ty = self.x, self.y
        self.next_time = time.monotonic()
        self.eye_speed = eye_speed
        self.twitch = twitch
        self.lidpos = 0
        self.lidpos_inc = 1
        self.lid_next_time = 0

    def update(self):
        self.x = self.x * (1-self.eye_speed) + self.tx * self.eye_speed # "easing"
        self.y = self.y * (1-self.eye_speed) + self.ty * self.eye_speed
        self.iris.x = int( self.x )
        self.iris.y = int( self.y ) + 10
        if time.monotonic() > self.next_time:
            t = random.uniform(0.25,self.twitch)
            self.next_time = time.monotonic() + t
            self.tx = iris_cx + random.uniform(-r,r)
            self.ty = iris_cy + random.uniform(-r,r)
        if time.monotonic() > self.lid_next_time:
            self.lid_next_time = time.monotonic() + random.uniform(2,5)
            self.lidpos = self.lidpos + self.lidpos_inc
            self.lids[0] = self.lidpos
            if self.lidpos == 0 or self.lidpos == eyelid_sprites-1:
                self.lidpos_inc *= -1
        self.display.refresh()

# a list of all the eyes, in this case, only one
the_eyes = [
    Eye( spi0, tft_L0_dc, tft_L0_cs,  tft_L0_rst, rot=0),
]

while True:
    for eye in the_eyes:
        eye.update()
        #eye.lid_up.y += 5
        #eye.lid_lo.y += 5

# badge_touchwheel0.py -- try out touchwheel on supercon2023 badge
# 5 Nov 2023 - @todbot / Tod Kurt#
#
import microcontroller
import time, math, random
import board, busio
import displayio, vectorio, bitmaptools
import touchio
import gc9a01
import adafruit_imageload

# overclock
microcontroller.cpu.frequency = 250_000_000

displayio.release_displays()

# config options
change_time = 5  # seconds between different lissajous
num_shades = 20  # how many shades of green
r = 80           # lissajous size
phi_inc = 0.04   # how fast to draw lissajous
a = 0.87 # 0.75   # lissajous A
b = 0.62 # 0.53   # lissajous B

dw, dh = 240,240  # display dimensions

# Wiring for Pico wired as 2023Supercon badge is wired
tft_clk  = board.GP2
tft_mosi = board.GP3
tft_rst = board.GP4
tft_dc  = board.GP5
tft_cs  = board.GP1 # no, not wired up but display_bus requires it

# touchwheel plugged into GND,GP26,GP27,GP28 on side of badge
touch_pins = (board.GP26, board.GP27, board.GP28)

class TouchWheel():
    """Simple capacitive touchweel made from three captouch pads """
    def __init__(self,touch_pins, offset=-0.333/2):
        self.touchins = []
        self.offset = offset # physical design is rotated 1/2 a sector anti-clockwise
        for p in touch_pins:
            touchin = touchio.TouchIn(p)
            self.touchins.append(touchin)

    def pos(self):
        """
        Given three touchio.TouchIn pads, compute wheel position 0-1
        or return None if wheel is not pressed
        """
        a = self.touchins[0]
        b = self.touchins[1]
        c = self.touchins[2]

        # compute raw percentages
        a_pct = (a.raw_value - a.threshold) / a.threshold
        b_pct = (b.raw_value - b.threshold) / b.threshold
        c_pct = (c.raw_value - c.threshold) / c.threshold
        #print( "%+1.2f  %+1.2f  %+1.2f" % (a_pct, b_pct, c_pct), end="\t")

        pos = None
        # cases when finger is touching two pads
        if a_pct >= 0 and b_pct >= 0:  #
            pos = 0 + 0.333 * (b_pct / (a_pct + b_pct))
        elif b_pct >= 0 and c_pct >= 0:  #
            pos = 0.333 + 0.333 * (c_pct / (b_pct + c_pct))
        elif c_pct >= 0 and a_pct >= 0:  #
            pos = 0.666 + 0.333 * (a_pct / (c_pct + a_pct))
            # special cases when finger is just on a single pad.
            # these shouldn't be needed and create "deadzones" at these points
            # so surely there's a better solution
        elif a_pct > 0 and b_pct <= 0 and c_pct <= 0:
            pos = 0
        elif a_pct <= 0 and b_pct > 0 and c_pct <= 0:
            pos = 0.333
        elif a_pct <= 0 and b_pct <= 0 and c_pct > 0:
            pos = 0.666
            # wrap pos around the 0-1 circle if offset puts it outside that range
        return (pos + self.offset) % 1 if pos is not None else None

# config the hardware

touchwheel = TouchWheel(touch_pins)

spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst,
                                 baudrate=80_000_000)
display = gc9a01.GC9A01(display_bus, width=dw, height=dh, rotation=0)

main = displayio.Group()
display.root_group = main

# make colors for traces
pal = displayio.Palette(num_shades+2)
pal[0] = 0   # background, will be transparent
pal[1] = 0x11ff11  # main dot color
for i in range(num_shades):
    pal[2+i] = (0, int(255-(i*255/num_shades)), 0)  # trails colors
pal.make_transparent(0)

# make the grid lines
for i in range(8):
    main.append(vectorio.Rectangle(pixel_shader=pal, width=1, height=dw,
                                   x=20 + i*40, y=0, color_index=num_shades-3))
    main.append(vectorio.Rectangle(pixel_shader=pal, width=dh, height=1,
                                   x=0, y=20 + i*40, color_index=num_shades-3))

# todbot image
tbitmap, tpalette = adafruit_imageload.load("png/todbot005.png")
tpalette.make_transparent(0)
timage = displayio.TileGrid(tbitmap, pixel_shader=tpalette)
main.append(timage) # shows the image

# make bitmap we'll scribble lissajous on
bitmap = displayio.Bitmap(dw,dh, len(pal))
tg = displayio.TileGrid(bitmap, pixel_shader=pal)
main.append(tg)

# make little dot for touchwheel
dot = vectorio.Circle(pixel_shader=pal, radius=8, x=120, y=120, color_index=1)
main.append(dot)

x,y = 0,0
phi = 0
last_time = time.monotonic()
last_touchcheck_time = 0
touch_pos = 0

while True:

    # get new lissajous  position
    phi += phi_inc
    x = 120 + int(r * math.sin( a*phi ))
    y = 120 + int(r * math.cos( b*phi ))

    bitmap[x,y] = 1  # bright green in the palette

    time.sleep(0.001)  # sets the "framerate" effectively

    if time.monotonic() - last_touchcheck_time > 0.03:
        last_touchcheck_time = time.monotonic()
        pos = touchwheel.pos()
        if pos is not None:   # touched!
            #touch_pos = pos * 0.7 + 0.3 * touch_pos  # filter
            touch_pos = pos
            a = 3.14 - (6.28/12) + touch_pos*6.28 # adjust for how touchwheel is mounted
            dot.x = int(120 + 110*math.sin(a))
            dot.y = int(120 + 110*math.cos(a))

    if time.monotonic() - last_time > change_time:
        last_time = time.monotonic()
        bitmap.fill(0)  # clear screend
        phi = 0
        a = random.uniform(0.5,0.9)
        b = random.uniform(0.5,0.8)
        print("new a,b %.2f %.2f %f" % (a,b, phi_inc))

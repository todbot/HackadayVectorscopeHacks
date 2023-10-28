/**
 * Fakey_VectorScope_Lissajous.ino -- fake vectorscope for Hackaday Supercon 2023
 * 22 Oct 2023 - @todbot / Tod Kurt
 */

 #include <Arduino_GFX_Library.h>

Arduino_DataBus *bus = new Arduino_RPiPicoSPI(5 /* DC */, 1 /* CS */, 2 /* SCK */, 3 /* MOSI */, GFX_NOT_DEFINED /* MISO */);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, 4 /* RST */, 0 /* r */, true /* ips */ ); // IPS is set on GC9A01

const int num_trails = 200;  // cannot go over 255
const int change_millis = 5000;

uint8_t r = 70; // radius of lissajous
float a = 0.6;
float b = 0.3;
float phi = 0;
float phi_inc = 0.1;

uint8_t x, y;
uint8_t dot_size = 2;

// our very cheezy circular buffer storing past positions
int trails_x[num_trails];
int trails_y[num_trails];
int trails_pos = 0;

uint32_t last_millis;

void setup() {
  Serial.begin(115200);
  bus->begin(80000000);
  if (!gfx->begin()){
    Serial.println("gfx->begin() failed!");
  }
  gfx->fillScreen(BLACK);
}

void loop() {
  gfx->startWrite();

  // draw grid lines
  for( int i=0; i< 7; i++) {
    uint8_t d = 20 + i*40;
    gfx->drawLine( 0, d,  239, d, gfx->color565(0, 44, 0));
    gfx->drawLine( d, 0,  d, 239, gfx->color565(0, 44, 0));
  }
  gfx->endWrite();

  gfx->startWrite();
  gfx->fillCircle(x,y, dot_size, BLACK);  // erase last position

  // compute new position
  x = 120 + r * sin( a*phi );
  y = 120 + r * cos( b*phi );
  phi += phi_inc;

  // save new position
  trails_x[ trails_pos ] = x;
  trails_y[ trails_pos ] = y;
  trails_pos = (trails_pos+1) % num_trails;

  // draw new position
  int16_t c = gfx->color565(0x11, 0xff, 0x11);
  gfx->fillCircle(x, y, dot_size, c);

  // draw trails
  uint8_t ltx=x, lty=y; // last tx & ty for line drawing
  for(int i=0; i<num_trails; i++) {
    int ii = (trails_pos + i) % num_trails;   // very cheezy FIFO buffer
    uint8_t tx = trails_x[ii];
    uint8_t ty = trails_y[ii];
    uint8_t gg = (i*(255/num_trails));
    c = gfx->color565(0, gg, 0);
    gfx->drawLine(tx,ty, ltx, lty, c);
    ltx = tx; lty = ty;
  }
  gfx->endWrite();

  if ((millis() - last_millis) > change_millis ) {
    last_millis = millis();
    //gfx->fillScreen(BLACK);
    a = 0.2 + 0.7*random(100)/100.0;
    b = 0.2 + 0.7*random(100)/100.0;
  }

  // delay(30);

}

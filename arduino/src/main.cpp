#include <FastLED.h>

#define LED_PIN_MAIN 6
#define LED_PIN_SECONDARY 3
#define NUM_LEDS_MAIN 46
#define NUM_LEDS_SECONDARY 14
#define BRIGHTNESS 255
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB
#define HALF_LEDS (NUM_LEDS_MAIN / 2)

CRGB previousFullColor = CRGB::Black;

CRGB ledsMain[NUM_LEDS_MAIN];
CRGB ledsSecondary[NUM_LEDS_SECONDARY];

bool isTurningOnAll = false;
bool isTurningOffAll = false;

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<LED_TYPE, LED_PIN_MAIN, COLOR_ORDER>(ledsMain, NUM_LEDS_MAIN).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<LED_TYPE, LED_PIN_SECONDARY, COLOR_ORDER>(ledsSecondary, NUM_LEDS_SECONDARY).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear();
  FastLED.show();
}

void setAll(CRGB leds[], int numLeds, const CRGB& color) {
  for (int i = 0; i < numLeds; i++) {
    leds[i] = color;
  }
  FastLED.show();
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
      if (command == 'C') {
        int red = Serial.parseInt();
        int green = Serial.parseInt();
        setAll(ledsMain, NUM_LEDS_MAIN, CRGB(red, green, 0));
      }
    }
}




CRGB blendColors(const CRGB& color1, const CRGB& color2, float progress) {
  byte r = color1.r + (color2.r - color1.r) * progress;
  byte g = color1.g + (color2.g - color1.g) * progress;
  byte b = color1.b + (color2.b - color1.b) * progress;

  return CRGB(r, g, b);
}

#include <FastLED.h>

#define LED_PIN_MAIN 2
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

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 'C') {  // New command to set all LEDs to a specific color
      // Read the custom RGB values from Serial
      int red = Serial.parseInt();
      int green = Serial.parseInt();
      int blue = Serial.parseInt();
      setAll(ledsMain, NUM_LEDS_MAIN, CRGB(red, green, blue));
    } 
    // else{
    //     if (command == '0') {
    //       fadeAll(ledsMain, NUM_LEDS_MAIN, CRGB::Black, CRGB::Red, 2000); // 2 seconds fade time
    //     } else if (command == '1') {
    //       fadeAll(ledsMain, NUM_LEDS_MAIN, CRGB::Red, CRGB::Black, 2000);
    //     } else if (command == '2') {
    //       fadeSegment(ledsMain, 0, HALF_LEDS, CRGB::Black, CRGB::Red, 2000); // 2 seconds fade time
    //     } else if (command == '3') {
    //       fadeSegment(ledsMain, 0, HALF_LEDS, CRGB::Red, CRGB::Black, 2000); // 2 seconds fade time
    //     } else if (command == '4') {
    //       fadeSegment(ledsMain, HALF_LEDS, NUM_LEDS_MAIN, CRGB::Black, CRGB::Red, 2000); // 2 seconds fade time
    //     } else if (command == '5') {
    //       fadeSegment(ledsSecondary, 0, NUM_LEDS_SECONDARY, CRGB::Red, CRGB::Black, 2000); // 2 seconds fade time
    //     } else if (command == '6'){
    //       fadeSegment(ledsSecondary, 0, NUM_LEDS_SECONDARY, CRGB::Red, CRGB::Black, 2000); // 2 seconds fade time
    //     } 
    //     else if (command == '7') {  // New command to set custom color
    //         // Read the custom RGB values from Serial
    //         int red = Serial.parseInt();
    //         int green = Serial.parseInt();
    //         int blue = Serial.parseInt();
    //         int smooth = Serial.parseInt();
    //         fadeAll(ledsMain, NUM_LEDS_MAIN, previousFullColor, CRGB(red, green, blue), smooth);
    //       }
          
    //     } 

    }
}

void fadeAll(CRGB leds[], int numLeds, const CRGB& startColor, const CRGB& endColor, int fadeDuration) {
  unsigned long startTime = millis();

  while (millis() - startTime <= fadeDuration) {
    float progress = float(millis() - startTime) / fadeDuration;
    CRGB currentColor = blendColors(startColor, endColor, progress);
    for (int i = 0; i < numLeds; i++) {
      leds[i] = currentColor;
    }
    FastLED.show();
  }
  previousFullColor = endColor;
}

void setAll(CRGB leds[], int numLeds, const CRGB& color) {
  for (int i = 0; i < numLeds; i++) {
    leds[i] = color;
  }
  FastLED.show();
}

void fadeSegment(CRGB leds[], int startIndex, int endLedIndex, const CRGB& startColor, const CRGB& endColor, int fadeDuration) {
  unsigned long startTime = millis();
  while (millis() - startTime <= fadeDuration) {
    float progress = float(millis() - startTime) / fadeDuration;
    CRGB currentColor = blendColors(startColor, endColor, progress);
    for (int i = startIndex; i < endLedIndex; i++) {
      leds[i] = currentColor;
    }
    FastLED.show();
  }
}

CRGB blendColors(const CRGB& color1, const CRGB& color2, float progress) {
  byte r = color1.r + (color2.r - color1.r) * progress;
  byte g = color1.g + (color2.g - color1.g) * progress;
  byte b = color1.b + (color2.b - color1.b) * progress;

  return CRGB(r, g, b);
}

#include <Arduino.h>
#include <math.h>
const int   NUM_CH          = 1;
const int   ADC_PINS[NUM_CH] = {34};     
const float FS              = 2000.0f;   
const uint32_t PERIOD_US    = 500;       
const int   PLOT_EVERY      = 10;        
const float HP_HZ    = 20.0f;   
const float NOTCH_HZ = 50.0f;   
const float LP_HZ    = 450.0f;  
const float ENV_HZ   = 5.0f;    


struct Biquad {
  float b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0;
  float z1 = 0, z2 = 0;
  float process(float x) {
    float y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
};

enum FilterType { LOWPASS, HIGHPASS, NOTCH };

Biquad makeFilter(FilterType type, float f0, float Q) {
  float w0 = 2.0f * PI * f0 / FS;
  float c = cosf(w0), s = sinf(w0);
  float alpha = s / (2.0f * Q);
  float b0, b1, b2, a0, a1, a2;
  switch (type) {
    case LOWPASS:
      b0 = (1 - c) / 2; b1 = 1 - c;     b2 = (1 - c) / 2; break;
    case HIGHPASS:
      b0 = (1 + c) / 2; b1 = -(1 + c);  b2 = (1 + c) / 2; break;
    default: // NOTCH
      b0 = 1;           b1 = -2 * c;    b2 = 1;           break;
  }
  a0 = 1 + alpha; a1 = -2 * c; a2 = 1 - alpha;
  Biquad f;
  f.b0 = b0 / a0; f.b1 = b1 / a0; f.b2 = b2 / a0;
  f.a1 = a1 / a0; f.a2 = a2 / a0;
  return f;
}


struct Channel {
  Biquad hp, notch, lp;
  float env = 0;
  double sumSq = 0, sumRaw = 0;
};
Channel ch[NUM_CH];
float envAlpha;

bool plotMode = true;
uint32_t sampleCount = 0;
uint32_t measCount = 0;

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < NUM_CH; i++) {
    pinMode(ADC_PINS[i], INPUT);
    ch[i].hp    = makeFilter(HIGHPASS, HP_HZ, 0.7071f);
    ch[i].notch = makeFilter(NOTCH, NOTCH_HZ, 30.0f);
    ch[i].lp    = makeFilter(LOWPASS, LP_HZ, 0.7071f);
  }
  envAlpha = 1.0f - expf(-2.0f * PI * ENV_HZ / FS);
  delay(500);
  Serial.println("MSI Stage 3 ready. Type p (plot) or m (measure).");
}

void handleSerial() {
  while (Serial.available()) {
    char k = Serial.read();
    if (k == 'p') { plotMode = true; }
    if (k == 'm') {
      plotMode = false;
      measCount = 0;
      for (int i = 0; i < NUM_CH; i++) { ch[i].sumSq = 0; ch[i].sumRaw = 0; }
      Serial.println("Measure mode: RMS of filtered signal, 1 s windows");
    }
  }
}

void loop() {
  static uint32_t next = micros();
  int32_t wait = (int32_t)(micros() - next);
  if (wait < 0) { handleSerial(); return; }
  if (wait > (int32_t)(10 * PERIOD_US)) next = micros();  
  next += PERIOD_US;

  float yOut[NUM_CH];
  for (int i = 0; i < NUM_CH; i++) {
    float raw = (float)analogReadMilliVolts(ADC_PINS[i]);   
    float y = ch[i].hp.process(raw);
    y = ch[i].notch.process(y);
    y = ch[i].lp.process(y);
    ch[i].env += envAlpha * (fabsf(y) - ch[i].env);         
    yOut[i] = y;

    if (!plotMode) {
      ch[i].sumSq  += (double)y * y;
      ch[i].sumRaw += raw;
    }
  }


  if (plotMode && (sampleCount % PLOT_EVERY) == 0) {
    for (int i = 0; i < NUM_CH; i++) {
      if (i > 0) Serial.print(',');
      Serial.printf("ch%d:%.1f,env%d:%.1f", i + 1, yOut[i], i + 1, ch[i].env);
    }
    Serial.println();
  }

  sampleCount++;

  if (!plotMode) {
    measCount++;
    if (measCount >= (uint32_t)FS) {
      for (int i = 0; i < NUM_CH; i++) {
        float rms = sqrt(ch[i].sumSq / measCount);
        float dc  = ch[i].sumRaw / measCount;
        Serial.printf("ch%d  RMS: %.1f mV   DC bias: %.0f mV\n", i + 1, rms, dc);
        ch[i].sumSq = 0; ch[i].sumRaw = 0;
      }
      measCount = 0;
    }
  }
}

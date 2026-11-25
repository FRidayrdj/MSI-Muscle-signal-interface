#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <math.h>


const char* WIFI_SSID = "YOUR_HOTSPOT_NAME";
const char* WIFI_PASS = "YOUR_HOTSPOT_PASSWORD";


const uint16_t UDP_PORT = 5005;
const int   NUM_CH            = 1;
const int   ADC_PINS[NUM_CH]  = {34};    
const float FS                = 2000.0f; 
const uint32_t PERIOD_US      = 500;     
const int   SAMPLES_PER_PACKET = 50;     
const int   LED_PIN           = 2;       

const float HP_HZ = 20.0f, NOTCH_HZ = 50.0f, LP_HZ = 450.0f;


struct Biquad {
  float b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0, z1 = 0, z2 = 0;
  float process(float x) {
    float y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
};
enum FilterType { LOWPASS, HIGHPASS, NOTCH };

Biquad makeFilter(FilterType type, float f0, float Q) {
  float w0 = 2.0f * PI * f0 / FS, c = cosf(w0), s = sinf(w0), alpha = s / (2.0f * Q);
  float b0, b1, b2;
  switch (type) {
    case LOWPASS:  b0 = (1 - c) / 2; b1 = 1 - c;    b2 = (1 - c) / 2; break;
    case HIGHPASS: b0 = (1 + c) / 2; b1 = -(1 + c); b2 = (1 + c) / 2; break;
    default:       b0 = 1;           b1 = -2 * c;   b2 = 1;           break;
  }
  float a0 = 1 + alpha;
  Biquad f;
  f.b0 = b0 / a0; f.b1 = b1 / a0; f.b2 = b2 / a0;
  f.a1 = (-2 * c) / a0; f.a2 = (1 - alpha) / a0;
  return f;
}

struct Channel { Biquad hp, notch, lp; };
Channel ch[NUM_CH];

float filterSample(int i, float raw) {
  float y = ch[i].hp.process(raw);
  y = ch[i].notch.process(y);
  return ch[i].lp.process(y);
}


struct __attribute__((packed)) Packet {
  char     magic[2];   
  uint8_t  numCh;
  uint8_t  count;      
  uint32_t seq;        
  int16_t  data[SAMPLES_PER_PACKET * NUM_CH];
};

QueueHandle_t pktQueue;
WiFiUDP udp;
IPAddress target;
bool haveTarget = false;

IPAddress broadcastIP() {
  IPAddress ip = WiFi.localIP(), mask = WiFi.subnetMask(), b;
  for (int i = 0; i < 4; i++) b[i] = ip[i] | (uint8_t)~mask[i];
  return b;
}


void senderTask(void*) {
  Packet p;
  for (;;) {
    if (xQueueReceive(pktQueue, &p, pdMS_TO_TICKS(100)) == pdTRUE &&
        WiFi.status() == WL_CONNECTED) {

      udp.beginPacket(haveTarget ? target : broadcastIP(), UDP_PORT);
      udp.write((const uint8_t*)&p, sizeof(p));
      udp.endPacket();
    }
    int n = udp.parsePacket();               
    if (n > 0) {
      char buf[16];
      udp.read(buf, sizeof(buf));
      target = udp.remoteIP();
      haveTarget = true;
    }
    digitalWrite(LED_PIN, WiFi.status() == WL_CONNECTED ? HIGH : LOW);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  for (int i = 0; i < NUM_CH; i++) {
    pinMode(ADC_PINS[i], INPUT);
    ch[i].hp    = makeFilter(HIGHPASS, HP_HZ, 0.7071f);
    ch[i].notch = makeFilter(NOTCH, NOTCH_HZ, 30.0f);
    ch[i].lp    = makeFilter(LOWPASS, LP_HZ, 0.7071f);

    float raw = (float)analogReadMilliVolts(ADC_PINS[i]);
    for (int k = 0; k < 4000; k++) filterSample(i, raw);
  }

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);                      
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(250);
    Serial.print(".");
  }
  digitalWrite(LED_PIN, HIGH);
  Serial.printf("\nConnected. ESP32 IP: %s\n", WiFi.localIP().toString().c_str());

  udp.begin(UDP_PORT);
  pktQueue = xQueueCreate(16, sizeof(Packet));
  xTaskCreatePinnedToCore(senderTask, "sender", 4096, NULL, 2, NULL, 0);
}

void loop() {
  static uint32_t next = micros();
  static Packet pkt;
  static int idx = 0;
  static uint32_t seq = 0;

  int32_t wait = (int32_t)(micros() - next);
  if (wait < 0) return;
  if (wait > (int32_t)(20 * PERIOD_US)) next = micros();   
  next += PERIOD_US;

  for (int i = 0; i < NUM_CH; i++) {
    float y = filterSample(i, (float)analogReadMilliVolts(ADC_PINS[i]));
    long v = lroundf(y * 10.0f);
    if (v > 32767) v = 32767;
    if (v < -32768) v = -32768;
    pkt.data[idx * NUM_CH + i] = (int16_t)v;
  }

  if (++idx == SAMPLES_PER_PACKET) {
    pkt.magic[0] = 'E'; pkt.magic[1] = 'M';
    pkt.numCh = NUM_CH;
    pkt.count = SAMPLES_PER_PACKET;
    pkt.seq = seq++;
    xQueueSend(pktQueue, &pkt, 0);           
    idx = 0;
  }
}

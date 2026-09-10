#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>
#include <OneWire.h>
#include <DallasTemperature.h>

/************* WiFi *************/
const char* ssid       = "Kousttav_5G";
const char* password   = "biswas1234";
const char* serverName = "http://192.168.29.135:5000/data";
const char* deleteURL  = "http://192.168.29.135:5000/delete_last_two";

/************* Pins *************/
#define TdsPin        34  
#define TurbidityPin  35
#define pHPin         32
#define DOPin         33       // 0<-- DO sensor analog pin

#define VREF          3.3
#define SCOUNT        30
#define AVG_COUNT     10
#define ONE_WIRE_BUS  4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

/************* Buffers *************/
int tdsBuffer[SCOUNT];
int turbBuffer[SCOUNT];
int phBuffer[SCOUNT];
int doBuffer[SCOUNT];          // <-- DO buffer

int tdsTemp[SCOUNT];
int turbTemp[SCOUNT];
int phTemp[SCOUNT];
int doTemp[SCOUNT];            // <-- DO temp buffer for median

int tdsIndex  = 0;
int turbIndex = 0;
int phIndex   = 0;
int doIndex   = 0;             // <-- DO ring index

/************* Smoothing *************/
float avgBuffer[AVG_COUNT];
int   avgIndex  = 0;
float smoothNTU = 0;
float smoothPH  = 7;
float smoothTDS = 0;
float smoothDO  = 0;           // <-- DO EMA

/************* Voltages *************/
float tdsVoltage  = 0;
float turbVoltage = 0;
float phVoltage   = 0;
float doVoltage   = 0;         // <-- DO voltage

/************* Final Values *************/
float temperature   = 25;
float tdsValue      = 0;
float turbidityNTU  = 0;
float phValue       = 7;
float doValue       = 0;       // <-- DO in mg/L
float doSaturation  = 0;       // <-- DO saturation %

/************* Zero Detection Counters *************/
int tdsZeroCount  = 0;
int turbZeroCount = 0;
int phZeroCount   = 0;
int doZeroCount   = 0;         // <-- DO zero counter

/************* Potability & Send Counter *************/
int potability = 0;
int sendCount  = 0;

/* ──────────────────────────────────────────────────
   DO Saturation vs Temperature lookup (mg/L at 1 atm)
   Index 0 = 0 °C, index 40 = 40 °C
   ────────────────────────────────────────────────── */
const float doSatTable[41] = {
  14.62, 14.22, 13.83, 13.46, 13.11, 12.77, 12.45, 12.14, 11.84, 11.56,
  11.29, 11.03, 10.78, 10.54, 10.31, 10.08,  9.87,  9.67,  9.47,  9.28,
   9.09,  8.91,  8.74,  8.57,  8.41,  8.26,  8.11,  7.96,  7.83,  7.69,
   7.56,  7.43,  7.31,  7.19,  7.08,  6.97,  6.86,  6.75,  6.65,  6.55,
   6.45
};

float getDOSaturation(float tempC) {
  if (tempC < 0)  tempC = 0;
  if (tempC > 40) tempC = 40;
  int   lo  = (int)tempC;
  int   hi  = lo + 1;
  float frac = tempC - lo;
  if (hi > 40) hi = 40;
  return doSatTable[lo] + frac * (doSatTable[hi] - doSatTable[lo]);
}

/************* Helpers *************/
int readADC(int pin) {
  int sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += analogRead(pin);
    delayMicroseconds(200);
  }
  return sum / 5;
}

void copyBuffer(int source[], int destination[]) {
  for (int i = 0; i < SCOUNT; i++)
    destination[i] = source[i];
}

int getMedianNum(int bArray[], int len) {
  int temp[len];
  for (int i = 0; i < len; i++)
    temp[i] = bArray[i];

  for (int j = 0; j < len - 1; j++)
    for (int i = 0; i < len - j - 1; i++)
      if (temp[i] > temp[i + 1]) {
        int t       = temp[i];
        temp[i]     = temp[i + 1];
        temp[i + 1] = t;
      }

  return (len % 2 == 1) ? temp[len / 2]
                        : (temp[len / 2] + temp[len / 2 - 1]) / 2;
}

void rebootWithCleanup() {
  Serial.println("Sensor error detected! Rebooting ESP32...");
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(deleteURL);
    int code = http.GET();
    Serial.print("Delete response: ");
    Serial.println(code);
    http.end();
  }
  delay(2000);
  ESP.restart();
}

/************* Setup *************/
void setup() {
  Serial.begin(115200);
  sensors.begin();

  analogReadResolution(12);
  analogSetPinAttenuation(TdsPin,       ADC_11db);
  analogSetPinAttenuation(TurbidityPin, ADC_11db);
  analogSetPinAttenuation(pHPin,        ADC_11db);
  analogSetPinAttenuation(DOPin,        ADC_11db);  // <-- DO attenuation

  pinMode(TdsPin,       INPUT);
  pinMode(TurbidityPin, INPUT);
  pinMode(pHPin,        INPUT);
  pinMode(DOPin,        INPUT);                     // <-- DO pin mode

  // Pre-fill all buffers with mid-scale so first medians are sane
  for (int i = 0; i < SCOUNT; i++) {
    tdsBuffer[i]  = 2048;
    turbBuffer[i] = 2048;
    phBuffer[i]   = 2048;
    doBuffer[i]   = 2048;                           // <-- DO pre-fill
  }

  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");
  Serial.println(WiFi.localIP());
}

/************* Loop *************/
void loop() {

  /* ── 1. SAMPLING  (every 80 ms) ─────────────────────────── */
  static unsigned long sampleTime = 0;

  if (millis() - sampleTime >= 80) {
    sampleTime = millis();

    int tdsADC  = readADC(TdsPin);
    int turbADC = readADC(TurbidityPin);
    int phADC   = readADC(pHPin);
    int doADC   = readADC(DOPin);                   // <-- DO ADC read

    // Reject clearly bad ADC readings, hold last good value
    if (phADC < 5)
      phADC  = phBuffer[(phIndex   + SCOUNT - 1) % SCOUNT];

    if (turbADC < 10 || turbADC > 4080)
      turbADC = turbBuffer[(turbIndex + SCOUNT - 1) % SCOUNT];

    if (doADC < 5)
      doADC  = doBuffer[(doIndex   + SCOUNT - 1) % SCOUNT];  // <-- DO guard

    tdsBuffer[tdsIndex]   = tdsADC;
    turbBuffer[turbIndex] = turbADC;
    phBuffer[phIndex]     = phADC;
    doBuffer[doIndex]     = doADC;                  // <-- DO store

    tdsIndex  = (tdsIndex  + 1) % SCOUNT;
    turbIndex = (turbIndex + 1) % SCOUNT;
    phIndex   = (phIndex   + 1) % SCOUNT;
    doIndex   = (doIndex   + 1) % SCOUNT;           // <-- DO index advance
  }

  /* ── 2. PROCESS + SEND  (every 2 s) ─────────────────────── */
  static unsigned long sendTime = 0;

  if (millis() - sendTime < 2000) return;
  sendTime = millis();

  /* 2a. Median voltages */
  copyBuffer(tdsBuffer,  tdsTemp);
  copyBuffer(turbBuffer, turbTemp);
  copyBuffer(phBuffer,   phTemp);
  copyBuffer(doBuffer,   doTemp);                   // <-- DO copy

  int tdsMedian  = getMedianNum(tdsTemp,  SCOUNT);
  int turbMedian = getMedianNum(turbTemp, SCOUNT);
  int phMedian   = getMedianNum(phTemp,   SCOUNT);
  int doMedian   = getMedianNum(doTemp,   SCOUNT);  // <-- DO median

  tdsVoltage  = tdsMedian  * VREF / 4095.0;
  turbVoltage = turbMedian * VREF / 4095.0;
  phVoltage   = phMedian   * VREF / 4095.0;
  doVoltage   = doMedian   * VREF / 4095.0;        // <-- DO voltage

  /* 2b. Temperature */
  sensors.requestTemperatures();
  temperature = sensors.getTempCByIndex(0);
  if (temperature == DEVICE_DISCONNECTED_C) {
    Serial.println("Temp sensor error – using 25 °C fallback");
    temperature = 25.0;
  }

  /* 2c. TDS */
  float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0);
  float compensationVoltage     = tdsVoltage / compensationCoefficient;

  float rawTDS =
    (133.42 * compensationVoltage * compensationVoltage * compensationVoltage
     - 255.86 * compensationVoltage * compensationVoltage
     + 857.39 * compensationVoltage) * 0.5;

  smoothTDS = 0.93 * smoothTDS + 0.07 * rawTDS;
  tdsValue  = round(smoothTDS * 100.0) / 100.0;

  /* 2d. Turbidity */
  float rawNTU = (3.3 - turbVoltage) * 100.0;
  rawNTU = constrain(rawNTU, 0.0, 300.0);

  avgBuffer[avgIndex] = rawNTU;
  avgIndex = (avgIndex + 1) % AVG_COUNT;

  float avgNTU = 0;
  for (int i = 0; i < AVG_COUNT; i++) avgNTU += avgBuffer[i];
  avgNTU /= AVG_COUNT;

  smoothNTU    = 0.92 * smoothNTU + 0.08 * avgNTU;
  turbidityNTU = round(smoothNTU * 100.0) / 100.0;

  /* 2e. pH */
  float rawPH = 7.0 + (0.30 - phVoltage) * 10.0;
  if (fabs(rawPH - smoothPH) < 0.05) rawPH = smoothPH;
  smoothPH = 0.97 * smoothPH + 0.03 * rawPH;
  phValue  = constrain(round(smoothPH * 100.0) / 100.0, 0.0, 14.0);

  /* 2f. Dissolved Oxygen ─────────────────────────────────────
     DFRobot Gravity DO sensor:
       V_sat  = voltage at full saturation (calibrated at ~3.3 V max)
       DO     = (doVoltage / V_sat) * DO_sat(T)
     We use the temperature-corrected saturation table.
  ──────────────────────────────────────────────────────────── */
  float doSat       = getDOSaturation(temperature);  // mg/L at current temp
  float doVoltSat   = 3.3;                           // voltage at 100% sat
                                                     // adjust if you have calibration data
  float rawDO       = (doVoltage / doVoltSat) * doSat;
  rawDO             = constrain(rawDO, 0.0, 20.0);

  smoothDO          = 0.93 * smoothDO + 0.07 * rawDO;
  doValue           = round(smoothDO * 100.0) / 100.0;

  doSaturation      = (doSat > 0)
                      ? constrain(round((doValue / doSat) * 10000.0) / 100.0, 0.0, 150.0)
                      : 0;

  /* 2g. Potability
     Criteria:
       pH       6.5 – 8.5
       TDS      ≤ 500 ppm
       Turbidity ≤ 5 NTU
       DO       ≥ 5 mg/L   (WHO minimum for drinking water)
     Potable if all 4 pass, or at least 3 pass (score >= 3)
  */
  int score = (phValue      >= 6.5 && phValue <= 8.5)
            + (tdsValue     <= 500)
            + (turbidityNTU <= 5)
            + (doValue      >= 5.0);                // <-- DO potability check
  potability = (score >= 3) ? 1 : 0;

  /* 2h. Guard – reject physically impossible values */
  if (tdsValue <= 0 || turbidityNTU <= 0 || phValue <= 0 || doValue <= 0) {
    Serial.println("Invalid reading – skipping send");
    return;
  }

  /* 2i. Stuck-at-zero detection */
  tdsZeroCount  = (tdsValue     < 1.0) ? tdsZeroCount  + 1 : 0;
  turbZeroCount = (turbidityNTU < 0.5) ? turbZeroCount + 1 : 0;
  phZeroCount   = (phValue      < 1.0) ? phZeroCount   + 1 : 0;
  doZeroCount   = (doValue      < 0.2) ? doZeroCount   + 1 : 0;  // <-- DO zero detect

  if (tdsZeroCount  >= 5 || turbZeroCount >= 5 ||
      phZeroCount   >= 5 || doZeroCount   >= 5) {
    rebootWithCleanup();
    return;
  }

  /* 2j. Print */
  Serial.println("------ WATER DATA ------");
  Serial.print("Temperature  : "); Serial.print(temperature,  2); Serial.println(" °C");
  Serial.print("TDS          : "); Serial.print(tdsValue,      2); Serial.println(" ppm");
  Serial.print("Turbidity    : "); Serial.print(turbidityNTU, 2); Serial.println(" NTU");
  Serial.print("pH           : "); Serial.println(phValue,     2);
  Serial.print("DO           : "); Serial.print(doValue,       2); Serial.println(" mg/L");
  Serial.print("DO Saturation: "); Serial.print(doSaturation,  2); Serial.println(" %");
  Serial.print("Potability   : "); Serial.println(potability);

  /* 2k. HTTP POST */
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"tds\":"              + String(tdsValue,      2) + ",";
    json += "\"turbidity\":"        + String(turbidityNTU,  2) + ",";
    json += "\"ph\":"               + String(phValue,        2) + ",";
    json += "\"temperature\":"      + String(temperature,   2) + ",";
    json += "\"dissolved_oxygen\":" + String(doValue,        2) + ",";  // <-- real DO now
    json += "\"do_saturation\":"    + String(doSaturation,   2) + ",";
    json += "\"potability\":"       + String(potability);
    json += "}";

    Serial.println("Sending: " + json);
    int httpCode = http.POST(json);
    Serial.print("HTTP Response: "); Serial.println(httpCode);
    http.end();

    if (httpCode > 0) {
      sendCount++;
      if (sendCount >= 200) {
        Serial.println("200 sends reached – scheduled reboot");
        delay(2000);
        ESP.restart();
      }
    }
  } else {
    Serial.println("WiFi disconnected – skipping send");
  }
}
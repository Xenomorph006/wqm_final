#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

const char* ssid = "Kousttav_5G";
const char* password = "biswas1234";

WebServer server(80);

// Relay Pins
#define BASE_RELAY 25
#define ACID_RELAY 26
#define PELTIER_RELAY 27

Servo myServo;

#define SERVO_PIN 14
#define OFF_POS 0
#define ON_POS 100

//----------------------------------------------------
void sendResponse(String msg) {
  server.send(200, "application/json", msg);
}

//----------------------------------------------------
void handleBase() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "Missing JSON");
    return;
  }

  DynamicJsonDocument doc(256);

  if (deserializeJson(doc, server.arg("plain"))) {
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  String message = doc["message"];
  float time = doc["time"];
  float value = doc["value"];

  Serial.println("\n====== BASE ======");
  Serial.println(message);
  Serial.print("Time (min): ");
  Serial.println(time);
  Serial.print("Value: ");
  Serial.println(value);

  digitalWrite(BASE_RELAY, LOW);

  unsigned long duration = (unsigned long)(time * 60000.0);
  delay(duration);

  digitalWrite(BASE_RELAY, HIGH);

  DynamicJsonDocument res(128);
  res["status"] = "success";
  res["motor"] = "base";
  res["time"] = time;
  res["value"] = value;

  String output;
  serializeJson(res, output);

  sendResponse(output);
}

//----------------------------------------------------
void handleAcid() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "Missing JSON");
    return;
  }

  DynamicJsonDocument doc(256);

  if (deserializeJson(doc, server.arg("plain"))) {
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  String message = doc["message"];
  float time = doc["time"];
  float value = doc["value"];

  Serial.println("\n====== ACID ======");
  Serial.println(message);
  Serial.print("Time (min): ");
  Serial.println(time);
  Serial.print("Value: ");
  Serial.println(value);

  digitalWrite(ACID_RELAY, LOW);

  unsigned long duration = (unsigned long)(time * 60000.0);
  delay(duration);

  digitalWrite(ACID_RELAY, HIGH);

  DynamicJsonDocument res(128);
  res["status"] = "success";
  res["motor"] = "acid";
  res["time"] = time;
  res["value"] = value;

  String output;
  serializeJson(res, output);

  sendResponse(output);
}

//----------------------------------------------------
void handleCooling() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "Missing JSON");
    return;
  }

  DynamicJsonDocument doc(256);

  if (deserializeJson(doc, server.arg("plain"))) {
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  String message = doc["message"];
  float time = doc["time"];

  Serial.println("\n====== COOLING ======");
  Serial.println(message);
  Serial.print("Time (min): ");
  Serial.println(time);

  digitalWrite(PELTIER_RELAY, LOW);

  unsigned long duration = (unsigned long)(time * 60000.0);
  delay(duration);

  digitalWrite(PELTIER_RELAY, HIGH);

  DynamicJsonDocument res(128);
  res["status"] = "success";
  res["device"] = "peltier";
  res["time"] = time;

  String output;
  serializeJson(res, output);

  sendResponse(output);
}
void handleLowDo() {
  Serial.println("\n====== LOWDO ======");

  myServo.write(ON_POS);   // 25°
  delay(3000);

  myServo.write(OFF_POS);  // 0°
  delay(3000);

  DynamicJsonDocument res(128);
  res["status"] = "success";
  res["device"] = "servo";

  String output;
  serializeJson(res, output);

  sendResponse(output);
}
//----------------------------------------------------
void setup() {
  Serial.begin(115200);

  pinMode(BASE_RELAY, OUTPUT);
  pinMode(ACID_RELAY, OUTPUT);
  pinMode(PELTIER_RELAY, OUTPUT);

  // Active LOW relay
  digitalWrite(BASE_RELAY, HIGH);
  digitalWrite(ACID_RELAY, HIGH);
  digitalWrite(PELTIER_RELAY, HIGH);

  ESP32PWM::allocateTimer(0);
  myServo.setPeriodHertz(50);            // standard 50Hz servo signal
  myServo.attach(SERVO_PIN, 500, 2400);  // explicit min/max pulse width (µs)
  myServo.write(OFF_POS);

  WiFi.begin(ssid, password);

  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.print(WiFi.localIP());

  server.on("/base", HTTP_POST, handleBase);
  server.on("/acid", HTTP_POST, handleAcid);
  server.on("/cooling", HTTP_POST, handleCooling);
  server.on("/lowdo", HTTP_POST, handleLowDo);

  server.begin();
  Serial.println("\nHTTP Server Started");
}

//----------------------------------------------------
void loop() {
  server.handleClient();
}
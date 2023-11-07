#include <ESP8266WiFi.h>                                // Подключаем библиотеку ESP8266WiFi
#include <ESP8266HTTPClient.h>
#include <Wire.h>                                       // Подключаем библиотеку Wire
#include <WiFiClient.h>
#include <Adafruit_BME280.h>                            // Подключаем библиотеку Adafruit_BME280
#include <Arduino_JSON.h>
#include <Adafruit_Sensor.h>                            // Подключаем библиотеку Adafruit_Sensor

#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BME280 bme;

const int R_LED = D5;
const int G_LED = D6;
const int B_LED = D7;
const int ERROR_LED = D0;
const int SUCCESS_LED = D8;

const char * ssid = "L8";
const char * password = "o???AoXqpAE?ejHnL7oLkdN";


String serverName = "http://146.0.79.198:5000";

unsigned long lastTime = 0;
unsigned long timerDelay = 15000;

unsigned long lastTimeColor = 0;
unsigned long timerDelayColor = 1500;

String colorReadings;

void setup() {
  pinMode(ERROR_LED, OUTPUT);
  pinMode(SUCCESS_LED, OUTPUT);
  Serial.begin(115200);

  if (!bme.begin(0x76)) { // Проверка инициализации датчика
    Serial.println("Could not find a valid BME280 sensor, check wiring!"); // Печать, об ошибки инициализации.
    while (1); // Зацикливаем
  }

  Serial.print("Connecting to "); // Отправка в Serial port 
  Serial.println(ssid); // Отправка в Serial port 
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println(""); // Отправка в Serial port 
  Serial.println("WiFi connected."); // Отправка в Serial port 
  Serial.println("IP address: "); // Отправка в Serial port 
  Serial.println(WiFi.localIP()); // Отправка в Serial port 
}

void loop() {
    digitalWrite(ERROR_LED, LOW);
    digitalWrite(SUCCESS_LED, LOW);
  if ((millis() - lastTime) > timerDelay) {

    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;

      float temp = bme.readTemperature();
      float pressure = bme.readPressure() / 100.0F;
      float humidity = bme.readHumidity();

      String serverPath = serverName + "/set_state";

      http.begin(client, serverPath.c_str());
      http.addHeader("Content-Type", "application/json");
      String httpRequestData = "{\"temp\":" + String(temp) + ",\"hum\": " + String(humidity) + ",\"color\": -1}";
      int httpResponseCode = http.POST(httpRequestData);
      if( httpResponseCode == 200){
        digitalWrite(SUCCESS_LED, HIGH);
      } else {
        digitalWrite(ERROR_LED, HIGH);
      }
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      http.end();


      

    } else {
      Serial.println("WiFi Disconnected");
      digitalWrite(ERROR_LED, HIGH);

    }
    lastTime = millis();
  }

  if ((millis() - lastTimeColor) > timerDelayColor){

      String serverPath = serverName + "/get_state";
      colorReadings = httpGETRequest(serverPath);
      JSONVar myObject = JSON.parse(colorReadings);
      if (JSON.typeof(myObject) == "undefined") {
        Serial.println("Parsing input failed!");
        digitalWrite(ERROR_LED, HIGH);
      }
      // Serial.print("JSON object = ");
      String color = myObject["color"];

      // Serial.println(StrToHex(color.c_str()));
      uint64_t rgb = StrToHex(color.c_str());
      int r = rgb >> 16;
      int g = (rgb & 0x00ff00) >> 8;
      int b = rgb & 0x0000ff;
      Serial.println(r);
      Serial.println(g);
      Serial.println(b);
      analogWrite(R_LED, r);
      analogWrite(G_LED, g);
      analogWrite(B_LED, b);
      lastTimeColor = millis();
  }
}

String httpGETRequest(String serverName) {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, serverName);

  int httpResponseCode = http.GET();

  String payload = "{}";

  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
    digitalWrite(SUCCESS_LED, HIGH);
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
    digitalWrite(ERROR_LED, HIGH);
  }
  // Free resources
  http.end();

  return payload;
}
uint64_t StrToHex(const char * str) {
  return (uint64_t) strtoull(str, 0, 16);
}
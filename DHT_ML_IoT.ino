#include <WiFi.h>
#include <HTTPClient.h>

// Replace with your network credentials
const char* ssid = "iot1";
const char* password = "vedant123";
int i;
int a, b;

const char* serverUrl = "https://192.168.177.240/predict";
int temp[10] = {30, 22, 25, 18, 28, 24, 21, 19, 35, 32};
int hum[10] = {70, 80, 65, 90, 75, 85, 95, 60, 50, 55};

void setup() {
  Serial.begin(115200);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to Wi-Fi");
  
  i = 0;
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    a = temp[i];
    b = hum[i];
    String url = String(serverUrl) + "?temperature="+String(a)+"&humidity="+String(b)+"&status=active";
    http.begin(url);
    
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error code: " + String(httpResponseCode));
    }

    i++;

    if(i >= 10){
      i = 0;
    }

    http.end();
    
    delay(1000); // Wait for 1 second before next request
  }
}

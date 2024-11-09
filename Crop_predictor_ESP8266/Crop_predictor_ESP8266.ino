#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>


const char* ssid = "pjtproj";
const char* password = "dummy123";   
ESP8266WebServer server(80);         

#define DHTPIN D4         // GPIO2 
#define SOIL_MOISTURE_PIN A0 
#define DHTTYPE DHT11   

DHT dht(DHTPIN, DHTTYPE);
unsigned long previousMillis = 0; // Store the last time sensor readings were printed
const long interval = 5000; 

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    
    // Wait for the Wi-Fi connection
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

  
    dht.begin();

    // Define the route for getting data
    server.on("/get_data", HTTP_GET, handleGetData);

    
    server.begin();
}

void loop() {
    server.handleClient();
    
    
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;

        
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN); // Read soil moisture

      
        if (isnan(temperature) || isnan(humidity)) {
            Serial.println("Failed to read from DHT sensor");
        } else {
           
            Serial.print("Temperature: ");
            Serial.print(temperature);
            Serial.print(" °C, Humidity: ");
            Serial.print(humidity);
            Serial.print(" %, Soil Moisture: ");
            Serial.println(soilMoistureValue);
        }
    }
}

void handleGetData() {
    // Set CORS headers
    server.sendHeader("Access-Control-Allow-Origin", "*"); // Allow all origins
    server.sendHeader("Access-Control-Allow-Methods", "GET, OPTIONS"); 

 
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN); // Read soil moisture

   
    if (isnan(temperature) || isnan(humidity)) {
        server.send(500, "application/json", "{\"error\":\"Failed to read from DHT sensor\"}");
        return;
    }

    // Create JSON response
    String jsonResponse = "{";
    jsonResponse += "\"temperature\":" + String(temperature) + ",";
    jsonResponse += "\"humidity\":" + String(humidity) + ",";
    jsonResponse += "\"soilMoisture\":" + String(soilMoistureValue);
    jsonResponse += "}";

    // Send JSON response
    server.send(200, "application/json", jsonResponse);
}
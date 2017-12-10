
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <PubSubClient.h>

//------------------------------------------
//MQTT
#define mqtt_server "192.168.0.4"
#define mqtt_user "pi"
#define mqtt_password "1FjqrZ78*"

#define topic_response_light "home/aquarium/light/response"
#define topic_response_temperature "home/aquarium/temperature/response"
#define topic_response_co2 "home/aquarium/co2/response"
#define topic_response_fertilizer "home/aquarium/fertilizer/response"

//------------------------------------------
//DS18B20
#define ONE_WIRE_BUS D7 //Pin to which is attached a temperature sensor

//------------------------------------------
//Relay
#define RELAY_1_PIN D1
//------------------------------------------
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature DS18B20(&oneWire);
long lastTemp; //The last measurement
const int durationTemp = 5000; //The frequency of temperature measurement

//------------------------------------------
//WIFI
const char* ssid = "MYWIFI";
const char* password = "MYWIFIPASSWORD";

//------------------------------------------
WiFiClient espClient;
PubSubClient client(espClient);

//-----------Publish Methods----------------
void publishTemp(){
  DS18B20.requestTemperatures(); 
  float newTemp = DS18B20.getTempCByIndex(0);
  client.publish(topic_response_temperature, String(newTemp).c_str(), false);
}

//----------Control Methods-----------------
void controlCO2(int operation){
  if(operation == 0){
      //Close co2 tube
      Serial.println("Close co2 tube");
      String response = "0";
      client.publish(topic_response_co2, response.c_str(), false);
    }else if(operation == 1){
      //Open co2 tube
      Serial.println("Open co2 tube");
      String response = "1";
      client.publish(topic_response_co2, response.c_str(), false);
    }
}
void controlFertilizer(byte* payload, unsigned int length){
  int emptyOperation = (char)payload[0] - '0';
  if(emptyOperation == 0 && length == 1){
    //Empty tube
    Serial.println("Empty fertilizer tube");
    String response = "0";
    client.publish(topic_response_fertilizer, response.c_str(), false);
    return;
  }
  Serial.println("Fertilize ml:");
  for(int i = 0; i < length; i++){
    Serial.print(payload[i]);
  }
  Serial.println();
  String response = "x";
  client.publish(topic_response_fertilizer, response.c_str(), false);
}
void controlLight(int operation){
  if(operation == 0){
      //Turn off
      Serial.println("Turn light off");
      String response = "0";
      digitalWrite(RELAY_1_PIN, LOW);
      client.publish(topic_response_light, response.c_str(), false);
    }else if(operation == 1){
      //Turn on
      Serial.println("Turn light on");
      String response = "1";
      digitalWrite(RELAY_1_PIN, HIGH);
      client.publish(topic_response_light, response.c_str(), false);
    }
}
//------------------------------------------
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println();
  if(strstr(topic, "response")){
    Serial.println("This is a response");
    return; // Terminate callback since this was sent from the esp8266
  }
  if(strstr(topic, "temperature")){
    publishTemp();
    return;
  }
  if(strstr(topic, "co2")){
    int operation = (char)payload[0] - '0';
    controlCO2(operation);
    return;
  }
  if(strstr(topic, "fertilizer")){
    controlFertilizer(payload, length);
    return;
  }
  if(strstr(topic, "light")){
    int operation = (char)payload[0] - '0';
    controlLight(operation);
    return;
  }
  Serial.print("Length:");
  Serial.println(length);
  Serial.println("Payload");
  for(int i = 0; i < length; i++)
  {
    Serial.println((char)payload[i]);
  }
}

void setup() {
  //Setup Serial port speed
  Serial.begin(115200);
  //Setup pins
  pinMode(RELAY_1_PIN, OUTPUT);

  //Setup WIFI
  WiFi.begin(ssid, password);
  Serial.println("");

  //Wait for WIFI connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    // If you do not want to use a username and password, change next line to
    // if (client.connect("ESP8266Client")) {
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("home/aquarium/#"); // subscribe to all in aquarium
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

bool checkBound(float newValue, float prevValue, float maxDiff) {
  return !isnan(newValue) &&
         (newValue < prevValue - maxDiff || newValue > prevValue + maxDiff);
}

long lastMsg = 0;
float temp = 0.0;
float diff = 1.0;

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;

    DS18B20.requestTemperatures(); 
    float newTemp = DS18B20.getTempCByIndex(0);

    if (checkBound(newTemp, temp, diff)) {
      temp = newTemp;
      Serial.print("New temperature:");
      Serial.println(String(temp).c_str());
      client.publish(topic_response_temperature, String(temp).c_str(), false);
    }

  }
}


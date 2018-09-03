//------------------------------------------
//Motor
#define MOTOR_PIN 2
#define CO2_PIN 4
#define TWINSTAR_PIN 7
//------------------------------------------
//----------Control Methods-----------------

void setup() {
  //Setup Serial port speed
  Serial.begin(115200);
  //Setup pins
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(CO2_PIN, OUTPUT);
  pinMode(TWINSTAR_PIN, OUTPUT);
}

void loop() {
  digitalWrite(MOTOR_PIN,HIGH);
  delay(5000);
  digitalWrite(MOTOR_PIN,LOW);
  delay(3000);
  digitalWrite(CO2_PIN,HIGH);
  delay(5000);
  digitalWrite(CO2_PIN,LOW);
  delay(3000);
  digitalWrite(TWINSTAR_PIN,HIGH);
  delay(5000);
  digitalWrite(TWINSTAR_PIN,LOW);
  delay(3000);
}



// pin configuration
#define motor1Enable_pin 2 // enable - turn on to go home
#define motor1Position_pin 4 // input a - low to go to position 1, high to go to position 2
#define motor1Homing_pin 9 // input b - make HIGH to set home position

#define motor2Enable_pin 3
#define motor2Position_pin 5
#define motor2Homing_pin 10

/// API
void setupMotorPins() {
  pinMode(motor1Homing_pin, OUTPUT);
  pinMode(motor1Enable_pin, OUTPUT);
  pinMode(motor1Position_pin, OUTPUT);

  pinMode(motor2Homing_pin, OUTPUT);
  pinMode(motor2Enable_pin, OUTPUT);
  pinMode(motor2Position_pin, OUTPUT);

  writeEnabledPins();
  writePositionPins(LOW);
  writeHomingPins(LOW);
}

void writeEnabledPins() {
  digitalWrite(motor1Enable_pin, enabled? HIGH : LOW);
  digitalWrite(motor2Enable_pin, enabled? HIGH : LOW);
}

void writePositionPins(int value) {
  digitalWrite(motor1Position_pin, value);
  digitalWrite(motor2Position_pin, value);
}

void writeHomingPins(int value) {
  digitalWrite(motor1Homing_pin, value);
  digitalWrite(motor2Homing_pin, value);
}

void setMotorPinHome(int motor, int value) {
  int pin = motor == 1 ? motor1Homing_pin : motor2Homing_pin;
  digitalWrite(pin, value);
}

void setEnabled(bool on) {
  enabled = on;
  Serial.print("SETTING ENABLED PINS ");
  printPinState(enabled);
  writeEnabledPins();
}

void setHome(bool home) {
  Serial.print("SETTING HOMING PINS ");
  printPinState(home);
  writeHomingPins(home? HIGH : LOW);
}

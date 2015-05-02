
// pin configuration
#define motor1Enable_pin 2 // enable - turn on to go home -- green
#define motor1Position_pin 3 // input a - low to go to position 1, high to go to position 2 -- white
#define motor1Homing_pin 4 // input b - make HIGH to set home position -- purple

#define motor2Enable_pin 5 // purple
#define motor2Position_pin 6 // green
#define motor2Homing_pin 7 // black

/// API
void setupMotorPins() {
  pinMode(motor1Homing_pin, OUTPUT);
  pinMode(motor1Enable_pin, OUTPUT);
  pinMode(motor1Position_pin, OUTPUT);

  pinMode(motor2Homing_pin, OUTPUT);
  pinMode(motor2Enable_pin, OUTPUT);
  pinMode(motor2Position_pin, OUTPUT);

  setEnabled(1, LOW);
  setEnabled(2, LOW);
  writePositionPins(LOW);
  writeHomingPins(LOW);
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

void setEnabled(int motor, bool on) {
  int pin = -1;

  if (motor == 1) {
    pin = motor1Enable_pin;
    motor_1_enabled = on;
    Serial.print("MOTOR 1 ");
  }
  else if (motor == 2) {
    pin = motor2Enable_pin;
    motor_2_enabled = on;
    Serial.print("MOTOR 2 ");
  }

  if (pin < 0) {
    return;
  }

  digitalWrite(pin, on);

  Serial.print("SET ENABLED: ");
  printPinState(on);
}

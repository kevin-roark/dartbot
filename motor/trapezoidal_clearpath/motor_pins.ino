
// pin configuration
#define motor1PWM_pin 9
#define motor1Enable_pin 2
#define motor1Inhibit_pin 4

#define motor2PWM_pin 10
#define motor2Enable_pin 1
#define motor2Inhibit_pin 5

/// API
void setupMotorPins() {
  pinMode(motor1PWM_pin, OUTPUT);
  pinMode(motor1Enable_pin, OUTPUT);
  pinMode(motor1Inhibit_pin, OUTPUT);
  pinMode(motor2PWM_pin, OUTPUT);
  pinMode(motor2Enable_pin, OUTPUT);
  pinMode(motor2Inhibit_pin, OUTPUT);
  
  writeToMotor(1, ZERO_DUTY);
  writeToMotor(2, ZERO_DUTY);
  writeEnabledPins();
  writeInhibitPins();
}

void writeEnabledPins() {
  digitalWrite(motor1Enable_pin, enabled? HIGH : LOW);
  digitalWrite(motor2Enable_pin, enabled? HIGH : LOW);
}

void writeInhibitPins() {
  digitalWrite(motor1Inhibit_pin, inhibited? HIGH : LOW);
  digitalWrite(motor2Inhibit_pin, inhibited? HIGH : LOW);
}

void writeToMotor(int motor, int duty_cycle) {
  int pin = motor == 1 ? motor1PWM_pin : motor2PWM_pin;
  analogWrite(pin, duty_cycle);
}


// Ramp cycles as percentage between 0 -> 255
#define PWM_ZERO_VEL 127
#define PWM_MAX_CW_VEL 0
#define PWM_MAX_CCW_VEL 255
#define SLOW_CW_DUTY 122
#define SLOW_CCW_DUTY 132

// pin configuration
#define motor1PWM_pin 9
#define motor1Enable_pin 2
#define motor1Inhibit_pin 4
#define motor2PWM_pin 10
#define motor2Enable_pin 3
#define motor2Inhibit_pin 5
#define limitSwitch_pin 13

// behavior configuration
#define shouldPrint true
#define initiallyEnable false
#define initiallyInhibit false

// state management
boolean enabled = initiallyEnable;
boolean inhibited = initiallyInhibit;
boolean clockwise = true;
boolean waitingForLimitDepress = false;
unsigned long lastLimitSwitchTime;

void setup() {
  pinMode(motor1PWM_pin, OUTPUT);
  pinMode(motor1Enable_pin, OUTPUT);
  pinMode(motor1Inhibit_pin, OUTPUT);
  pinMode(motor2PWM_pin, OUTPUT);
  pinMode(motor2Enable_pin, OUTPUT);
  pinMode(motor2Inhibit_pin, OUTPUT);
  
  pinMode(limitSwitch_pin, INPUT);

  Serial.begin(4800);

  if (shouldPrint) {
    Serial.println("Getting started!");
  }

  writeToMotor(1, PWM_ZERO_VEL);
  writeToMotor(2, PWM_ZERO_VEL);
  writeEnabledPins();
  writeInhibitPins();
  
  lastLimitSwitchTime = millis();
}

void loop() {  
  int limitSwitch = digitalRead(limitSwitch_pin);
  if (limitSwitch == LOW && !waitingForLimitDepress) {
    Serial.println("limit switch hit dang!!!");
    waitingForLimitDepress = true;
    lastLimitSwitchTime = millis();
    clockwise = !clockwise;
  } else if (limitSwitch == HIGH && waitingForLimitDepress && millis() - lastLimitSwitchTime > 200) {
    waitingForLimitDepress = false;
    Serial.println("i am depressed!!"); 
  }

  int duty_cycle = clockwise? SLOW_CW_DUTY : SLOW_CCW_DUTY;
  writeToMotor(1, duty_cycle);
  writeToMotor(2, duty_cycle);
}


/// SerialEvent called whenever key is pressed, essentially. Runs between loop() calls
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char) Serial.read();
    switch (inChar) {
      case '1':
      case '2':
        enabled = (inChar == '2');
        Serial.print("SETTING ENABLED PIN ");
        printPinState(enabled);
        writeEnabledPins();
        break;

      case '3':
      case '4':
        inhibited = (inChar == '4');
        Serial.print("SETTING INHIBIT PIN ");
        printPinState(inhibited);
        writeInhibitPins();
        break;
    }
  }
}

/// Pins
void writeEnabledPins() {
  digitalWrite(motor1Enable_pin, enabled? HIGH : LOW);
}

void writeInhibitPins() {
  digitalWrite(motor1Inhibit_pin, inhibited? HIGH : LOW);
}

void writeToMotor(int motor, int duty_cycle) {
  int pin = motor == 1 ? motor1PWM_pin : motor2PWM_pin;
  analogWrite(pin, duty_cycle);
}

/// Printing
void printRampingUp(int val) {
  if (shouldPrint) {
    Serial.print("ramping up: ");
    Serial.println(val);
  }
}

void printRampingDown(int val) {
  if (shouldPrint) {
    Serial.print("ramping down: ");
    Serial.println(val);
  }
}

void printPinState(boolean on) {
  Serial.println(on? "HIGH" : "LOW");
}

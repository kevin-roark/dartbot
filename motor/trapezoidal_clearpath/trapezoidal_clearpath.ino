
// Ramp cycles as percentage between 0 -> 255
#define PWM_ZERO_VEL 127
#define PWM_MAX_CW_VEL 0
#define PWM_MAX_CCW_VEL 255

// loop behavior states
#define RAMPING_UP 0
#define SUSTAINING 1
#define RAMPING_DOWN 2
#define WAITING 3

// pin configuration
#define motor1PWM_pin 9
#define motor1Enable_pin 2
#define motor1Inhibit_pin 4
#define motor2PWM_pin 10
#define motor2Enable_pin 3
#define motor2Inhibit_pin 5

// behavior configuration
int rampTime = 2000; // ms
int sustainTime = 5000; // ms
int timeBetweenLoops = 4000; // ms
#define clockwise true
#define shouldLoop true
#define shouldPrint true
#define initiallyEnable false
#define initiallyInhibit false

// derived variables
int rampStepDelay = rampTime / PWM_ZERO_VEL;
int rampUpIncrement = clockwise? -1 : +1;
int rampUpLimit = clockwise? (PWM_MAX_CW_VEL + 1) : (PWM_MAX_CCW_VEL - 1); // supposed to stay at 1 way from theoretical max
int rampDownIncrement = clockwise ? +1 : -1;

// state management
boolean enabled = initiallyEnable;
boolean inhibited = initiallyInhibit;
int cyclesCompleted = 0;
int current_pwm = PWM_ZERO_VEL;
int loopState = RAMPING_UP;
unsigned long loopTimer;

void setup() {
  pinMode(motor1PWM_pin, OUTPUT);
  pinMode(motor1Enable_pin, OUTPUT);
  pinMode(motor1Inhibit_pin, OUTPUT);
  pinMode(motor2PWM_pin, OUTPUT);
  pinMode(motor2Enable_pin, OUTPUT);
  pinMode(motor2Inhibit_pin, OUTPUT);

  Serial.begin(4800);

  if (shouldPrint) {
    Serial.println("Getting started!");
  }

  writeToMotor(1);
  writeToMotor(2);
  writeEnabledPins();
  writeInhibitPins();
  resetLoopTimer();
}

void loop() {
  if (!shouldLoop && cyclesCompleted > 0) {
    return; // get out of here!
  }

  // ramp from 0 -> max velocity
  if (loopState == RAMPING_UP && isLoopTimerExpired(rampStepDelay)) {
    current_pwm += rampUpIncrement;
    writeToMotor(1);
    writeToMotor(2);
    printRampingUp(current_pwm);

    if (current_pwm == rampUpLimit) {
      transitionToSustain();
    }

    resetLoopTimer();
  }

  // sustain max velocity
  if (loopState == SUSTAINING && isLoopTimerExpired(sustainTime)) {
      loopState = RAMPING_DOWN;
      resetLoopTimer();
  }

  // ramp from max velocity -> 0
  if (loopState == RAMPING_DOWN && isLoopTimerExpired(rampStepDelay)) {
    current_pwm += rampDownIncrement;
    writeToMotor(1);
    writeToMotor(2);
    printRampingDown(current_pwm);

    if (current_pwm == PWM_ZERO_VEL) {
      transitionToWaiting();
    }

    resetLoopTimer();
  }

  // wait for next cycle
  if (loopState == WAITING && isLoopTimerExpired(timeBetweenLoops)) {
    loopState = RAMPING_UP;
    resetLoopTimer();
  }
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

void writeToMotor(int motor) {
  int pin = motor == 1 ? motor1PWM_pin : motor2PWM_pin;
  analogWrite(pin, current_pwm);
}

/// Loop Timer
boolean isLoopTimerExpired(int ms) {
  return millis() - loopTimer >= ms;
}

void resetLoopTimer() {
  loopTimer = millis();
}

/// State Transitions
void transitionToSustain() {
  loopState = SUSTAINING;

  if (shouldPrint) {
    Serial.print("sustaining with pwm ");
    Serial.print(current_pwm);
    Serial.print(" for ");
    Serial.print(sustainTime);
    Serial.println(" ms");
  }
}

void transitionToWaiting() {
  loopState = WAITING;
  cyclesCompleted += 1;

  if (shouldPrint) {
    Serial.print("completed cycle ");
    Serial.print(cyclesCompleted);
    Serial.print("! Now waiting for ");
    Serial.print(timeBetweenLoops);
    Serial.println(" ms");
  }
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

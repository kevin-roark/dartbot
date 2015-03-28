
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
#define motorPin 9
#define enablePin 2
#define inhibitPin 4

// behavior configuration
int rampTime = 2000; // ms
int sustainTime = 5000; // ms
int timeBetweenLoops = 4000; // ms
#define clockwise true
#define shouldLoop true
#define shouldPrint true
#define enabled false

// derived variables
int rampStepDelay = rampTime / PWM_ZERO_VEL;
int rampUpIncrement = clockwise? -1 : +1;
int rampUpLimit = clockwise? (PWM_MAX_CW_VEL + 1) : (PWM_MAX_CCW_VEL - 1); // supposed to stay at 1 way from theoretical max
int rampDownIncrement = clockwise ? +1 : -1;

// state management
int cyclesCompleted = 0;
int current_pwm = PWM_ZERO_VEL;
int loopState = RAMPING_UP;
unsigned long loopTimer;

void setup() {
  pinMode(motorPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(inhibitPin, OUTPUT);
  
  Serial.begin(4800);
  
  if (shouldPrint) {
    Serial.println("Getting started!"); 
  }
  
  writeToMotor();
  writeEnabledPin();
  resetLoopTimer();
}

void loop() {  
  if (!shouldLoop && cyclesCompleted > 0) {
    return; // get out of here! 
  }
   
  // ramp from 0 -> max velocity
  if (loopState == RAMPING_UP && isLoopTimerExpired(rampStepDelay)) {
    current_pwm += rampUpIncrement;
    writeToMotor();
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
    writeToMotor();
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

/// Pins
void writeEnabledPin() {
  digitalWrite(enablePin, enabled? HIGH : LOW);
}

void writeToMotor() {
  analogWrite(motorPin, current_pwm);
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


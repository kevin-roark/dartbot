
// Ramp cycles as percentage between 0 -> 255 for uni mode
// 0 is max clockwise, 127 zero, 255 max ccw for bi mode
#define ZERO_DUTY 127

// loop behavior states
#define RAMPING_UP 0
#define SUSTAINING 1
#define RAMPING_DOWN 2
#define WAITING 3

// behavior configuration
int rampTime = 2000; // ms
int sustainTime = 5000; // ms
int timeBetweenLoops = 4000; // ms
boolean clockwise = true;
#define shouldLoop true

// derived variables
int rampStepDelay = rampTime / ZERO_DUTY;
int rampUpIncrement = clockwise? -1 : +1;
int rampUpLimit = clockwise? 1 : 254; // supposed to stay at 1 way from theoretical max
int rampDownIncrement = clockwise ? +1 : -1;

// state management
boolean enabled = false;
boolean inhibited = false;
int cyclesCompleted = 0;
int current_duty_cycle = ZERO_DUTY;
int loopState = RAMPING_UP;
unsigned long loopTimer;

void setup() {
  Serial.begin(4800);
      
  setupMotorPins();
  setupElectromagnet();
  setupLimitSwitches();
  
  printStartMessage();
  resetLoopTimer();
}

void loop() {
  if (!shouldLoop && cyclesCompleted > 0) {
    return; // get out of here!
  }

  // ramp from 0 -> max velocity
  if (loopState == RAMPING_UP && isLoopTimerExpired(rampStepDelay)) {
    current_duty_cycle += rampUpIncrement;
    writeToMotor(1, current_duty_cycle);
    writeToMotor(2, current_duty_cycle);
    printRampingUp(current_duty_cycle);

    if (current_duty_cycle == rampUpLimit) {
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
    current_duty_cycle += rampDownIncrement;
    writeToMotor(1, current_duty_cycle);
    writeToMotor(2, current_duty_cycle);
    printRampingDown(current_duty_cycle);

    if (current_duty_cycle == ZERO_DUTY) {
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
  printSustainState();
}

void transitionToWaiting() {
  loopState = WAITING;
  cyclesCompleted += 1;
  printWaitingState();
}

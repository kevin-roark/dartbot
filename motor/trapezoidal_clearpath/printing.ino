
/// Configuration
#define shouldPrint true

/// API
void printStartMessage() {
  if (shouldPrint) {
    Serial.println("Getting started!");
  } 
}

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

void printWaitingState() {
  if (shouldPrint) {
    Serial.print("completed cycle ");
    Serial.print(cyclesCompleted);
    Serial.print("! Now waiting for ");
    Serial.print(timeBetweenLoops);
    Serial.println(" ms");
  } 
}

void printSustainState() {
  if (shouldPrint) {
    Serial.print("sustaining with pwm ");
    Serial.print(current_duty_cycle);
    Serial.print(" for ");
    Serial.print(sustainTime);
    Serial.println(" ms");
  } 
}

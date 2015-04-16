
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

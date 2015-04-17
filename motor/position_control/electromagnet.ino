
/// Configuration
#define electromagnet_pin 11

/// API
void setupElectromagnet() {
  pinMode(electromagnet_pin, OUTPUT);
  writeElectroMagnet(true);
}

void writeElectroMagnet(bool on) {
  digitalWrite(electromagnet_pin, on? HIGH : LOW);
  Serial.print("SET ELECTROMAGNET ");
  printPinState(on);
}

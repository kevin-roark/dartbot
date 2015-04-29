
// optical limit switch config:
// anode (orange) should wire to a 250 ohm resistor, the other end of the resistor to a arduino output pin.
// collector (white) should wire to pullup digital input.
// cathode (green) should wire to a arduino ground pin.
// emitter (blue) wires to arduino ground pin.
// helpful: https://arduino-info.wikispaces.com/Opto-Switch

#define anodePin 12
#define collectorPin 13

void setup() {
  Serial.begin(9600);
  
  pinMode(anodePin, OUTPUT);
  pinMode(collectorPin, INPUT_PULLUP);
  
  digitalWrite(anodePin, HIGH);
}

void loop() {
  bool on = digitalRead(collectorPin);
  printPinState(on);
}

void printPinState(boolean on) {
  Serial.println(on? "HIGH" : "LOW");
}

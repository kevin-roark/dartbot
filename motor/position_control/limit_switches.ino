
// optical limit switch config:
// anode (orange) should wire to a 250 ohm resistor, the other end of the resistor to a arduino output pin.
// cathode (green) should wire to a arduino ground pin.
// collector (white) should wire to pullup digital input.
// emitter (blue) wires to arduino ground pin.

/// Configuration
#define proximalHomePhysicalLimitSwitch_pin 12
#define proximalSafetyPhysicalLimitSwitch_pin 13
#define distalHomeOpticalLimitSwitch_pin 7
#define distalSafetyOpticalLimitSwitch_pin 8

/// State management
bool setProximalHome = false;
bool setDistalHome = false;

/// API
void setupLimitSwitches() {
  pinMode(proximalHomePhysicalLimitSwitch_pin, INPUT_PULLUP);
  pinMode(proximalSafetyPhysicalLimitSwitch_pin, INPUT_PULLUP);

  pinMode(distalHomeOpticalLimitSwitch_pin, INPUT);
  pinMode(distalSafetyOpticalLimitSwitch_pin, INPUT);
}

void checkLimitSwitches() {
  // proximal home switch (physical)
  if (!setProximalHome && digitalRead(proximalHomePhysicalLimitSwitch_pin) == LOW) {
    setMotorHome(1, true);
    Serial.println("proximal motor is home");
    setProximalHome = true;
  }

  // distal home switch (optical)
  if (!setDistalHome && digitalRead(distalHomeOpticalLimitSwitch_pin) == HIGH) {
    setMotorHome(2, true);
    Serial.println("distal motor is home");
    setDistalHome = true;
  }

  // proximal safety switch (physical)
  if (digitalRead(proximalSafetyPhysicalLimitSwitch_pin) == LOW) {
    setEnabled(false);
    Serial.print("SAFETY LIMIT SWITCH HIT: ");
    Serial.println(proximalSafetyPhysicalLimitSwitch_pin);
  }

  // distal safety switch (optical)
  if (digitalRead(distalSafetyOpticalLimitSwitch_pin) == HIGH) {
    setEnabled(false);
    Serial.print("SAFETY LIMIT SWITCH HIT: ");
    Serial.println(distalSafetyOpticalLimitSwitch_pin);
  }
}

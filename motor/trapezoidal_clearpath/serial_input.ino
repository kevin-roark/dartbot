
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
        
      case '5':
      case '6':
        writeElectroMagnet(inChar == '6');
        break;
    }
  }
}

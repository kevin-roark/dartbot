
/// SerialEvent called whenever key is pressed, essentially. Runs between loop() calls
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char) Serial.read();
    switch (inChar) {

      // enable control
      case '1':
      case '2':
        bool on = (inChar == '2');
        setEnabled(on);
        break;

      // homing control
      case '3':
      case '4':
        bool home = (inChar == '4');
        setHome(home);
        break;

      // position control
      case '5':
        goToA();
        break;
      case '6':
        goToB();
        break;

      // limit switch simulation
      case '7':
        activateLimitPin(12);
        break;
      case '8':
        deactivateLimitPin();
        break;
    }
  }
}

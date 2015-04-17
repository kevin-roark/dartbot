
/// SerialEvent called whenever key is pressed, essentially. Runs between loop() calls
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char) Serial.read();
    switch (inChar) {

      // enable control
      case '1':
      case '2':
        setEnabled(inChar == '2');
        break;

      // homing control
      case '3':
      case '4':
        setHome(inChar == '4');
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
        activateLimitPin(12); // motor 1 backside
        break;
      case '8':
        activateLimitPin(A1); // motor 2 backside
        break;
      case '9':
        activateLimitPin(13); // motor 2 frontside, should disable both
        break;
      case '0':
        deactivateLimitPin(); // depression of le pin
        break;
    }
  }
}

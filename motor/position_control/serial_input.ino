
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
        //setHome(inChar == '4');
        break;

      // position control
      case '5':
        goToA();
        break;
      case '6':
        goToB();
        break;
    }
  }
}

int sensorPin = 2;
int objectCount = 0;
int sensorState = HIGH;
int lastSensorState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 200;

void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
  Serial.println("System Started");
  Serial.println("Waiting for object detection...");
}

void loop() {
  // 시리얼 명령 처리 (추가된 부분)
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("SET:")) {
      String valueStr = command.substring(4);
      int newValue = valueStr.toInt();
      objectCount = newValue;
      Serial.print("Count set to: ");
      Serial.println(objectCount);
    }
    else if (command == "RESET") {
      objectCount = 0;
      Serial.println("Count reset to 0");
    }
  }

  // 센서 값 읽기
  int reading = digitalRead(sensorPin);

  // 디바운싱 로직
  if (reading != lastSensorState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != sensorState) {
      sensorState = reading;

      // LOW 상태에서 물체 감지
      if (sensorState == LOW) {
        objectCount++;
        Serial.print("COUNT:");
        Serial.println(objectCount);
      }
    }
  }
  
  lastSensorState = reading;
}

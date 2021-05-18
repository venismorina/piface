#include <Servo.h>

Servo myservo; 
const int buzzer = 8;
int pos = 0;  

void setup() {
  Serial.begin(9600);
  pinMode(buzzer, OUTPUT); 
  detect();
}

void detect(){
  
   myservo.attach(9);  

  tone(buzzer, 1500); 
  delay(200);        
  noTone(buzzer);    
  delay(1000); 

  for (pos = 0; pos <= 90; pos += 1) 
  myservo.write(pos); 
  delay(1000);
  tone(buzzer, 1000); 
  delay(200);        
  noTone(buzzer);               
  delay(1500); 

  for (pos = 90; pos >= 0; pos -= 1)  
  myservo.write(pos);              
  delay(400);  
  }

void loop() {
   if (Serial.available() > 0) {
    String data = "0";
    data = Serial.readStringUntil('\n');
    if (data == "1"){
      detect();
    }                  
   }
}

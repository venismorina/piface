#include <LiquidCrystal.h>


LiquidCrystal lcd = LiquidCrystal(2, 3, 4, 5, 6, 7);

String sinjal = "";
String emri = "";
int delaynr = 0;

bool isEmri = true;

void setup() {
  Serial.begin(9600);
  Serial.println("Ready");
  lcd.begin(16, 2);
}
void loop() {


  if (Serial.available() > 0) {

    for(int i=1; i<=3; i++) {
        String data = Serial.readStringUntil('\n');
        if(i == 1){
          delaynr = data.toInt();
        }
        if(i == 2){
          sinjal = data;
        }
        if(i == 3){
          emri = data;
        }
    }
    

    lcd.setCursor(0, 0);
    lcd.print(sinjal);
    lcd.setCursor(0, 1);
    lcd.print(emri);
    
    delay(delaynr);

    lcd.setCursor(0, 0);
    lcd.print("                       ");
    lcd.setCursor(0, 1);
    lcd.print("                       ");


  }




}

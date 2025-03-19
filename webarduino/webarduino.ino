// Definice pinů pro ovládání motorů
const int motorA1 = 8;
const int motorA2 = 9;
const int motorB1 = 10;
const int motorB2 = 11;
const int motorC1 = 7;
const int motorC2 = 6;
const int motorD1 = 5;
const int motorD2 = 4;

// Definice pinů pro ultrazvukový senzor
const int trigPin = 2;
const int echoPin = 3;

// Proměnné pro řízení
String control_mode = "manual";  // Režim ovládání (manual/automatic/line_following)

void setup() {
  // Nastavení pinů motorů jako výstupy
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  pinMode(motorC1, OUTPUT);
  pinMode(motorC2, OUTPUT);
  pinMode(motorD1, OUTPUT);
  pinMode(motorD2, OUTPUT);

  // Nastavení pinů pro ultrazvukový senzor
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Nastavení sériové komunikace
  Serial.begin(9600);

  // Zastavení motorů při startu
  stop();
}

void loop() {
  // Kontrola, zda jsou dostupné příkazy ze sériové linky
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Přečtení příkazu
    command.trim();  // Odstranění bílých znaků

    // Přepínání režimů
    if (command == "MANUAL") {
      control_mode = "manual";
      Serial.println("Režim přepnut na: Manuální");
    } else if (command == "AUTO") {
      control_mode = "automatic";
      Serial.println("Režim přepnut na: Automatický");
    } else if (command == "LINE") {
      control_mode = "line_following";
      Serial.println("Režim přepnut na: Jízda podle čáry");
    } else {
      // Zpracování pohybových příkazů
      processCommand(command[0]);
    }
  }

  // Automatický režim
  if (control_mode == "automatic") {
    autoControl();
  }
}

// Funkce pro automatické řízení
void autoControl() {
  long distance = getDistance();  // Získání vzdálenosti od překážky

  if (distance > 30) {  // Pokud není překážka blíž než 30 cm
    dopredu();  // Pohybuj se dopředu
    Serial.println("Pohyb dopředu");
  } else {  // Pokud je překážka blíž než 30 cm
    stop();  // Zastav
    Serial.println("Zastavení - překážka detekována");

    // Vyhýbání se překážce
    vyhnutiSePrekazce();
  }
}

// Funkce pro získání vzdálenosti od překážky
long getDistance() {
  // Nastavení trig pinu na LOW a čekání 2 mikrosekundy
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Nastavení trig pinu na HIGH na 10 mikrosekund
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Měření doby, za kterou se vrátí echo
  long duration = pulseIn(echoPin, HIGH);

  // Výpočet vzdálenosti v centimetrech
  long distance = duration / 58;

  Serial.print("Vzdálenost: ");
  Serial.print(distance);
  Serial.println(" cm");

  return distance;
}

// Funkce pro vyhýbání se překážce
void vyhnutiSePrekazce() {
  stop();  // Zastav
  delay(500);  // Počkej 500 ms

  // Otoč doleva
  left_side_way();
  Serial.println("Otáčení doleva");
  delay(500);  // Počkej 500 ms

  // Zkontroluj vzdálenost po otočení
  long distance = getDistance();

  if (distance <= 30) {  // Pokud je stále překážka
    // Otoč doprava
    right_side_way();
    Serial.println("Otáčení doprava");
    delay(1000);  // Počkej 1 s
  }
}

// Funkce pro zpracování příkazů
void processCommand(char command) {
  switch (command) {
    case 'F':  // Příkaz pro pohyb dopředu
      if (control_mode == "manual" || control_mode == "line_following") {
        dopredu();
        Serial.println("Pohyb dopředu");
      }
      break;
    case 'B':  // Příkaz pro pohyb dozadu
      if (control_mode == "manual") {
        dozadu();
        Serial.println("Pohyb dozadu");
      }
      break;
    case 'L':  // Příkaz pro pohyb vlevo
      if (control_mode == "manual" || control_mode == "line_following") {
        left_side_way();
        Serial.println("Otáčení doleva");
      }
      break;
    case 'R':  // Příkaz pro pohyb vpravo
      if (control_mode == "manual" || control_mode == "line_following") {
        right_side_way();
        Serial.println("Otáčení doprava");
      }
      break;
    case 'S':  // Příkaz pro zastavení
      stop();
      Serial.println("Zastavení");
      break;
    default:
      Serial.println("Neznámý příkaz");
      break;
  }
}



// Funkce pro pohyb dopředu
void dopredu() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
  digitalWrite(motorC1, HIGH);
  digitalWrite(motorC2, LOW);
  digitalWrite(motorD1, HIGH);
  digitalWrite(motorD2, LOW);
}

// Funkce pro pohyb dozadu
void dozadu() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
  digitalWrite(motorC1, LOW);
  digitalWrite(motorC2, HIGH);
  digitalWrite(motorD1, LOW);
  digitalWrite(motorD2, HIGH);
}

// Funkce pro pohyb vlevo (boční)
void left_side_way() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
  digitalWrite(motorC1, HIGH);
  digitalWrite(motorC2, LOW);
  digitalWrite(motorD1, LOW);
  digitalWrite(motorD2, HIGH);
}

// Funkce pro pohyb vpravo (boční)
void right_side_way() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
  digitalWrite(motorC1, LOW);
  digitalWrite(motorC2, HIGH);
  digitalWrite(motorD1, HIGH);
  digitalWrite(motorD2, LOW);
}

// Funkce pro zastavení pohybu
void stop() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, LOW);
  digitalWrite(motorC1, LOW);
  digitalWrite(motorC2, LOW);
  digitalWrite(motorD1, LOW);
  digitalWrite(motorD2, LOW);
}

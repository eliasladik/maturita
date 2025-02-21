String control_mode = "manual"; 
// Definice pinů pro ovládání motorů
const int motorA1 = 8;
const int motorA2 = 9;

const int motorB1 = 10;
const int motorB2 = 11;

const int motorC1 = 7;
const int motorC2 = 6;

const int motorD1 = 5;
const int motorD2 = 4;

// Proměnné pro vzdálenost
int pTrig = 2;
int pEcho = 3;
long odezva, vzdalenost;

String mode = "MANUAL";

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

  pinMode(pTrig, OUTPUT);
  pinMode(pEcho, INPUT);

  // Nastavení sériové komunikace
  Serial.begin(9600);
  
  stop();
}

void loop() {
  // Kontrola, zda je dostupný nějaký příkaz přes sériovou linku
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Odstranění bílých znaků
    if (command == "AUTO") {
      mode = "AUTO";
      Serial.println("Režim přepnut na: Automatický");
    } else if (command == "MANUAL") {
      mode = "MANUAL";
      Serial.println("Režim přepnut na: Manuální");
    } else {
      processCommand(command[0]); // Zpracování pohybových příkazů
    }
  }

  // Pokud je aktivní automatické ovládání, spustí se logika automatického řízení
  if (mode == "AUTO") {
    autoControl();
  }
}

// Funkce pro zpracování příkazů ze sériové linky
void processCommand(char command) {
  switch (command) {
    case 'F':  // Příkaz pro pohyb dopředu
      if (control_mode == "manual") {
        dopredu();  // Manuální režim, pohyb dopředu
      }
      break;
    case 'B':  // Příkaz pro pohyb dozadu
      if (control_mode == "manual") {
        dozadu();  // Manuální režim, pohyb dozadu
      }
      break;
    case 'L':  // Příkaz pro pohyb vlevo
      if (control_mode == "manual") {
        left_side_way();  // Manuální režim, pohyb vlevo
      }
      break;
    case 'R':  // Příkaz pro pohyb vpravo
      if (control_mode == "manual") {
        right_side_way();  // Manuální režim, pohyb vpravo
      }
      break;
    case 'S':  // Příkaz pro zastavení
      if (control_mode == "manual") {
        stop();  // Manuální režim, zastavení
      }
      break;
    case 'M':  // Příkaz pro přepnutí na automatický režim
      control_mode = "automatic";
      Serial.println("Přepnuto na automatický režim");
      break;
    case 'N':  // Příkaz pro přepnutí na manuální režim
      control_mode = "manual";
      Serial.println("Přepnuto na manuální režim");
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
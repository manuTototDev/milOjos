#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  150 
#define SERVOMAX  600 

const int CH_BASE = 0, CH_HOMBRO = 1, CH_CAMARA_V = 2, CH_CAMARA_H = 3;

// --- VARIABLES DE CONTROL ---
float velocidadBusqueda = 0.04; // Tu velocidad perfecta
float posBase = 90, posHombro = 60, posCamV = 45;
float targetBase = 90, targetHombro = 60, targetCamV = 45;

unsigned long ultimoPulsoSerial = 0;
unsigned long tiempoUltimoCambioDestino = 0;
bool modoSeguimiento = false;

void setup() {
  Serial.begin(115200);
  pwm.begin();
  pwm.setPWMFreq(50);
  actualizarServos();
}

void loop() {
  if (Serial.available() > 0) {
    // Lectura de los 4 valores desde Python
    float pB = Serial.parseFloat();
    float pH = Serial.parseFloat();
    float pV = Serial.parseFloat();
    int modo = Serial.parseInt(); // El "Interruptor" (1=Rostro, 0=Busqueda)

    ultimoPulsoSerial = millis();

    if (modo == 1) {
      modoSeguimiento = true;
      posBase = pB;
      posHombro = pH;
      posCamV = pV;
      
      // Sincronizamos los targets de búsqueda para que no haya "latigazo" al salir
      targetBase = posBase;
      targetHombro = posHombro;
      targetCamV = posCamV;
      
      actualizarServos();
    } else {
      modoSeguimiento = false;
    }
  } 

  // MODO BÚSQUEDA: Solo si Python no detecta nada Y han pasado 2 segundos de silencio
  if (!modoSeguimiento && (millis() - ultimoPulsoSerial > 2000)) {
    modoBusquedaOrganica();
  }
}

void modoBusquedaOrganica() {
  if (millis() - tiempoUltimoCambioDestino > random(1500, 3000)) {
    targetBase   = random(40, 140); 
    targetHombro = random(45, 80);  
    targetCamV   = random(35, 75);  
    tiempoUltimoCambioDestino = millis();
  }

  posBase   += (targetBase - posBase) * velocidadBusqueda;
  posHombro += (targetHombro - posHombro) * velocidadBusqueda;
  posCamV   += (targetCamV - posCamV) * velocidadBusqueda;

  actualizarServos();
  delay(15); 
}

void actualizarServos() {
  pwm.setPWM(CH_BASE, 0, map(int(posBase), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH_HOMBRO, 0, map(int(posHombro), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH_CAMARA_V, 0, map(int(posCamV), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH_CAMARA_H, 0, map(int(posCamV), 0, 180, SERVOMIN, SERVOMAX));
}
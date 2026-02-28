#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  150 
#define SERVOMAX  600 

const int MIN_B = 15, MAX_B = 165;
const int MIN_H = 45, MAX_H = 85;
const int MIN_V = 15, MAX_V = 140;

// Estado de los 16 canales (4 brazos x 4 servos)
float pos[16] = {90, 60, 45, 90, 90, 60, 45, 90, 90, 60, 45, 90, 90, 60, 45, 90};
unsigned long ultimoPulsoSerial = 0;
bool modoManual = false;

// Variables de búsqueda
float t[16] = {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500};
float tVel = 0;
unsigned long ultimoSalto = 0;

float noise1D(float x) {
  int x0 = (int)x;
  float t_val = x - x0;
  float g0 = ((x0 * 1103515245 + 12345) & 0x7FFFFFFF) / 2147483647.0;
  float g1 = (((x0 + 1) * 1103515245 + 12345) & 0x7FFFFFFF) / 2147483647.0;
  return g0 + (3*t_val*t_val - 2*t_val*t_val*t_val) * (g1 - g0);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);
  pwm.begin();
  pwm.setPWMFreq(50);
  actualizarServos();
}

void loop() {
  unsigned long ahora = millis();

  // Si hay muchos datos, leemos el más reciente para evitar lag
  if (Serial.available() > 0) {
    if (Serial.peek() == '$') {
      Serial.read(); // Quitar el '$'
      String datos = Serial.readStringUntil('\n');
      
      // Parsear la cadena de comas
      int indice = 0;
      int startPos = 0;
      int endPos = datos.indexOf(',');
      
      while (endPos != -1 && indice < 16) {
        pos[indice] = datos.substring(startPos, endPos).toFloat();
        startPos = endPos + 1;
        endPos = datos.indexOf(',', startPos);
        indice++;
      }
      
      // El último valor es el modo
      if (indice >= 12) { // Al menos 3 brazos
        int m = datos.substring(startPos).toInt();
        if (m == 1) {
          modoManual = true;
          ultimoPulsoSerial = ahora;
          
          // En modo manual NO aplicamos límites de seguridad (MIN_B, MAX_H, etc)
          // Solo limitamos al rango físico del servo (0-180)
          for(int i=0; i<16; i++) {
            pos[i] = constrain(pos[i], 0, 180);
          }
        }
      }
    } else {
      Serial.read(); // Limpiar basura si no empieza con $
    }
  }

  // Failsafe: SI no hay serial en 3 segundos, volver a búsqueda suave
  if (ahora - ultimoPulsoSerial > 3000) {
    if (modoManual) {
      modoManual = false;
      // Reiniciar tiempos de búsqueda para que el salto no sea brusco
      for(int i=0; i<16; i++) t[i] = random(0, 1000);
    }
  }

  if (!modoManual) {
    tVel += 0.008; 
    float dt = map(pow(noise1D(tVel), 1.5) * 1000, 0, 1000, 5, 40) / 1000.0;
    if (ahora - ultimoSalto > 7000) {
      dt = 0.5;
      if (ahora - ultimoSalto > 7600) ultimoSalto = ahora;
    }
    for(int i=0; i<16; i++) {
        t[i] += dt * (1.0 + (i * 0.03));
        int tipo = i % 4;
        if (tipo == 0 || tipo == 3) pos[i] = map(noise1D(t[i]) * 100, 0, 100, MIN_B, MAX_B);
        else if (tipo == 1)         pos[i] = map(noise1D(t[i]) * 100, 0, 100, MIN_H, MAX_H);
        else if (tipo == 2)         pos[i] = map(noise1D(t[i]) * 100, 0, 100, MIN_V, MAX_V);
    }
  }

  actualizarServos();
  // Eliminamos el delay(15) para que el loop sea lo más rápido posible
}

void actualizarServos() {
  for(int i=0; i<16; i++) {
    pwm.setPWM(i, 0, map(int(pos[i]), 0, 180, SERVOMIN, SERVOMAX));
  }
}
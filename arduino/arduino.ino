#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Servo.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
Servo servoExtra1;
Servo servoExtra2;

#define SERVOMIN  150 
#define SERVOMAX  600 

const int CH_BASE = 0, CH_HOMBRO = 1, CH_CAMARA_V = 2, CH_CAMARA_H = 3;
const int CH2_BASE = 4, CH2_HOMBRO = 5, CH2_CAMARA_V = 6, CH2_CAMARA_H = 7;

// --- VARIABLES PERLIN ---
float tBase = 0, tHombro = 100, tCam = 200;
float t2Base = 300, t2Hombro = 400, t2Cam = 500;
float tVel = 0; // Ruido para la velocidad
float velocidadActual = 0.04;
unsigned long ultimoSalto = 0;

// --- VARIABLES DE CONTROL ARM 1 ---
float posBase = 90, posHombro = 60, posCamV = 45;
float targetBase = 90, targetHombro = 60, targetCamV = 45;

// --- VARIABLES DE CONTROL ARM 2 ---
float pos2Base = 90, pos2Hombro = 60, pos2CamV = 45;

unsigned long ultimoPulsoSerial = 0;
bool modoSeguimiento = false;

// Función de ruido simple (Perlin 1D estilo)
float noise1D(float x) {
  int x0 = (int)x;
  float t = x - x0;
  float g0 = ((x0 * 1103515245 + 12345) & 0x7FFFFFFF) / 2147483647.0;
  float g1 = (((x0 + 1) * 1103515245 + 12345) & 0x7FFFFFFF) / 2147483647.0;
  return g0 + (3*t*t - 2*t*t*t) * (g1 - g0); // Interpolación suave (smoothstep)
}

void setup() {
  Serial.begin(115200);
  pwm.begin();
  pwm.setPWMFreq(50);

  // Servos adicionales en pines directos
  servoExtra1.attach(30);
  servoExtra2.attach(31);
  servoExtra1.write(0);
  servoExtra2.write(0);

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

  // --- LÓGICA DE VELOCIDAD Y SALTOS ---
  unsigned long ahora = millis();
  
  // Ruido para determinar la velocidad actual (suave con cambios)
  tVel += 0.008; 
  float nVel = noise1D(tVel);
  // Usamos una curva de potencia para favorecer velocidades suaves con picos rápidos
  float nVelPower = pow(nVel, 1.5); 
  velocidadActual = map(nVelPower * 1000, 0, 1000, 4, 38) / 1000.0; // De 0.004 a 0.038

  // Incremento de tiempo en el ruido (determina qué tan rápido "viajamos")
  float dt = velocidadActual; // Ahora la velocidad es orgánica

  // Cambio brusco cada 7 segundos
  if (ahora - ultimoSalto > 7000) {
    dt = 0.5; // Salto brusco durante este frame
    if (ahora - ultimoSalto > 7500) { // El salto dura medio segundo
      ultimoSalto = ahora;
    }
  }

  // MODO BÚSQUEDA ARM 1: Solo si Python no detecta nada Y han pasado 2 segundos de silencio
  if (!modoSeguimiento && (ahora - ultimoPulsoSerial > 2000)) {
    moverArmConRuido(1, dt);
  }

  // MODO BÚSQUEDA ARM 2: Siempre activo
  moverArmConRuido(2, dt);

  actualizarServos();
  delay(15);
}

void moverArmConRuido(int arm, float dt) {
  if (arm == 1) {
    tBase += dt; tHombro += dt; tCam += dt;
    posBase   = map(noise1D(tBase) * 100, 0, 100, 15, 165);
    posHombro = map(noise1D(tHombro) * 100, 0, 100, 45, 80);
    posCamV   = map(noise1D(tCam) * 100, 0, 100, 10, 140);
  } else {
    t2Base += dt; t2Hombro += dt; t2Cam += dt;
    pos2Base   = map(noise1D(t2Base) * 100, 0, 100, 15, 165);
    pos2Hombro = map(noise1D(t2Hombro) * 100, 0, 100, 45, 80); 
    pos2CamV   = map(noise1D(t2Cam) * 100, 0, 100, 10, 140);
  }
}

void actualizarServos() {
  // ARM 1
  pwm.setPWM(CH_BASE, 0, map(int(posBase), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH_HOMBRO, 0, map(int(posHombro), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH_CAMARA_V, 0, map(int(posCamV), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH_CAMARA_H, 0, map(int(posCamV), 0, 180, SERVOMIN, SERVOMAX));

  // ARM 2
  pwm.setPWM(CH2_BASE, 0, map(int(pos2Base), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH2_HOMBRO, 0, map(int(pos2Hombro), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH2_CAMARA_V, 0, map(int(pos2CamV), 0, 180, SERVOMIN, SERVOMAX));
  pwm.setPWM(CH2_CAMARA_H, 0, map(int(pos2CamV), 0, 180, SERVOMIN, SERVOMAX));
}
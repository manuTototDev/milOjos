"""
servo_controller.py — Mil Ojos v3.0
Control de 9 brazos × 4 servos = 36 servos totales.
Protocolo: $s1,s2,s3,s4, ... ,s36,1\n  (valores en grados, separados por coma)
Configuracion de brazos cargada desde arm_config.json.

Modo búsqueda (sin rostro):
  La cámara (base del Brazo 1) barre suavemente 90° a la izquierda y regresa.
  Rango de barrido: SCAN_LEFT (0°) ↔ SCAN_RIGHT (90° = home).
  Velocidad controlada por SCAN_STEP_DEG por tick (~30 Hz).

Modo seguimiento (con rostro):
  El barrido se detiene; los servos siguen al rostro con SMOOTH_FACE.
"""

import serial
import threading
import numpy as np
import time
import os
import json
import math

# ── Configuración global ──────────────────────────────────────────────────────
NUM_BRAZOS       = 9
SERVOS_POR_BRAZO = 4
TOTAL_SERVOS     = NUM_BRAZOS * SERVOS_POR_BRAZO   # 36

COM_PORT    = os.environ.get("ARDUINO_PORT", "COM6")
BAUD_RATE   = 115200
SMOOTH_FACE = 0.65   # suavizado con rostro: incrementado para centrar el rostro casi instantáneamente
SMOOTH_IDLE = 0.20   # suavizado en búsqueda: incrementado para movimientos rápidos ("animal")

# ── Parámetros de barrido (modo búsqueda) ────────────────────────────────────
# La cámara se renderiza espejada (scaleX(-1)):
#   izquierda visual = base aumenta (90° → 180°)
#   derecha visual   = base disminuye (90° → 0°)
SCAN_HOME      = 90.0   # posición de reposo (centro)
SCAN_LIMIT     = 180.0  # límite del barrido: 90° a la izquierda (visual)
SCAN_STEP_DEG  = 0.16   # grados por tick (~30 Hz → ~0.08°/tick → barrido lento ~37 s)
# Sube SCAN_STEP_DEG para un barrido más rápido (ej. 0.2 → ~7 s).

# ── Cargar configuración de brazos desde arm_config.json ─────────────────────
_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arm_config.json")

with open(_CONFIG_FILE, "r", encoding="utf-8") as _f:
    _cfg = json.load(_f)

REST_POSITIONS: list[list[float]] = [
    [float(v) for v in arm["home"]] for arm in _cfg["arms"]
]

ACTIVE_ARMS: set[int] = {
    arm["id"] for arm in _cfg["arms"] if arm.get("active", False)
}

ARM_LABELS: dict[int, str] = {
    arm["id"]: arm["label"] for arm in _cfg["arms"]
}

print(f"[Config] {len(_cfg['arms'])} brazos cargados desde {_CONFIG_FILE}")
print(f"[Config] Activos: { {ARM_LABELS[i]: REST_POSITIONS[i] for i in ACTIVE_ARMS} }")


class ServoController:
    """
    Gestiona las posiciones de los 9 brazos y la comunicación con Arduino.
    Corre en un hilo propio a ~30 Hz.
    """

    def __init__(self):
        # Estado actual (suavizado) y objetivo para cada brazo
        self.pos    = [list(REST_POSITIONS[i]) for i in range(NUM_BRAZOS)]
        self.target = [list(REST_POSITIONS[i]) for i in range(NUM_BRAZOS)]

        self.face_detected = False   # ¿hay rostro actualmente?
        self.arduino = None
        self._lock   = threading.Lock()
        self._running = False

        # ── Estado del barrido de búsqueda ────────────────────────────────────
        # La base del Brazo 0 oscila entre SCAN_HOME y SCAN_LIMIT cuando no hay rostro.
        self._scan_dir = 1    # +1 → moviéndose hacia SCAN_LIMIT (izquierda visual)
        self._scan_pos = REST_POSITIONS[0][0]  # arranca desde el home de la base

        self.last_face_time = 0.0
        self.last_velocities = [[0.0]*SERVOS_POR_BRAZO for _ in range(NUM_BRAZOS)]
        self.time_start = time.time()
        
        # Estado para movimiento orgánico (sacádico)
        self.next_saccade_time = 0.0
        self.saccade_target_base = SCAN_HOME
        self.saccade_target_codo = REST_POSITIONS[0][2] if len(REST_POSITIONS) > 0 else 90.0

        self._connect()

    # ── Conexión ──────────────────────────────────────────────────────────────
    def _connect(self):
        try:
            self.arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.01)
            time.sleep(2)
            print(f"[Servos] Arduino conectado en {COM_PORT}")
        except Exception as e:
            self.arduino = None
            print(f"[Servos] Arduino no disponible ({e}). Modo simulación.")

    # ── API pública: actualizar objetivo de un brazo ──────────────────────────
    def set_target(self, arm_index: int, servos: list[float]):
        """
        Actualiza el target de un brazo específico.
        arm_index: 0-based (0 = Brazo 1)
        servos: [base, hombro, codo, muñeca] en grados
        """
        if arm_index not in ACTIVE_ARMS:
            return   # brazo no activo, ignorar
        with self._lock:
            for i, v in enumerate(servos[:SERVOS_POR_BRAZO]):
                v_clipped = float(np.clip(v, 0, 180))
                # Suavizar la inercia para saber en qué dirección se movía
                delta = v_clipped - self.target[arm_index][i]
                self.last_velocities[arm_index][i] = self.last_velocities[arm_index][i] * 0.7 + delta * 0.3
                self.target[arm_index][i] = v_clipped

    def set_target_override(self, arm_index: int, servo_index: int, angle: float):
        """Fuerza un servo específico (bypass ACTIVE_ARMS). angle 0-180."""
        with self._lock:
            self.target[arm_index][servo_index] = float(np.clip(angle, 0, 180))

    def set_all_servos(self, angle: float):
        """Mueve todos los servos al ángulo indicado."""
        with self._lock:
            for arm in range(NUM_BRAZOS):
                for s in range(SERVOS_POR_BRAZO):
                    self.target[arm][s] = float(np.clip(angle, 0, 180))

    def set_face_detected(self, detected: bool):
        with self._lock:
            # Si pasamos de no detectar a detectar, detenemos el brazo en su posición física actual
            if detected and not self.face_detected:
                for s in range(SERVOS_POR_BRAZO):
                    self.target[0][s] = self.pos[0][s]
                    self.last_velocities[0][s] = 0.0
                self.saccade_target_base = self.pos[0][0]
                self.saccade_target_codo = self.pos[0][2]

            if detected:
                self.last_face_time = time.time()
            self.face_detected = detected

    def get_status(self) -> dict:
        """Retorna estado actual para el endpoint /servo/status"""
        with self._lock:
            return {
                "connected": self.arduino is not None,
                "port": COM_PORT,
                "active_arms": sorted(ACTIVE_ARMS),
                "num_brazos": NUM_BRAZOS,
                "positions": [list(self.pos[i]) for i in range(NUM_BRAZOS)],
                "targets":   [list(self.target[i]) for i in range(NUM_BRAZOS)],
            }

    # ── Loop de control ───────────────────────────────────────────────────────
    def start(self):
        self._running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        print("[Servos] Loop de control iniciado.")

    def stop(self):
        self._running = False
        if self.arduino:
            self.arduino.close()

    def _loop(self):
        """Suaviza posiciones y envía a Arduino a ~30 Hz."""
        while self._running:
            now = time.time()
            
            with self._lock:
                time_since_face = now - self.last_face_time
                if self.face_detected:
                    alpha = SMOOTH_FACE
                else:
                    if time_since_face < 3.0:
                        alpha = SMOOTH_FACE * 0.5  # Movimiento rápido pero un poco más suave al perder rostro
                    else:
                        alpha = SMOOTH_IDLE

                # ── Modo búsqueda: movimientos orgánicos del Brazo 0 ──────
                if not self.face_detected:
                    if time_since_face >= 3.0:
                        # Modo exploración orgánica ("animal buscando")
                        # Movimientos rápidos, sacádicos, con pausas cortas
                        if now > self.next_saccade_time:
                            import random
                            nuevo_base = self.saccade_target_base + random.uniform(-40, 40)
                            nuevo_codo = REST_POSITIONS[0][2] + random.uniform(-25, 25)
                            
                            # Mantener dentro de rangos razonables
                            self.saccade_target_base = float(np.clip(nuevo_base, 30, 150))
                            self.saccade_target_codo = float(np.clip(nuevo_codo, 40, 140))
                            
                            # Siguiente movimiento en un tiempo corto y aleatorio (0.2 a 0.8s)
                            self.next_saccade_time = now + random.uniform(0.2, 0.8)
                            
                        self.target[0][0] = self.saccade_target_base
                        self.target[0][2] = self.saccade_target_codo
                    else:
                        # Han pasado menos de 3 segundos desde la última vez que vimos un rostro
                        # Moverse rápidamente hacia la última dirección donde se vio al rostro (inercia amplificada)
                        self.target[0][0] += self.last_velocities[0][0] * 4.0
                        self.target[0][2] += self.last_velocities[0][2] * 4.0
                        self.target[0][0] = float(np.clip(self.target[0][0], 0, 180))
                        self.target[0][2] = float(np.clip(self.target[0][2], 0, 180))
                else:
                    # Rastreo activo (target gestionado externamente por set_target)
                    pass

                # ── Suavizado para todos los servos ──────────────────────────
                for arm in range(NUM_BRAZOS):
                    for s in range(SERVOS_POR_BRAZO):
                        cur = self.pos[arm][s]
                        tgt = self.target[arm][s]
                        self.pos[arm][s] = cur + (tgt - cur) * alpha
                        self.pos[arm][s] = float(np.clip(self.pos[arm][s], 0, 180))

                angles = [int(self.pos[arm][s])
                          for arm in range(NUM_BRAZOS)
                          for s in range(SERVOS_POR_BRAZO)]

            if self.arduino:
                # El código de Arduino actual espera exactamente 16 canales
                cmd = "$" + ",".join(map(str, angles[:16])) + ",1\n"
                try:
                    self.arduino.write(cmd.encode())
                except Exception as e:
                    print(f"[Servos] Error enviando: {e}")

            time.sleep(1 / 50)   # ~50 Hz — mayor resolución de movimiento

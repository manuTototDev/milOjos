"""
servo_controller.py — Mil Ojos v3.0
Control de 9 brazos × 4 servos = 36 servos totales.
Protocolo: $s1,s2,s3,s4, ... ,s36,1\n  (valores en grados, separados por coma)
Solo el Brazo 1 es activo. Los demás están en posición de reposo.
"""

import serial
import threading
import numpy as np
import time
import os

# ── Configuración global ──────────────────────────────────────────────────────
NUM_BRAZOS  = 9
SERVOS_POR_BRAZO = 4
TOTAL_SERVOS = NUM_BRAZOS * SERVOS_POR_BRAZO   # 36

COM_PORT    = os.environ.get("ARDUINO_PORT", "COM6")
BAUD_RATE   = 115200
SMOOTH_FACE = 0.22   # factor de suavizado cuando hay rostro
SMOOTH_IDLE = 0.03   # factor de suavizado en modo reposo

# ── Posiciones de reposo por brazo [base, hombro, codo, muñeca] ──────────────
REST_POSITIONS = [
    [90.0, 60.0, 70.0, 90.0],   # Brazo 1 — ACTIVO (tracking)
    [90.0, 60.0, 50.0, 90.0],   # Brazo 2 — reposo
    [90.0, 70.0, 60.0, 90.0],   # Brazo 3 — reposo
    [90.0, 65.0, 55.0, 90.0],   # Brazo 4 — reposo
    [90.0, 60.0, 50.0, 90.0],   # Brazo 5 — reposo
    [90.0, 70.0, 60.0, 90.0],   # Brazo 6 — reposo
    [90.0, 65.0, 55.0, 90.0],   # Brazo 7 — reposo
    [90.0, 60.0, 50.0, 90.0],   # Brazo 8 — reposo
    [90.0, 70.0, 60.0, 90.0],   # Brazo 9 — reposo
]

# Brazos activos (índice 0-based). Solo el 1 por ahora.
ACTIVE_ARMS = {0}   # ← agregar más índices aquí para activar más brazos


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
                self.target[arm_index][i] = float(np.clip(v, 20, 160))

    def set_face_detected(self, detected: bool):
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
            alpha = SMOOTH_FACE if self.face_detected else SMOOTH_IDLE

            with self._lock:
                for arm in range(NUM_BRAZOS):
                    for s in range(SERVOS_POR_BRAZO):
                        cur = self.pos[arm][s]
                        tgt = self.target[arm][s]
                        self.pos[arm][s] = cur + (tgt - cur) * alpha
                        self.pos[arm][s] = float(np.clip(self.pos[arm][s], 20, 160))

                angles = [int(self.pos[arm][s])
                          for arm in range(NUM_BRAZOS)
                          for s in range(SERVOS_POR_BRAZO)]

            if self.arduino:
                cmd = "$" + ",".join(map(str, angles)) + ",1\n"
                try:
                    self.arduino.write(cmd.encode())
                except Exception as e:
                    print(f"[Servos] Error enviando: {e}")

            time.sleep(1 / 30)   # ~30 Hz

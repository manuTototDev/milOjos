"""
brain_trainer.py — Mil Ojos v3.0
Red neuronal de refuerzo para seguimiento de rostro.
Recibe error normalizado (-1 a 1) y retorna steps para base y codo.
No depende de OpenCV ni de cámara local; el frontend provee los datos.
"""

import numpy as np
import os
import time

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PESOS_FILE = os.path.join(BASE_DIR, "pesos_robot.npy")
LR         = 0.02


class BrainTrainer:
    """
    Controlador de seguimiento para el Brazo 1.
    Entrada:  error_input = [err_x_rel, err_y_rel]  → valores entre -1 y 1
    Salida:   (step_v, step_h, status_msg)
    """

    def __init__(self):
        self.pesos              = np.zeros((2, 2))
        self.fase_calib         = 0
        self.timer_fase         = 0.0
        self.error_inicial_fase = np.zeros(2)
        self.aciertos           = 0
        self.fallos             = 0
        self.last_dist          = 0.0
        self.last_move          = np.zeros(2)
        self.load_pesos()

    # ── Persistencia ──────────────────────────────────────────────────────────
    def load_pesos(self):
        if os.path.exists(PESOS_FILE):
            try:
                self.pesos = np.load(PESOS_FILE)
                print(f"[Brain] Pesos cargados desde {PESOS_FILE}")
            except Exception:
                self.pesos = np.zeros((2, 2))

    def save_pesos(self):
        np.save(PESOS_FILE, self.pesos)

    def reset_pesos(self):
        self.pesos      = np.zeros((2, 2))
        self.fase_calib = 0
        self.save_pesos()
        print("[Brain] Pesos reseteados.")

    # ── Update principal ──────────────────────────────────────────────────────
    def update(self, error_input: np.ndarray, distancia_px: float, ahora: float):
        """
        Retorna (step_v, step_h, status_msg).
        step_v / step_h: grados a sumar al target del servo correspondiente.
        """
        step_v, step_h = 0.0, 0.0
        status_msg     = "SISTEMA LISTO"

        if self.fase_calib == 0:
            status_msg = "FASE 0: QUIETO — MIDIENDO"
            if self.timer_fase == 0:
                self.timer_fase = ahora
            if ahora - self.timer_fase > 2.0:
                self.fase_calib         = 1
                self.timer_fase         = ahora
                self.error_inicial_fase = error_input.copy()
                step_h                  = 10.0
                print("[Brain] Iniciando Fase 1 (Base)")

        elif self.fase_calib == 1:
            status_msg = "FASE 1: MIDIENDO BASE…"
            if ahora - self.timer_fase > 1.2:
                diff_err            = error_input - self.error_inicial_fase
                self.pesos[1, 0]    = diff_err[0] / 10.0
                self.pesos[1, 1]    = diff_err[1] / 10.0
                self.fase_calib     = 2
                self.timer_fase     = ahora
                self.error_inicial_fase = error_input.copy()
                step_v              = 10.0
                print("[Brain] Iniciando Fase 2 (Vertical)")

        elif self.fase_calib == 2:
            status_msg = "FASE 2: MIDIENDO CODO…"
            if ahora - self.timer_fase > 1.2:
                diff_err            = error_input - self.error_inicial_fase
                self.pesos[0, 0]    = diff_err[0] / 10.0
                self.pesos[0, 1]    = diff_err[1] / 10.0
                self.pesos          = -np.clip(self.pesos, -0.6, 0.6)
                self.fase_calib     = 3
                self.save_pesos()
                print("[Brain] Calibración exitosa.")

        elif self.fase_calib == 3:
            delta_dist = self.last_dist - distancia_px
            if self.last_dist > 0 and distancia_px > 30:
                if delta_dist > 0.8:
                    self.aciertos += 1
                    status_msg = "+++ PREMIO +++"
                    self.pesos += LR * np.outer(self.last_move * 0.1, error_input)
                elif delta_dist < -1.5:
                    self.fallos += 1
                    status_msg = "--- CASTIGO ---"
                    self.pesos -= LR * 2.0 * np.outer(self.last_move * 0.1, error_input)

            mov_raw = np.dot(self.pesos, error_input)
            step_v  = float(mov_raw[0] * 55)
            step_h  = float(mov_raw[1] * 55)

        self.last_dist  = distancia_px
        self.last_move  = np.array([step_v, step_h])
        return step_v, step_h, status_msg

    def get_state(self) -> dict:
        return {
            "fase_calib": self.fase_calib,
            "aciertos":   self.aciertos,
            "fallos":     self.fallos,
            "pesos":      self.pesos.tolist(),
        }

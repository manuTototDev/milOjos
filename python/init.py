import cv2
import serial
import time
import threading
import numpy as np
import os

if not os.path.exists('capturas'): os.makedirs('capturas')

class VideoStream:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.frame = None
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                # Rotación 90° Izquierda
                self.frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            else:
                self.stopped = True

    def read(self): return self.frame
    def stop(self): 
        self.stopped = True
        self.cap.release()

# --- SERIAL ---
try:
    arduino = serial.Serial('COM6', 115200, timeout=0.01)
    time.sleep(2)
except: 
    print("Error: Revisa el puerto COM6"); exit()

vs = VideoStream(0).start()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- AJUSTES DE PRECISIÓN ---
GANANCIA_X = 0.012   # Muy fino para que no oscile
GANANCIA_Y = 0.15    # Más alto para forzar el centrado vertical
DEADZONE_Y = 8       # Zona muerta más pequeña en Y para ser más exigente
MAX_STEP_Y = 3.0     # Permitimos pasos más grandes en Y para compensar inercia
SUAVIZADO_MOV = 0.15 

posBase, posHombro, posCamV = 90.0, 60.0, 45.0
targetBase, targetCamV = 90.0, 45.0
ultimo_avistamiento = time.time()

print("DEBUG Y: Revisa si el círculo rojo busca la línea blanca.")

try:
    while True:
        frame = vs.read()
        if frame is None: continue

        frame_small = cv2.resize(frame, (240, 320))
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 10, minSize=(50, 50))
        
        cx, cy = 120, 160 # Centro del frame
        ahora = time.time()

        # Dibujar guías de centro en pantalla
        cv2.line(frame_small, (0, cy), (240, cy), (255, 255, 255), 1) # Línea horizonte
        cv2.line(frame_small, (cx, 0), (cx, 320), (255, 255, 255), 1) # Línea vertical

        if len(faces) > 0:
            ultimo_avistamiento = ahora
            x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
            tx, ty = x + w//2, y + h//2 
            
            cv2.rectangle(frame_small, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(frame_small, (tx, ty), 5, (0, 0, 255), -1)

            # --- LÓGICA DE CENTRADO ---
            err_x = cx - tx
            err_y = cy - ty # Si la cara está arriba, ty < 160, err_y es positivo

            # Eje X
            if abs(err_x) > 10:
                targetBase += np.clip(err_x * GANANCIA_X, -2.0, 2.0)
            
            # Eje Y (Centrado Crítico)
            if abs(err_y) > DEADZONE_Y:
                # IMPORTANTE: Si el robot se mueve al revés en Y, cambia el signo de GANANCIA_Y
                paso_y = np.clip(err_y * GANANCIA_Y, -MAX_STEP_Y, MAX_STEP_Y)
                targetCamV += paso_y 
                
                # Debug en consola para ver valores reales
                # print(f"Error Y: {err_y} | Target Y: {int(targetCamV)}")

        else:
            # Modo Búsqueda
            if ahora - ultimo_avistamiento > 3.0:
                targetBase = 90 + 40 * np.sin(ahora * 0.5) # Escaneo sinusoidal suave
                targetCamV = 50

        # Suavizado
        posBase += (targetBase - posBase) * SUAVIZADO_MOV
        posCamV += (targetCamV - posCamV) * SUAVIZADO_MOV

        # Límites físicos
        posBase = np.clip(posBase, 15, 165)
        posCamV = np.clip(posCamV, 10, 140)
        
        # Envío
        cmd = f"{int(posBase)},{int(posHombro)},{int(posCamV)},1\n"
        arduino.write(cmd.encode())
        
        cv2.imshow("Debug Centrado Y", frame_small)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

except KeyboardInterrupt: pass
finally:
    vs.stop()
    cv2.destroyAllWindows()
    arduino.close()
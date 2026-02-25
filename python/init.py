import cv2
import serial
import time
import threading
import numpy as np
import os

if not os.path.exists('capturas/completas'): os.makedirs('capturas/completas')
if not os.path.exists('capturas/rostros'): os.makedirs('capturas/rostros')

# --- INICIO ---
print("Iniciando sistema...")

class VideoStream:
    def __init__(self, src):
        print("Abriendo cámara (esto puede tardar unos segundos)...")
        # CAP_DSHOW es mucho más rápido en Windows
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
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
    print("Conectando con Arduino en COM6...")
    arduino = serial.Serial('COM6', 115200, timeout=0.01)
    print("Arduino detectado, esperando reinicio (2s)...")
    time.sleep(2)
    print("Arduino listo.")
except: 
    print("Error: Revisa el puerto COM6"); exit()

print("Iniciando detección...")
vs = VideoStream(0).start()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- AJUSTES DE PRECISIÓN ---
GANANCIA_X = 0.005   # Muy suave para evitar velocidad excesiva
GANANCIA_Y = -0.06   # Ajustado para centrado lento y preciso
DEADZONE_Y = 5       
MAX_STEP_Y = 1.0     # Paso máximo pequeño según preferencia del usuario
SUAVIZADO_MOV = 0.03 # Movimiento ultra fluido

posBase, posHombro, posCamV = 90.0, 60.0, 45.0
targetBase, targetCamV = 90.0, 45.0
ultimo_avistamiento = time.time()
ultima_foto = 0 # Temporizador para cooldown de fotos

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

        # Inicialización de posiciones para Brazo 1 (Búsqueda)
        posB1_Base, posB1_Homb, posB1_Vert, posB1_Horz = 90, 60, 45, 90

        if len(faces) > 0:
            ultimo_avistamiento = ahora
            x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
            tx, ty = x + w//2, y + h//2 
            
            # --- LÓGICA DE CENTRADO ADAPTATIVO ---
            err_x = cx - tx
            err_y = cy - ty 
            
            # Zona muerta del 10% (Tolerancia central)
            DEADZONE_X = 24 # 10% de 240
            DEADZONE_Y_VAL = 32 # 10% de 320
            
            face_color = (0, 255, 0)

            # Eje X - Solo mueve si sale del 10% central
            if abs(err_x) > DEADZONE_X:
                velocidad_x = (abs(err_x) / 120.0) * GANANCIA_X * 10 
                paso_x = np.clip(err_x * velocidad_x, -1.5, 1.5)
                targetBase += paso_x
            
            # Eje Y - Solo mueve si sale del 10% central
            if abs(err_y) > DEADZONE_Y_VAL:
                velocidad_y = (abs(err_y) / 160.0) * abs(GANANCIA_Y)
                paso_y = np.clip(err_y * GANANCIA_Y * velocidad_y, -MAX_STEP_Y, MAX_STEP_Y)
                targetCamV += paso_y 

            # --- AUTO-FOTO ---
            # Solo si AMBOS están dentro del 10% central
            if abs(err_x) <= DEADZONE_X and abs(err_y) <= DEADZONE_Y_VAL:
                if ahora - ultima_foto > 10.0:
                    ultima_foto = ahora
                    face_color = (255, 0, 0)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    ruta_foto = os.path.join('capturas/completas', f"foto_{timestamp}.jpg")
                    cv2.imwrite(ruta_foto, frame)
                    rx, ry, rw, rh = x*2, y*2, w*2, h*2
                    rostro_crop = frame[ry:ry+rh, rx:rx+rw]
                    if rostro_crop.size > 0:
                        ruta_rostro = os.path.join('capturas/rostros', f"rostro_{timestamp}.jpg")
                        cv2.imwrite(ruta_rostro, rostro_crop)
                        print(f"¡Fotos guardadas!: {ruta_foto} y {ruta_rostro}")

            cv2.rectangle(frame_small, (x, y), (x+w, y+h), face_color, 2)
            cv2.circle(frame_small, (tx, ty), 5, (0, 0, 255), -1)

            # Brazo 1 (0-3) imita suavemente en espejo
            posB1_Base = 180 - targetBase
            posB1_Vert = targetCamV
            posB1_Horz = 90 # Mantiene el horizonte

        else:
            # --- MODO BÚSQUEDA ACTIVA (8 SERVOS) ---
            if ahora - ultimo_avistamiento > 2.0:
                frec = ahora * 0.4
                # Brazo 2 (Cámara - 4 a 7)
                targetBase = 90 + 50 * np.sin(frec)
                targetCamV = 70 + 30 * np.cos(frec * 0.7)
                # Brazo 1 (Búsqueda - 0 a 3)
                posB1_Base = 90 + 60 * np.cos(frec * 0.8)
                posB1_Homb = 65 + 15 * np.sin(frec * 0.5)
                posB1_Vert = 60 + 40 * np.sin(frec * 1.2)
                posB1_Horz = 90 + 30 * np.cos(frec * 0.9)

        # Suavizado para Arm 2
        posBase += (targetBase - posBase) * SUAVIZADO_MOV
        posCamV += (targetCamV - posCamV) * SUAVIZADO_MOV

        # Límites de seguridad Arm 2
        posBase = np.clip(posBase, 15, 165)
        posCamV = np.clip(posCamV, 10, 140)
        
        # Envío de 8 Canales
        cmd = f"{int(posB1_Base)},{int(posB1_Homb)},{int(posB1_Vert)},{int(posB1_Horz)},{int(posBase)},60,{int(posCamV)},90,1\n"
        arduino.write(cmd.encode())
        time.sleep(0.02)
        
        cv2.imshow("Debug Centrado Y", frame_small)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

except KeyboardInterrupt: pass
finally:
    vs.stop()
    cv2.destroyAllWindows()
    arduino.close()
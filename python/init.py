import cv2
import serial
import time
import threading
import numpy as np
import os

if not os.path.exists('capturas/completas'): os.makedirs('capturas/completas')
if not os.path.exists('capturas/rostros'): os.makedirs('capturas/rostros')

# --- INICIO ---
print("Iniciando sistema con 3 Brazos...")

class VideoStream:
    def __init__(self, src):
        print("Abriendo cámara (esto puede tardar unos segundos)...")
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
    time.sleep(2)
    print("Arduino listo.")
except: 
    print("Error: Revisa el puerto COM6"); exit()

print("Iniciando detección...")
vs = VideoStream(0).start()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- AJUSTES ---
GANANCIA_X = 0.005
GANANCIA_Y = -0.06
MAX_STEP_Y = 1.0
SUAVIZADO_MOV = 0.03

posBase, posHombro, posCamV = 90.0, 60.0, 45.0
targetBase, targetCamV = 90.0, 45.0
ultimo_avistamiento = time.time()
ultima_foto = 0

try:
    while True:
        frame = vs.read()
        if frame is None: continue

        frame_small = cv2.resize(frame, (240, 320))
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 10, minSize=(50, 50))
        
        cx, cy = 120, 160
        ahora = time.time()

        # Posiciones para Brazos 1 (0-3) y 3 (8-11)
        b1 = [90, 60, 45, 90]
        b3 = [90, 60, 45, 90]

        if len(faces) > 0:
            ultimo_avistamiento = ahora
            x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
            tx, ty = x + w//2, y + h//2 
            
            err_x = cx - tx
            err_y = cy - ty 
            DZ_X = 24
            DZ_Y = 32
            face_color = (0, 255, 0)

            if abs(err_x) > DZ_X:
                vel_x = (abs(err_x) / 120.0) * GANANCIA_X * 10 
                targetBase += np.clip(err_x * vel_x, -1.5, 1.5)
            
            if abs(err_y) > DZ_Y:
                vel_y = (abs(err_y) / 160.0) * abs(GANANCIA_Y)
                targetCamV += np.clip(err_y * GANANCIA_Y * vel_y, -MAX_STEP_Y, MAX_STEP_Y)

            if abs(err_x) <= DZ_X and abs(err_y) <= DZ_Y:
                if ahora - ultima_foto > 10.0:
                    ultima_foto = ahora
                    face_color = (255, 0, 0)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(os.path.join('capturas/completas', f"foto_{timestamp}.jpg"), frame)
                    rx, ry, rw, rh = x*2, y*2, w*2, h*2
                    rostro_crop = frame[ry:ry+rh, rx:rx+rw]
                    if rostro_crop.size > 0:
                        cv2.imwrite(os.path.join('capturas/rostros', f"rostro_{timestamp}.jpg"), rostro_crop)

            cv2.rectangle(frame_small, (x, y), (x+w, y+h), face_color, 2)
            
            # Brazos 1 y 3 imitan al principal
            b1 = [180 - targetBase, targetCamV + 10, targetCamV, 90]
            b3 = [targetBase, targetCamV - 10, targetCamV + 5, 90]

        else:
            if ahora - ultimo_avistamiento > 2.0:
                f = ahora * 0.4
                targetBase = 90 + 50 * np.sin(f)
                targetCamV = 70 + 30 * np.cos(f * 0.7)
                b1 = [90 + 60 * np.cos(f*0.8), 65 + 15 * np.sin(f*0.5), 60 + 40 * np.sin(f*1.2), 90]
                b3 = [90 + 55 * np.sin(f*0.9), 70 + 20 * np.cos(f*0.6), 55 + 35 * np.cos(f*1.1), 90]

        # Suavizado y límites para Arm 2
        posBase += (targetBase - posBase) * SUAVIZADO_MOV
        posCamV += (targetCamV - posCamV) * SUAVIZADO_MOV
        posBase = np.clip(posBase, 15, 165)
        posCamV = np.clip(posCamV, 10, 140)
        
        # Envío con Sincronía '$'
        cmd = f"${int(b1[0])},{int(b1[1])},{int(b1[2])},{int(b1[3])},"
        cmd += f"{int(posBase)},60,{int(posCamV)},90,"
        cmd += f"{int(b3[0])},{int(b3[1])},{int(b3[2])},{int(b3[3])},1\n"
        
        arduino.write(cmd.encode())
        time.sleep(0.02)
        
        cv2.imshow("Debug Centrado Y", frame_small)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

except KeyboardInterrupt: pass
finally:
    if vs: vs.stop()
    cv2.destroyAllWindows()
    if arduino: arduino.close()
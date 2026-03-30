import cv2
import serial
import time
import threading
import numpy as np
import os
import pickle
import re
import urllib.request
import csv
from collections import Counter
from PIL import Image
from insightface.app import FaceAnalysis

# --- CONFIGURACION DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FCAES_DIR = os.path.join(BASE_DIR, "..", "fcaesDes")
DB_FILE = os.path.join(BASE_DIR, "face_database.pkl")
UPDATE_FILE = os.path.join(BASE_DIR, "last_update.txt")
CAPTURA_COMPLETA_DIR = os.path.join(BASE_DIR, "..", "capturas", "completas")
CAPTURA_ROSTRO_DIR = os.path.join(BASE_DIR, "..", "capturas", "rostros")

for d in [CAPTURA_COMPLETA_DIR, CAPTURA_ROSTRO_DIR]:
    if not os.path.exists(d): os.makedirs(d)

# --- CLASE DE ACTUALIZACION AUTOMATICA ---
class BulletinManager:
    def __init__(self, db_file, update_file, fcaes_dir, app):
        self.db_file = db_file
        self.update_file = update_file
        self.fcaes_dir = fcaes_dir
        self.app = app
        self.database = []
        self.load_database()

    def load_database(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'rb') as f:
                self.database = pickle.load(f)
            print(f"Base de datos cargada: {len(self.database)} rostros.")
        else:
            print("Aviso: No se encontro base de datos inicial.")

    def check_and_update(self):
        ahora = time.time()
        last_upd = 0
        if os.path.exists(self.update_file):
            with open(self.update_file, 'r') as f:
                try: last_upd = float(f.read().strip())
                except: pass
        
        # Si paso mas de un dia (86400 seg)
        if ahora - last_upd > 86400:
            print("Buscando nuevos boletines en la web...")
            threading.Thread(target=self.run_update_process, daemon=True).start()

    def run_update_process(self):
        try:
            # 1. Descargar (Logica Simplificada de step1)
            target_url = "https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
            req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
            
            pattern = r'/sites/cobupem\.edomex\.gob\.mx/files/images/Desaparecidos/(\d{4})/[^/]+/[^"]+\.jpg'
            matches = re.findall(pattern, html)
            
            found_urls = re.findall(r'/sites/cobupem\.edomex\.gob\.mx/files/images/Desaparecidos/\d{4}/[^/]+/[^"]+\.jpg', html)
            base_url = "https://cobupem.edomex.gob.mx"
            
            new_files = []
            for partial_url in set(found_urls):
                url = base_url + partial_url
                year_match = re.search(r'/Desaparecidos/(\d{4})/', url)
                year = year_match.group(1) if year_match else "Desconocido"
                
                full_dir = os.path.join(self.fcaes_dir, year, "boletines_completos")
                if not os.path.exists(full_dir): os.makedirs(full_dir)
                
                filename = urllib.parse.unquote(os.path.basename(url))
                full_path = os.path.join(full_dir, filename)
                
                if not os.path.exists(full_path):
                    parts = url.split('/')
                    encoded_path = '/'.join([urllib.parse.quote(p) for p in parts[3:]])
                    encoded_url = f"https://{parts[2]}/{encoded_path}"
                    urllib.request.urlretrieve(encoded_url, full_path)
                    new_files.append((full_path, year, filename))
            
            if not new_files:
                print("No hay boletines nuevos.")
            else:
                print(f"Descargados {len(new_files)} nuevos boletines. Procesando...")
                for full_path, year, filename in new_files:
                    # 2. Crop (Logica de step2)
                    crop_dir = os.path.join(self.fcaes_dir, year, "fotos_recortadas")
                    if not os.path.exists(crop_dir): os.makedirs(crop_dir)
                    cropped_name = f"foto_{filename}"
                    cropped_path = os.path.join(crop_dir, cropped_name)
                    
                    try:
                        img_pil = Image.open(full_path)
                        # Box simplificado para el update
                        w, h = img_pil.size
                        box = (5, 60, 245, 380) if (w,h) == (640,480) else (int(w*0.02), int(h*0.1), int(w*0.5), int(h*0.8))
                        img_pil.crop(box).save(cropped_path)
                        
                        # 3. Index (Logica de step3)
                        img_cv = cv2.imread(cropped_path)
                        faces = self.app.get(img_cv)
                        if faces:
                            self.database.append({
                                'name': filename,
                                'year': year,
                                'embedding': faces[0].normed_embedding,
                                'original_path': cropped_path
                            })
                    except Exception as e:
                        print(f"Error procesando {filename}: {e}")
                
                # Guardar DB con prevencion de corrupcion
                tmp_db = self.db_file + ".tmp"
                with open(tmp_db, 'wb') as f:
                    pickle.dump(self.database, f)
                if os.path.exists(self.db_file): os.remove(self.db_file)
                os.rename(tmp_db, self.db_file)
                print(f"Base de datos actualizada. Total: {len(self.database)} rostros.")

            with open(self.update_file, 'w') as f:
                f.write(str(time.time()))
                
        except Exception as e:
            print(f"Error en el proceso de update: {e}")

# --- VIDEO STREAM ---
class VideoStream:
    def __init__(self, src):
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
                # El usuario rota la camara fisicamente 90 grados en su init.py original
                self.frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            else:
                self.stopped = True

    def read(self): return self.frame
    def stop(self): 
        self.stopped = True
        self.cap.release()

# --- INICIO SISTEMA ---
print("Cargando Modelos de IA (InsightFace)...")
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

manager = BulletinManager(DB_FILE, UPDATE_FILE, FCAES_DIR, app)
manager.check_and_update()

print("Conectando con Arduino...")
try:
    arduino = serial.Serial('COM6', 115200, timeout=0.01)
    time.sleep(2)
except:
    print("Aviso: No se encontro Arduino en COM6. Modo simulacion visual.")
    arduino = None

vs = VideoStream(0).start()

# --- AJUSTES MOVIMIENTO (MODO NERVIOSO) ---
posBase, posHombro, posCamV = 90.0, 60.0, 45.0
targetBase, targetCamV = 90.0, 45.0
ultimo_avistamiento = time.time()
ultima_foto = 0
last_known_base = 90.0
last_known_camv = 70.0

# --- SISTEMA DE DATOS PARA RED NEURONAL ---
CSV_DATOS = os.path.join(BASE_DIR, "training_data.csv")
if not os.path.exists(CSV_DATOS):
    with open(CSV_DATOS, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'err_x_rel', 'err_y_rel', 'dist_px', 'aciertos', 'fallos', 'peso_v_x', 'peso_h_y'])

# --- CEREBRO Y ENTRENAMIENTO (Separado en brain_trainer.py) ---
from brain_trainer import BrainTrainer
trainer = BrainTrainer() # Carga automÃ¡ticamente pesos_robot.npy

# --- VARIABLES DE ESTADO Y ARMAS (4 SERVOS POR BRAZO) ---
posArm2 = [90.0, 60.0, 70.0, 90.0]
targetArm2 = [90.0, 60.0, 70.0, 90.0]

# Iniciamos otros brazos en reposo
b1 = [90, 60, 50, 90]
b3 = [90, 70, 60, 90]
b4 = [90, 65, 55, 90]

last_known_base = 90.0
last_known_camv = 70.0
current_display_indices = None
history = []
MAX_HISTORY = 15

try:
    while True:
        frame = vs.read()
        if frame is None: continue

        faces = app.get(frame)
        ahora = time.time()
        
        # Ventanas
        reward_canvas = np.zeros((350, 450, 3), dtype=np.uint8)
        canvas = np.zeros((850, 600, 3), dtype=np.uint8)
        cv2.putText(canvas, "MIL OJOS v2.0 - SISTEMA DE VIGILANCIA IA", (80, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Centro de la Imagen
        img_h, img_w = frame.shape[:2]
        cx, cy = img_w // 2, img_h // 2
        
        # Mira HUD
        cv2.line(frame, (cx-20, cy), (cx+20, cy), (0, 255, 255), 1)
        cv2.line(frame, (cx, cy-20), (cx, cy+20), (0, 255, 255), 1)

        if faces:
            ultimo_avistamiento = ahora
            main_face = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)[0]
            
            bbox = main_face.bbox.astype(int)
            tx, ty = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
            
            # --- CÁLCULO DE DISTANCIAS ---
            err_x, err_y = cx - tx, cy - ty
            distancia_px = np.sqrt(err_x**2 + err_y**2)
            error_input = np.array([err_x / (img_w / 2), err_y / (img_h / 2)])
            
            # Dibujo de vector de error
            cv2.line(frame, (cx, cy), (tx, ty), (0, 255, 0), 2)
            cv2.circle(frame, (tx, ty), 5, (0, 0, 255), -1)
            
            # --- LLAMADA AL CEREBRO (BrainTrainer) ---
            step_v, step_h, status_rl, reward_color = trainer.update(error_input, distancia_px, ahora)
            
            # Aplicar movimiento EXCLUSIVO al Brazo 2
            targetArm2[0] += step_h # Base (Yaw)
            targetArm2[2] += step_v # Codo (Tilt)
            
            # HUD del Entrenador
            trainer.draw_hud(reward_canvas, status_rl, reward_color, distancia_px)

            # Dibujar vector de Intención IA (Azul) sobre el error
            mv_ai = np.dot(trainer.pesos, error_input)
            cv2.arrowedLine(frame, (cx, cy), (cx+int(mv_ai[1]*500), cy-int(mv_ai[0]*500)), (255, 0, 0), 2)

            # --- GUARDAR DATOS RED NEURONAL (CSV) ---
            with open(CSV_DATOS, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([ahora, error_input[0], error_input[1], distancia_px, trainer.aciertos, trainer.fallos, trainer.pesos[0][0], trainer.pesos[1][1]])

            # Info en Pantalla
            cv2.putText(frame, f"DISTANCIA: {int(distancia_px)}px", (tx+10, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"IA WEIGHTS: {np.round(trainer.pesos.flatten()[:2], 2)}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Sincronizar otros brazos (Vigilancia coordinada)
            last_known_base, last_known_camv = targetArm2[0], targetArm2[2]
            b1 = [180 - (targetArm2[0] - 5), targetArm2[2] + 15, targetArm2[2], 90]
            b3 = [targetArm2[0] + 5, targetArm2[2] - 10, targetArm2[2] + 10, 90]
            b4 = [180 - targetArm2[0], targetArm2[2] + 5, targetArm2[2] - 10, 90]

            # --- BUSQUEDA EN DB ---
            if manager.database:
                db_embs = np.array([e['embedding'] for e in manager.database])
                sims = np.dot(db_embs, main_face.normed_embedding)
                history.append(np.argmax(sims))
                if len(history) > MAX_HISTORY: history.pop(0)
                most_common_id, count = Counter(history).most_common(1)[0]
                if current_display_indices is None or (most_common_id != current_display_indices[0] and count >= 8):
                    current_display_indices = np.argsort(sims)[-4:][::-1]
                
                if current_display_indices is not None:
                    # Mostrar resultados en canvas (omitido por brevedad en el diff, pero funcional)
                    gender = "Masc" if main_face.sex == 1 else "Fem"
                    cv2.putText(canvas, f"BIO: {gender} - {int(main_face.age)} anos", (10, 830), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    for i, idx in enumerate(current_display_indices):
                        m = manager.database[idx]
                        m_img = cv2.imread(m['original_path'])
                        if m_img is not None:
                            m_img = cv2.resize(m_img, (280, 330))
                            row, col = i // 2, i % 2
                            canvas[50+row*400:380+row*400, 10+col * 290:290+col*290] = m_img
                            cv2.putText(canvas, f"{m['name'][:20]}", (15+col*290, 410+row*400), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Captura automatica
            if distancia_px < 35:
                if ahora - ultima_foto > 10.0:
                    ultima_foto = ahora
                    ts = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(os.path.join(CAPTURA_COMPLETA_DIR, f"cam_{ts}.jpg"), frame)
                    print(f"SISTEMA: Captura centreada realizada ({ts})")

        else:
            # --- MODO BUSQUEDA INTELIGENTE ---
            tiempo_perdido = ahora - ultimo_avistamiento
            if tiempo_perdido < 6.0:
                t_j = ahora * 10
                targetArm2[0] = last_known_base + 10 * np.sin(t_j)
                targetArm2[2] = last_known_camv + 5 * np.cos(t_j)
                cv2.putText(canvas, "ESTADO: BUSCANDO SUJETO...", (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                t_s = ahora * 0.3
                targetArm2[0] = 90 + 60 * np.sin(t_s)
                targetArm2[2] = 70 + 10 * np.cos(t_s * 0.5)
                cv2.putText(canvas, "ESTADO: ESCANEANDO ENTORNO...", (100, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            t_misc = ahora * 0.25
            b1 = [90 + 40 * np.sin(t_misc), 60 + 5, 50, 90]
            b3 = [90 + 40 * np.cos(t_misc), 70, 60, 90]
            b4 = [90 + 50 * np.sin(t_misc * 0.5), 65, 55, 90]

        # --- ENVIAR A ARDUINO (16 SERVOS TOTAL) ---
        if arduino:
            f_smooth = 0.22 if faces else 0.03
            for i in range(4):
                targetArm2[i] = np.clip(targetArm2[i], 20, 160)
                posArm2[i] += (targetArm2[i] - posArm2[i]) * f_smooth
                posArm2[i] = np.clip(posArm2[i], 20, 160)
            
            cmd = f"${int(b1[0])},{int(b1[1])},{int(b1[2])},{int(b1[3])},"
            cmd += f"{int(posArm2[0])},{int(posArm2[1])},{int(posArm2[2])},{int(posArm2[3])}," 
            cmd += f"{int(b3[0])},{int(b3[1])},{int(b3[2])},{int(b3[3])},"
            cmd += f"{int(b4[0])},{int(b4[1])},{int(b4[2])},{int(b4[3])},1\n"
            arduino.write(cmd.encode())

        # Visualizacion
        cv2.imshow("Stream Mil Ojos", cv2.resize(frame, (360, 480)))
        cv2.imshow("Red Neuronal - Refuerzo", reward_canvas)
        cv2.imshow("Resultados de Semejanza", canvas)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('r'): trainer.reset_pesos()

except KeyboardInterrupt: pass
finally:
    vs.stop()
    cv2.destroyAllWindows()
    if arduino: arduino.close()
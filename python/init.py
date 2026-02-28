import cv2
import serial
import time
import threading
import numpy as np
import os
import pickle
import re
import urllib.request
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

# --- ESTADO DE INTERFAZ STICKY ---
current_display_indices = None
history = []
MAX_HISTORY = 15

try:
    while True:
        frame = vs.read()
        if frame is None: continue

        faces = app.get(frame)
        ahora = time.time()
        b1, b3, b4 = [90,60,45,90], [90,60,45,90], [90,60,45,90]
        
        # Panel de busqueda (Canvas)
        canvas = np.zeros((850, 600, 3), dtype=np.uint8)
        cv2.putText(canvas, "MIL OJOS - BUSQUEDA PROFESIONAL", (120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if faces:
            ultimo_avistamiento = ahora
            faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)
            main_face = faces[0]
            
            bbox = main_face.bbox.astype(int)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            
            # --- LÓGICA DE CENTRADO ADAPTATIVO (CON CONVERGENCIA) ---
            img_h, img_w = frame.shape[:2]
            cx, cy = img_w // 2, img_h // 2
            tx, ty = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
            
            err_x = cx - tx
            err_y = cy - ty
            
            # Normalizamos el error (-1.0 a 1.0) para aplicar el deadzone del 15%
            err_x_rel = err_x / (img_w / 2)
            err_y_rel = err_y / (img_h / 2)
            
            DEADZONE = 0.15 # 15% de cercanía al centro
            
            # --- CENTRADO EN X (Servo 1) ---
            if abs(err_x_rel) < DEADZONE:
                step_x = 0
            else:
                # Pasos proporcionales: más pequeños cuanto más cerca
                GANANCIA_X = 0.15 
                step_x = err_x_rel * GANANCIA_X * 10
                step_x = np.clip(step_x, -4.0, 4.0)
            targetBase += step_x
            
            # 2. SERVO 2: DELANTE / ATRÁS (Fijo en balance)
            pos_arm2_v2 = 75 
            
            # --- CENTRADO EN Y (Servo 3) ---
            if abs(err_y_rel) < DEADZONE:
                step_y = 0
            else:
                # Invertido (-0.35 original) y adaptativo
                GANANCIA_Y = -0.25 
                step_y = err_y_rel * GANANCIA_Y * 15
                step_y = np.clip(step_y, -5.0, 5.0)
            targetCamV += step_y

            # 4. SERVO 4: CUIDAR EL HORIZONTE (Relacionado con Servo 3)
            pos_arm2_v4 = 180 - (targetCamV * 1.05) 
            pos_arm2_v4 = np.clip(pos_arm2_v4, 40, 150)

            # Recordar posición para búsqueda
            last_known_base = targetBase
            last_known_camv = targetCamV

            # Feedback visual
            dist = np.sqrt(err_x**2 + err_y**2)
            if dist < 40:
                cv2.putText(canvas, "ESTADO: ANALISIS CRITICO (LOCKED)", (110, 780), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.putText(canvas, "ESTADO: INTERCEPTANDO SUJETO", (120, 780), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Busqueda en DB con Logica Sticky
            if manager.database:
                db_embs = np.array([e['embedding'] for e in manager.database])
                sims = np.dot(db_embs, main_face.normed_embedding)
                
                best_idx_frame = np.argmax(sims)
                history.append(best_idx_frame)
                if len(history) > MAX_HISTORY: history.pop(0)
                
                most_common_id, count = Counter(history).most_common(1)[0]
                
                if current_display_indices is None or (most_common_id != current_display_indices[0] and count >= 8):
                    current_display_indices = np.argsort(sims)[-4:][::-1]

                if current_display_indices is not None:
                    gender = "Masc" if main_face.sex == 1 else "Fem"
                    traits = f"PERFIL BIOMETRICO: {gender} | Edad: {int(main_face.age)} anos"
                    cv2.putText(canvas, traits, (10, 830), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    
                    for i, idx in enumerate(current_display_indices):
                        m = manager.database[idx]
                        s_live = np.dot(m['embedding'], main_face.normed_embedding)
                        m_img = cv2.imread(m['original_path'])
                        if m_img is not None:
                            m_img = cv2.resize(m_img, (280, 330))
                            row, col = i // 2, i % 2
                            y_off, x_off = 50 + row * 400, 10 + col * 290
                            canvas[y_off:y_off+330, x_off:x_off+280] = m_img
                            color = (0, 255, 0) if s_live > 0.45 else (200, 200, 200)
                            cv2.putText(canvas, f"{i+1}. {m['year']} - {s_live*100:.1f}%", (x_off, y_off+345), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                            cv2.putText(canvas, m['name'][:24], (x_off, y_off+360), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Captura automatica si esta centrado
            if abs(err_x) < 35 and abs(err_y) < 35:
                if ahora - ultima_foto > 15.0:
                    ultima_foto = ahora
                    ts = time.strftime("%Y%m%d_%H%M%S")
                    fname_c = os.path.join(CAPTURA_COMPLETA_DIR, f"cam_{ts}.jpg")
                    cv2.imwrite(fname_c, frame)
                    face_crop = frame[max(0,bbox[1]):bbox[3], max(0,bbox[0]):bbox[2]]
                    fname_r = os.path.join(CAPTURA_ROSTRO_DIR, f"face_{ts}.jpg")
                    cv2.imwrite(fname_r, face_crop)
                    print(f"Captura realizada: {ts}")

            # Otros brazos convergen (Vigilancia coordinada)
            b1 = [180 - (targetBase - 5), targetCamV + 15, targetCamV, 90]
            b3 = [targetBase + 5, targetCamV - 10, targetCamV + 10, 90]
            b4 = [180 - targetBase, targetCamV + 5, targetCamV - 10, 90]
            
        else:
            # --- MODO BUSQUEDA INTELIGENTE / RECUERDO ---
            tiempo_perdido = ahora - ultimo_avistamiento
            pos_arm2_v2 = 60 # Posición de reposo
            pos_arm2_v4 = 90 # Neutro
            
            if tiempo_perdido < 6.0:
                history = []
                t_j = ahora * 10
                targetBase = last_known_base + 10 * np.sin(t_j)
                targetCamV = last_known_camv + 5 * np.cos(t_j)
                cv2.putText(canvas, "SUJETO PERDIDO: BUSCANDO...", (80, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                t_search = ahora * 0.3
                targetBase = 90 + 60 * np.sin(t_search)
                targetCamV = 70 + 10 * np.cos(t_search * 0.5)
                cv2.putText(canvas, "ESCANEANDO ENTORNO...", (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            t_s = ahora * 0.25
            b1 = [90 + 40 * np.sin(t_s), 60 + 5, 50, 90]
            b3 = [90 + 40 * np.cos(t_s), 70, 60, 90]
            b4 = [90 + 50 * np.sin(t_s * 0.5), 65, 55, 90]

        # Enviar a Arduino - MODO AGRESIVO CON COMPENSACION
        if arduino:
            factor = 0.12 if faces else 0.03
            posBase += (targetBase - posBase) * factor
            posCamV += (targetCamV - posCamV) * factor
            
            posBase = np.clip(posBase, 20, 160)
            posCamV = np.clip(posCamV, 20, 130)

            cmd = f"${int(b1[0])},{int(b1[1])},{int(b1[2])},{int(b1[3])},"
            cmd += f"{int(posBase)},{int(pos_arm2_v2)},{int(posCamV)},{int(pos_arm2_v4)}," 
            cmd += f"{int(b3[0])},{int(b3[1])},{int(b3[2])},{int(b3[3])},"
            cmd += f"{int(b4[0])},{int(b4[1])},{int(b4[2])},{int(b4[3])},1\n"
            arduino.write(cmd.encode())

        # Visualizacion
        cv2.imshow("Stream Mil Ojos", cv2.resize(frame, (360, 480)))
        cv2.imshow("Resultados de Semejanza", canvas)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break

except KeyboardInterrupt: pass
finally:
    vs.stop()
    cv2.destroyAllWindows()
    if arduino: arduino.close()
import cv2
import serial
import time
import numpy as np

# Intentar conectar con Arduino
try:
    arduino = serial.Serial('COM6', 115200, timeout=0.1)
    time.sleep(2)
    print("Debug Manual Iniciado en COM6")
except:
    print("Error: Revisa la conexión con Arduino en COM6")
    exit()

def nothing(x): pass

# Creación robusta de ventana
WINDOW_NAME = 'CALIBRACION MANUAL 8 CANALES'
cv2.namedWindow(WINDOW_NAME)
cv2.startWindowThread() # Ayuda en Windows con la gestión de hilos

# Sliders para Brazo 1 (0-3)
cv2.createTrackbar('B1_CH0_Base', WINDOW_NAME, 90, 180, nothing)
cv2.createTrackbar('B1_CH1_Homb', WINDOW_NAME, 60, 180, nothing)
cv2.createTrackbar('B1_CH2_Vert', WINDOW_NAME, 45, 180, nothing)
cv2.createTrackbar('B1_CH3_Horz', WINDOW_NAME, 90, 180, nothing)

# Sliders para Brazo 2 (4-7)
cv2.createTrackbar('B2_CH4_Base', WINDOW_NAME, 90, 180, nothing)
cv2.createTrackbar('B2_CH5_Homb', WINDOW_NAME, 60, 180, nothing)
cv2.createTrackbar('B2_CH6_Vert', WINDOW_NAME, 45, 180, nothing)
cv2.createTrackbar('B2_CH7_Horz', WINDOW_NAME, 90, 180, nothing)

print("Controles activos. Presiona 'q' para salir.")

try:
    while True:
        # Verificar si la ventana sigue existiendo
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        # Leer todos los sliders
        p = [
            cv2.getTrackbarPos('B1_CH0_Base', WINDOW_NAME),
            cv2.getTrackbarPos('B1_CH1_Homb', WINDOW_NAME),
            cv2.getTrackbarPos('B1_CH2_Vert', WINDOW_NAME),
            cv2.getTrackbarPos('B1_CH3_Horz', WINDOW_NAME),
            cv2.getTrackbarPos('B2_CH4_Base', WINDOW_NAME),
            cv2.getTrackbarPos('B2_CH5_Homb', WINDOW_NAME),
            cv2.getTrackbarPos('B2_CH6_Vert', WINDOW_NAME),
            cv2.getTrackbarPos('B2_CH7_Horz', WINDOW_NAME)
        ]

        # Enviar comando con modo=1 (Manual Override)
        cmd = ",".join(map(str, p)) + ",1\n"
        arduino.write(cmd.encode())

        # Feedback visual simple para evitar Null Pointer en trackers
        img = np.zeros((150, 600, 3), np.uint8)
        cv2.putText(img, f"B1: {p[0]},{p[1]},{p[2]},{p[3]}", (20, 50), 1, 1.2, (0,255,0), 2)
        cv2.putText(img, f"B2: {p[4]},{p[5]},{p[6]},{p[7]}", (20, 110), 1, 1.2, (0,255,255), 2)
        cv2.imshow('VALORES ACTUALES', img)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

except KeyboardInterrupt: pass
finally:
    arduino.close()
    cv2.destroyAllWindows()

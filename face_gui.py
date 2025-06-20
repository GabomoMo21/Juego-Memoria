import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
import os
import numpy as np
import threading
import time as time 
import subprocess
import json
from PIL import Image, ImageTk
import tkinter.font as tkFont
import ctypes

SESSION_PATH = "session.json"



USERS_DIR = "users_lbph"

darkGray = "#cbc59e" 
color2 = "#3862a0" #light blue
azul = "#163552"
beige = "#F2EFE5"
color5 = "#2b2e2b"
color6 = "#7d7648"
darkerBeige = "#E3E1D9"
brown = "#ebdeb1" #brown

fontPath3 = os.path.join("fonts", "TT Ramillas Trial Regular.ttf")
fontPath4 = os.path.join("fonts", "BelanidiSerif-Regular.ttf")

# CARGA DE FUENTES A WINDOWS
ctypes.windll.gdi32.AddFontResourceW(fontPath3)
ctypes.windll.gdi32.AddFontResourceW(fontPath4)


class Boton:
    def __init__(self, master, text, command, relx, rely,
                 background="#8B4513", foreground=color5,
                 hover_bg="#333333", hover_fg=color5,
                 highlight="#333333", width=16, height=1, border=5, font=None):
        
        self.relx = relx
        self.rely = rely
        self.boton = tk.Button(
            master, text=text, command=command, background=background, foreground=foreground,
            activebackground=highlight, activeforeground=hover_fg, highlightthickness=2,
            highlightbackground=highlight, highlightcolor="WHITE", cursor="hand2",
            border=border, width=width, height=height, font=font
        )

        self.boton.place(relx=relx, rely=rely, anchor="center")
        self.boton.bind("<Enter>", lambda e: self.boton.config(background=hover_bg))
        self.boton.bind("<Leave>", lambda e: self.boton.config(background=background))

    def ocultar(self):
        self.boton.place_forget()

    def mostrar(self):
        self.boton.place(relx=self.relx, rely=self.rely, anchor="center")

# === Registrar rostro con OpenCV LBPH ===
def register_face_gui():
    name = simpledialog.askstring("Registro", "Ingresa tu nombre de usuario:")
    if not name:
        messagebox.showerror("Error", "Nombre inválido.")
        return

    name = name.strip().lower()
    
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    count = 0
    faces_data = []

    messagebox.showinfo("Instrucción", "Mira a la cámara. Se capturarán 10 imágenes automáticamente.")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face, (100, 100))
            faces_data.append(face_resized)
            count += 1

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Captura {count}/10", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Registrando rostro", frame)

        if count >= 10 or cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if faces_data:
        mean_face = np.mean(faces_data, axis=0)  # Promediar las 10 capturas
        filepath = os.path.join(USERS_DIR, f"{name}.npy")
        np.save(filepath, mean_face)
        messagebox.showinfo("Éxito", f"Usuario guardado correctamente como '{name}'.")
    else:
        messagebox.showwarning("Sin capturas", "No se capturó ningún rostro.")

# === Entrenamiento del modelo LBPH ===
def train_lbph_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []
    label_map = {}
    label_count = 0

    for file in os.listdir(USERS_DIR):
        if file.endswith(".jpg"):
            path = os.path.join(USERS_DIR, file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            name = file.split("_")[0]
            if name not in label_map:
                label_map[name] = label_count
                label_count += 1
            faces.append(img)
            labels.append(label_map[name])

    if not faces:
        return None, {}

    recognizer.train(faces, np.array(labels))
    return recognizer, {v: k for k, v in label_map.items()}
def load_known_faces():
    encodings = []
    names = []

    for file in os.listdir(USERS_DIR):
        if file.endswith(".npy"):
            path = os.path.join(USERS_DIR, file)
            encoding = np.load(path).flatten()
            encodings.append(encoding)
            names.append(os.path.splitext(file)[0])

    return encodings, names
# === Login con rostro ===
# === Login con rostro automático usando OpenCV ===
def login_with_face_gui():
    def login_thread():
        try:
            known_encodings, known_names = load_known_faces()
            if not known_encodings:
                messagebox.showerror("Error", "No hay rostros registrados.")
                return

            cap = cv2.VideoCapture(0)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            start_time = time.time()
            recognized = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    messagebox.showerror("Error", "No se pudo acceder a la cámara.")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = cv2.resize(gray[y:y+h, x:x+w], (100, 100)).flatten()
                    distances = [np.linalg.norm(face - known_enc) for known_enc in known_encodings]
                    min_distance = min(distances)
                    best_match_index = np.argmin(distances)

                    if min_distance < 2000:
                        name = known_names[best_match_index]
                        label = f"Reconocido: {name}"
                        color = (0, 255, 0)
                        recognized = True
                    else:
                        label = "Desconocido"
                        color = (0, 0, 255)

                    # Dibujar recuadro y etiqueta
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                    if recognized:
                        cv2.imshow("Login con rostro", frame)
                        cv2.waitKey(1000)
                        messagebox.showinfo("Login exitoso", f"Bienvenido, {name}!")

                        session_path = "session.json"

                        if os.path.exists(session_path):
                            with open(session_path, "r") as f:
                                session_data = json.load(f)
                        else:
                            session_data = {}

                        if "jugador1" not in session_data:
                            session_data["jugador1"] = name
                        elif "jugador2" not in session_data:
                            
                            if session_data["jugador1"] == name:
                                messagebox.showinfo("Sesión ya activa", "Este usuario ya inició como Jugador 1.")
                                cap.release()
                                cv2.destroyAllWindows()
                                return
                            session_data["jugador2"] = name
                        else:
                            messagebox.showerror("Sesión llena", "Ya hay 2 jugadores activos.")
                            cap.release()
                            cv2.destroyAllWindows()
                            return

                        with open(session_path, "w") as f:
                            json.dump(session_data, f, indent=4)
                        cap.release()
                        cv2.destroyAllWindows()
                        continuar.mostrar()
                        return

                cv2.imshow("Login con rostro", frame)

                if time.time() - start_time > 15:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Login fallido", "No se reconoció ningún rostro o se canceló el login.")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    threading.Thread(target=login_thread).start()


def entrar_como_invitado():
    session_path = "session.json"

    if os.path.exists(session_path):
        with open(session_path, "r") as f:
            session_data = json.load(f)
    else:
        session_data = {}

    if "jugador1" not in session_data:
        session_data["jugador1"] = "invitado1"
    elif "jugador2" not in session_data:
        session_data["jugador2"] = "invitado2"
    else:
        messagebox.showerror("Sesión llena", "Ya hay 2 jugadores activos.")
        return

    with open(session_path, "w") as f:
        json.dump(session_data, f, indent=4)

    messagebox.showinfo("Invitado", "Has ingresado como invitado.")
    continuar.mostrar()


def main_gui():

    global continuar
    faceID = tk.Tk()
    faceID.title("Sistema de Reconocimiento Facial")
    faceID.resizable(width=False, height=False)
    faceID.overrideredirect(1)
    

    ancho_pantalla = faceID.winfo_screenwidth()
    alto_pantalla = faceID.winfo_screenheight()
    x = (ancho_pantalla - 500) // 2
    y = (alto_pantalla - 750) // 2
    faceID.geometry(f"500x750+{x}+{y}")
    

    tarot1 = Image.open(os.path.join("Imagenes", "tarot1.png"))
    tarot1 = tarot1.resize((500, 750))  
    tarot1 = ImageTk.PhotoImage(tarot1)

    fondo = tk.Label(faceID, image=tarot1, bg=color2).place(relx=0.5, rely=0.5, anchor="center")
    
    BeladiniT = tkFont.Font(family="Belanidi Serif", size=24)
    Beladini = tkFont.Font(family="Belanidi Serif", size=13)
    TTRamillas = tkFont.Font(family="TT Ramillas Trl", size=35)
    TTRamillass = tkFont.Font(family="TT Ramillas Trl", size=20)

    tk.Label(faceID, foreground=color6, bg=azul, text="FACE LOGIN", font=BeladiniT).place(relx=0.5, rely=0.18, anchor="center")

    registro = Boton(faceID, text="Registrarse", command=register_face_gui, relx=0.5, rely=0.41, background=brown, 
          foreground=color5, hover_bg=darkGray, hover_fg=color5, highlight=darkGray, font= Beladini)

    inicio = Boton(faceID, text="Iniciar sesión", command=login_with_face_gui, relx=0.5, rely=0.29, background=brown, 
          foreground=color5, hover_bg=darkGray, hover_fg=color5, highlight=darkGray, font= Beladini)

    
    salir = Boton(faceID, text="Salir", command=lambda: [faceID.destroy()], relx=0.5, rely=0.65, background=brown, 
          foreground=color5, hover_bg=darkGray, hover_fg=color5, highlight=darkGray, font= Beladini)
    
    invitado = Boton(faceID, text="Invitado", command=entrar_como_invitado, relx=0.5, rely=0.53,
         background=brown, foreground=color5, hover_bg=darkGray, hover_fg=darkerBeige, highlight=darkGray, height=1, font= Beladini)
    
    continuar = Boton(faceID, text="Continuar", command= lambda: [faceID.destroy()], relx=0.5, rely=0.79, background=brown, 
          foreground=color5, hover_bg=darkGray, hover_fg=color5, highlight=darkGray, height=1, font= Beladini)
    continuar.ocultar()  

    faceID.mainloop()

def main():
    subprocess.Popen(["python", "main.py"])

if __name__ == "__main__":
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    main_gui()
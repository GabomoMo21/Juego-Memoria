from tkinter import *
from tkinter import messagebox
import pygame
import tkinter as tk
import subprocess
import json
from PIL import Image, ImageTk

import json
import os
import subprocess
import ctypes
import tkinter.font as tkFont



morado = "#2a012d"
dorado = "#7d7648"
lila = "#5d2f61"
fontPath4 = os.path.join("fonts", "BelanidiSerif-Regular.ttf")
ctypes.windll.gdi32.AddFontResourceW(fontPath4)


SESSION_PATH = "session.json"

def iniciar_login():
    subprocess.Popen(["python", "face_gui.py"])


pygame.init()
pygame.mixer.init()

sonido_click = pygame.mixer.Sound("Musica/boton.mp3")

def reproducir_click():
    sonido_click.play()
    

def reproducir_musica(ruta, volumen=0.5, repetir=-1):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.set_volume(volumen)
    pygame.mixer.music.play(repetir)

def detener_musica():
    pygame.mixer.music.stop()

def pausar_musica():
    pygame.mixer.music.pause()

def reanudar_musica():
    pygame.mixer.music.unpause()

def nivel1():
    subprocess.Popen(["python", "clasico.py"])
    detener_musica()
    window.destroy()

def activar_boton2():
    global boton2
    boton2.config(state="normal")

def ficha():
    detener_musica()
    window.destroy()
    subprocess.Popen(["python", "Ficha.py"])
    

def nivel2():
    subprocess.Popen(["python", "patrones.py"])
    window.destroy()

def salon():
    subprocess.Popen(["python", "halloffame.py"])


def salon2():
    subprocess.Popen(["python", "hall_of_fame_patrones.py"])


def cerrar_sesion():
    import json
    with open("session.json", "w") as f:
        json.dump({}, f)
    

def sonidostop():
    pygame.mixer.music.stop()

def ventanaprincipal():
    global window
    global patrones_btn
    global tarot2, boton_ajustes  

    def start_move(event):
        window.x = event.x
        window.y = event.y

    def do_move(event):
        x = event.x_root - window.x
        y = event.y_root - window.y
        window.geometry(f"+{x}+{y}")

    window.resizable(width=False, height=False)
    window.overrideredirect(1)
    
    ancho_pantalla = window.winfo_screenwidth()
    alto_pantalla = window.winfo_screenheight()
    x = (ancho_pantalla - 660) // 2
    y = (alto_pantalla - 770) // 2
    window.geometry(f"660x770+{x}+{y}")

    tarot2 = Image.open(os.path.join("Imagenes", "tarot2.png"))
    tarot2 = tarot2.resize((660, 770))  
    tarot2 = ImageTk.PhotoImage(tarot2)

    ajustes = PhotoImage(file="Imagenes/ajustes.png")
    ajustes = ajustes.subsample(150, 150)

    exit = PhotoImage(file="Imagenes/exit.png")
    exit = exit.subsample(25, 25)

    fondo = tk.Label(window, image=tarot2, bg=morado)
    fondo.place(x=0, y=0, relwidth=1, relheight=1)

    BeladiniT = tkFont.Font(family="Belanidi Serif", size=34)
    Beladini = tkFont.Font(family="Belanidi Serif", size=13)

    head = tk.Label(window, foreground=dorado, bg=morado, text="MEMORY GAME", font=BeladiniT)
    head.place(relx=0.5, rely=0.1, anchor="center")

    fondo.bind("<Button-1>", start_move)
    fondo.bind("<B1-Motion>", do_move)

    clasico_btn = Button(window, text="Modo Clásico", bg='#dcc266', fg="black", width=16, height=1, borderwidth=5,
                      font=(Beladini),
                      command=lambda: (reproducir_click(), detener_musica(), nivel1()))
    clasico_btn.place(relx=0.5, rely=0.375, anchor="center")


    patrones_btn = Button(window, text="Modo Patrones", bg='#dcc266', fg="black", width=16, height=1, borderwidth=5, 
                    font=Beladini,
                    command=lambda: (reproducir_click(), detener_musica(), nivel2()))
    patrones_btn.place(relx=0.5, rely=0.500, anchor="center")

    fama_clasico_btn = Button(window, text="Mejores Clásico", bg='#dcc266', fg="black", width=16, height=1, borderwidth=5,
                           font=Beladini,
                           command=lambda: (reproducir_click(), detener_musica(), salon()))
    fama_clasico_btn.place(relx=0.5, rely=0.625, anchor="center")

    fama_patrones_btn = Button(window, text="Mejores Patrones", bg='#dcc266', fg="black", width=16, borderwidth=5,
                           font=Beladini,
                           command=lambda: (reproducir_click(), detener_musica(), salon2()))
    fama_patrones_btn.place(relx=0.5, rely=0.750, anchor="center")
    
    Login = Button(window, text="Login", bg='#dcc266', fg="black", width=16, borderwidth=5,
                    font=Beladini,
                    command=lambda: (reproducir_click(), detener_musica(), iniciar_login()))
    Login.place(relx=0.5, rely=0.250, anchor="center")

    cerrar_sesion1 = Button(window, text="Cerrar Sesiones Activas", bg=lila, fg=dorado, width=22, borderwidth=5,
                    font=Beladini,
                    command=lambda: (cerrar_sesion()))
    cerrar_sesion1.place(relx=0.5, rely=1, anchor="s",  y=-22)
   

    salir_btn = Button(window, image=exit, command=window.destroy,
                           bd=5, cursor="hand2", bg=dorado)
    salir_btn.image = exit
    salir_btn.place(relx=0, rely=1, anchor="sw", x=+20, y=-20)



    def abrir_ajustes():
        global settings
        reproducir_click()
        ajustes = Toplevel(window)
        ajustes.title("Ajustes")
        ajustes.config(bg=lila)
            
        def start_move(event):
            ajustes.x = event.x
            ajustes.y = event.y

        def do_move(event):
            x = event.x_root - ajustes.x
            y = event.y_root - ajustes.y
            ajustes.geometry(f"+{x}+{y}")

        ajustes.resizable(width=False, height=False)
        ajustes.overrideredirect(1)
        
        ancho_pantalla = ajustes.winfo_screenwidth()
        alto_pantalla = ajustes.winfo_screenheight()
        x = (ancho_pantalla - 500) // 2
        y = (alto_pantalla - 500) // 2
        ajustes.geometry(f"500x500+{x}+{y}")

        settings = Image.open(os.path.join("Imagenes", "settings.png"))
        settings = settings.resize((500, 500))  
        settings = ImageTk.PhotoImage(settings)

        fondo = tk.Label(ajustes, bg=lila, image=settings)
        fondo.place(x=0, y=0, relwidth=1, relheight=1)

        fondo.bind("<Button-1>", start_move)
        fondo.bind("<B1-Motion>", do_move)

        BeladiniT = tkFont.Font(family="Belanidi Serif", size=18)
        Beladini = tkFont.Font(family="Belanidi Serif", size=14)

        Label(ajustes, text="AJUSTES DE SONIDO", font=BeladiniT, bg=lila, foreground='#dcc266').place(relx=0.5, rely=0.12, anchor="center")

        Label(ajustes, text="Volumen", bg=lila, font=Beladini, foreground='#dcc266').place(relx=0.5, rely=0.21, anchor="center")
        volumen_slider = Scale(ajustes, from_=0, to=100, orient="horizontal", length=250,
                            troughcolor="white", bg=dorado, foreground="white")
        volumen_slider.set(pygame.mixer.music.get_volume() * 100)
        volumen_slider.place(relx=0.5, rely=0.29, anchor="center")

        def cambiar_volumen(valor):
            volumen = int(valor) / 100
            pygame.mixer.music.set_volume(volumen)
            with open("config.json", "w") as f:
                json.dump({"volumen": volumen}, f)

        volumen_slider.config(command=cambiar_volumen)

        Button(ajustes, text="Reiniciar Música", bg='#dcc266', font=Beladini, width=16, height=1, border=5,
            command=lambda: reproducir_musica("Musica/Menu.mp3")).place(relx=0.5, rely=0.45, anchor="center")

        Button(ajustes, text="Detener Música", bg='#dcc266', font=Beladini, width=16, height=1, border=5,
            command=detener_musica).place(relx=0.5, rely=0.625, anchor="center")

        Button(ajustes, text="Cerrar", bg="#ef233c", fg="white", font=Beladini, width=16, height=1, border=5,
            command=ajustes.destroy).place(relx=0.5, rely=0.80, anchor="center")


    boton_ajustes = Button(window, image=ajustes, command=abrir_ajustes,
                           bd=5, cursor="hand2", bg=lila)
    boton_ajustes.image = ajustes 
    boton_ajustes.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)




window = Tk()
ventanaprincipal()
reproducir_musica("Musica\Menu.mp3")
window.mainloop()
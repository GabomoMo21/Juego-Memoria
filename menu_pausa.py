import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import ctypes
import os
from PIL import Image, ImageTk

fontPath4 = os.path.join("fonts", "BelanidiSerif-Regular.ttf")
ctypes.windll.gdi32.AddFontResourceW(fontPath4)

def mostrar_menu_pausa(callbacks):
    global pausa
    """
    Muestra un menú de pausa con opciones y control de volumen.
    
    Parámetros:
    - callbacks: diccionario con funciones para:
        - "reanudar"
        - "reiniciar"
        - "menu_principal"
        - "salir"
        - "obtener_volumen"
        - "ajustar_volumen"
    """
    ventana = tk.Tk()
    ventana.title("Menú de Pausa")
    ventana.configure(bg="#2e2e2e")
    ventana.resizable(False, False)

    
    pausa = Image.open(os.path.join("Imagenes", "pausa.png"))
    pausa = pausa.resize((400, 550))  
    pausa = ImageTk.PhotoImage(pausa)
    
    
    ventana.overrideredirect(1)
    
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla - 400) // 2
    y = (alto_pantalla - 550) // 2
    ventana.geometry(f"400x550+{x}+{y}")

    Beladini = tkFont.Font(family="Belanidi Serif", size=12)
    BeladiniT = tkFont.Font(family="Belanidi Serif", size=14)

    # Estilo general
    estilo_boton = {"font": Beladini, "bg": "#444", "fg": "white", "width": 17, "bd": 3}
    
    tk.Label(ventana, image=pausa,  bg="#1e1e1e", fg="white").place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(ventana, text="PAUSA", font=BeladiniT, bg="#1e1e1e", fg="white").place(relx=0.5, rely=0.12, anchor="center")
    

    tk.Button(ventana, text="Reanudar", command=lambda: (ventana.destroy(), callbacks["reanudar"]()), **estilo_boton).place(relx=0.5, rely=0.23, anchor="center")
    tk.Button(ventana, text="Reiniciar", command=lambda: (ventana.destroy(), callbacks["reiniciar"]()), **estilo_boton).place(relx=0.5, rely=0.38, anchor="center")
    tk.Button(ventana, text="Menú principal", command=lambda: (ventana.destroy(), callbacks["menu_principal"]()), **estilo_boton).place(relx=0.5, rely=0.53, anchor="center")
    tk.Button(ventana, text="Salir del juego", command=lambda: (ventana.destroy(), callbacks["salir"]()), **estilo_boton).place(relx=0.5, rely=0.68, anchor="center")

    volumen_actual = callbacks["obtener_volumen"]()
    volumen_var = tk.DoubleVar(value=volumen_actual)

    tk.Label(ventana, text="Volumen de música", font=Beladini, bg="#1e1e1e", fg="white").place(relx=0.5, rely=0.79, anchor="center")

    tk.Scale(ventana, from_=0, to=1, resolution=0.05, orient="horizontal",
             variable=volumen_var, length=220,
             troughcolor="#444", bg="#2e2e2e", fg="white",
             command=lambda v: callbacks["ajustar_volumen"](float(v))).place(relx=0.5, rely=0.87, anchor="center")


    ventana.mainloop() 
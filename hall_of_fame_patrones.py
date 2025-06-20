import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import json
import pygame
import requests
import xml.etree.ElementTree as ET
from datetime import date

hoy = date.today().strftime("%d/%m/%Y")


# === Obtener tipo de cambio en tiempo real ===
def obtener_tipo_cambio(indicador="318", fecha=None):
    import requests
    import xml.etree.ElementTree as ET
    from datetime import date

    if fecha is None:
        fecha = date.today().strftime("%d/%m/%Y")

    url = (
        "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/"
        "wsindicadoreseconomicos.asmx/ObtenerIndicadoresEconomicosXML"
    )

    params = {
        "Indicador": indicador,
        "FechaInicio": fecha,
        "FechaFinal": fecha,
        "Nombre": "Gabriel",
        "SubNiveles": "N",
        "CorreoElectronico": "mgabriels651@gmail.com",
        "Token": "6SALSBAARO"
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code != 200:
            return None

        outer_xml = ET.fromstring(resp.text)
        inner = outer_xml.text or ""
        root = ET.fromstring(inner)

        for nodo in root.findall(".//INGC011_CAT_INDICADORECONOMIC"):
            valor = nodo.find("NUM_VALOR").text
            return float(valor)
    except:
        return None


# === Música y sonido ===
pygame.init()
pygame.mixer.init()

def reproducir_musica():
    pygame.mixer.music.load("Musica/Menu.mp3")
    pygame.mixer.music.play()

def sonido():
    pygame.mixer.music.load("Musica/hall of fame.mp3")
    pygame.mixer.music.play()

# === Texto iterativo del ranking con premios ===
def construir_texto(ranking, maximo=5):
    cambio = obtener_tipo_cambio() or 550
    global tipo_cambio_actual
    tipo_cambio_actual = cambio
    texto = ""
    for i, jugador in enumerate(ranking[:maximo]):
        nivel = jugador['nivel']
        premio = (1 / nivel) * 100 * cambio
        premio = round(premio, 2)
        texto += f"{i+1}. {jugador['nombre']} - {nivel} nivel - Premio: ${premio}\n"
    return texto

# === Ordenar y mostrar ranking ===
def ordenar_y_mostrar(ranking, i=0):
    if i >= len(ranking):
        texto = construir_texto(ranking)
        canvas.itemconfig(texto_id, text=texto)
        canvas.itemconfig(cambio_id, text=f"Dólar hoy: ₡{round(tipo_cambio_actual, 2)}")
        canvas.itemconfig(fecha, text=f"fecha: {hoy}")
        return
    ordenar_elemento(ranking, i, i + 1)

def ordenar_elemento(ranking, i, j):
    if j >= len(ranking):
        ordenar_y_mostrar(ranking, i + 1)
        return
    if ranking[j]["nivel"] > ranking[i]["nivel"]:
        ranking[i], ranking[j] = ranking[j], ranking[i]
    ordenar_elemento(ranking, i, j + 1)

# === Mostrar ranking desde JSON ===
def mostrar_ranking():
    try:
        with open("ranking_patrones.json", "r") as archivo:
            ranking = json.load(archivo)
    except FileNotFoundError:
        ranking = []

    ordenar_y_mostrar(ranking)
    top5 = ranking[:5]

    with open("ranking_patrones.json", "w") as archivo:
        json.dump(top5, archivo, indent=4)

# === Animar fondo GIF ===
def animar_gif(frames, canvas, imagen_id, i=0):
    canvas.itemconfig(imagen_id, image=frames[i])
    ventana.after(100, lambda: animar_gif(frames, canvas, imagen_id, (i + 1) % len(frames)))

# === Ventana principal ===
ventana = tk.Tk()
ventana.title("\U0001F3C6 Hall of Fame")
ventana.geometry("700x450")
ventana.resizable(False, False)

# === Fondo animado ===
gif = Image.open("Imagenes/fondo hof.gif")
frames = [ImageTk.PhotoImage(f.copy().resize((700, 450))) for f in ImageSequence.Iterator(gif)]
canvas = tk.Canvas(ventana, width=700, height=450, highlightthickness=0)
canvas.pack()
gif_id = canvas.create_image(0, 0, image=frames[0], anchor="nw")
animar_gif(frames, canvas, gif_id)

# === Texto principal ===
canvas.create_text(350, 30, text="Top 5 Jugadores", font=("Arial", 24, "bold"),
                   fill="#FFD700", anchor="center")

fecha = canvas.create_text(90, 30, text="", font=("Arial", 14, "bold"),
                               fill="white", anchor="center")

cambio_id = canvas.create_text(350, 70, text="", font=("Arial", 14, "bold"),
                               fill="white", anchor="center")

texto_id = canvas.create_text(50, 110, text="", font=("Consolas", 16), fill="white",
                              anchor="nw", justify="left")

tk.Button(canvas, text="\U0001F501 Actualizar", command=mostrar_ranking,
          font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
          activebackground="#388E3C", relief="flat", width=20).place(x=250, y=360)

tk.Button(canvas, text="\u274C Cerrar", command=lambda: (reproducir_musica(), ventana.destroy()),
          font=("Arial", 12, "bold"), bg="#F44336", fg="white",
          activebackground="#C62828", relief="flat", width=20).place(x=250, y=400)


# === Sonido y ejecución inicial ===
tipo_cambio_actual = 0  # se actualiza en construir_texto
sonido()
mostrar_ranking()
ventana.mainloop()

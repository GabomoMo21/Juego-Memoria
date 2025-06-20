import pygame
import sys
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import subprocess
import tkinter.font as tkFont
import ctypes
import os
from PIL import Image, ImageTk

fontPath4 = os.path.join("fonts", "BelanidiSerif-Regular.ttf")
ctypes.windll.gdi32.AddFontResourceW(fontPath4)

def seleccionar_jugador_desde_session():
    try:
        with open("session.json", "r") as f:
            data = json.load(f)
    except:
        return "invitado"

    jugadores = list(data.values())

    if len(jugadores) < 1:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "Se necesita al menos un jugador logueado para jugar.")
        subprocess.Popen(["python", "main.py"])
        sys.exit()

    else:
        root = tk.Tk()
        root.title("Seleccionar jugador")
        root.configure(bg="#7d7648")
        root.eval('tk::PlaceWindow . center')

        root.resizable(width=False, height=False)
        root.overrideredirect(1)
        
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()
        x = (ancho_pantalla - 350) // 2
        y = (alto_pantalla - 200) // 2
        root.geometry(f"350x200+{x}+{y}")

        jugador_seleccionado = tk.StringVar()

        Beladini = tkFont.Font(family="Belanidi Serif", size=13)

        def elegir(nombre):
            jugador_seleccionado.set(nombre)
            root.destroy()

        tk.Label(root, text="¿Quién desea jugar?", font=Beladini, bg="#7d7648").pack(pady=12)
        for nombre in jugadores:
            tk.Button(root, text=nombre, font=("Times New Roman", 14, "bold"), bg='#dcc266', width=20, border=3, command=lambda n=nombre: elegir(n)).pack(pady=5)

        root.mainloop()
        return jugador_seleccionado.get()
    


class JuegoPatrones:
    def __init__(self):
        self.nombre_jugador = seleccionar_jugador_desde_session()
        pygame.init()
        pygame.mixer.init()

        try:
            self.sonido_acierto = pygame.mixer.Sound("musica/8-Bit Coin Sound Effect (Copyright Free) (mp3cut.net).mp3")
            self.sonido_fallo = pygame.mixer.Sound("musica/8-bit error game sound effects - wrong invalid denied unauthorized sounds (mp3cut.net).mp3")
        except:
            print("Sonidos no encontrados, continuando sin efectos de sonido.")
            self.sonido_acierto = None
            self.sonido_fallo = None
        
        try:
            pygame.mixer.music.load("musica/Gerudo Valley 8 Bit Remix - The Legend of Zelda_ Ocarina of Time (Konami VRC6).mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except:
            print("Música de fondo no encontrada o no cargada.")

        self.ANCHO = 700
        self.ALTO = 920
        self.FILAS = 6
        self.COLUMNAS = 6
        self.MARGEN = 10
        self.TAM_CASILLA = (self.ANCHO - (self.COLUMNAS + 1) * self.MARGEN) // self.COLUMNAS
        self.ventana = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.NOFRAME)
        pygame.display.set_caption("Juego de Memorización de Patrones")
        self.reloj = pygame.time.Clock()

        self.COLOR_FONDO = (30, 30, 30)
        self.COLOR_CASILLA = (70, 70, 70)
        self.COLOR_PATRON = (255, 100, 100)  
        self.COLOR_SELECCIONADA = (100, 255, 100)  
        self.COLOR_CORRECTO = (0, 255, 0)  
        self.COLOR_INCORRECTO = (255, 0, 0)  
        self.COLOR_TEXTO = (255, 255, 255)

        self.tablero = [[pygame.Rect(self.MARGEN + c * (self.TAM_CASILLA + self.MARGEN),
                                     100 + self.MARGEN + f * (self.TAM_CASILLA + self.MARGEN),
                                     self.TAM_CASILLA, self.TAM_CASILLA)
                         for c in range(self.COLUMNAS)] for f in range(self.FILAS)]

        self.nivel_actual = 1
        self.patron_actual = []
        self.patron_jugador = []
        self.patron_longitud = 3  
        
        # estados del juego
        self.mostrando_patron = 0
        self.esparando_jugador = 1
        self.mostrando_resultado = 2
        self.fin_juego = 3
        
        self.estado_juego = self.mostrando_patron
        
        self.tiempo_mostrar_patron = 600  
        self.tiempo_entre_casillas = 600
        self.tiempo_maximo_total = 12000   
        self.tiempo_maximo_entre_clicks = 2000  
        
        self.tiempo_inicio_patron = 0
        self.tiempo_ultimo_click = 0
        self.tiempo_inicio_jugador = 0
        self.tiempo_ultima_casilla = 0
        
        self.indice_casillas_mostradas = 0

        self.casilla_resaltada = None
        self.tiempo_resaltado = 0
        self.duracion_resaltado = 500
        
        self.paused = False
        self.mejor_nivel = 1

        self.fuente = pygame.font.Font("fonts/BelanidiSerif-Regular.ttf", 14)
        self.fuente_titulo = pygame.font.Font("fonts/BelanidiSerif-Regular.ttf", 28)
        self.fuente_stats = pygame.font.Font("fonts/BelanidiSerif-Regular.ttf", 16)
        self.fuente_instrucciones = pygame.font.Font("fonts/BelanidiSerif-Regular.ttf", 14)

        self.generar_nuevo_patron()

    def generar_nuevo_patron(self):
        self.patron_actual = []
        for i in range(self.patron_longitud):
            fila = random.randint(0, self.FILAS - 1)
            columna = random.randint(0, self.COLUMNAS - 1)
            self.patron_actual.append((fila, columna))
        
        self.patron_jugador = []
        self.estado_juego = self.mostrando_patron
        self.tiempo_inicio_patron = pygame.time.get_ticks()
        self.indice_casillas_mostradas = 0
        self.tiempo_ultima_casilla = pygame.time.get_ticks()

    def actualizar_mostrar_patron(self):
        tiempo_actual = pygame.time.get_ticks()
        
        if self.indice_casillas_mostradas < len(self.patron_actual):
            tiempo_transcurrido = tiempo_actual - self.tiempo_ultima_casilla
            
            if tiempo_transcurrido >= self.tiempo_mostrar_patron + self.tiempo_entre_casillas:
                self.casilla_resaltada = self.patron_actual[self.indice_casillas_mostradas]
                self.tiempo_resaltado = tiempo_actual
                self.indice_casillas_mostradas += 1
                self.tiempo_ultima_casilla = tiempo_actual
                
                if self.sonido_acierto:
                    self.sonido_acierto.play()
        else:
            if tiempo_actual - self.tiempo_ultima_casilla >= self.tiempo_entre_casillas * 2:
                self.estado_juego = self.esparando_jugador
                self.tiempo_inicio_jugador = tiempo_actual
                self.tiempo_ultimo_click = tiempo_actual
                self.casilla_resaltada = None

    def verificar_click_usuario(self, fila, columna):
        tiempo_actual = pygame.time.get_ticks()
        indice_actual = len(self.patron_jugador)
        
        if tiempo_actual - self.tiempo_ultimo_click > self.tiempo_maximo_entre_clicks:
            self.terminar_juego(False, "¡Tardaste mucho en presionar la casilla siguiente!")
            return
        
        if tiempo_actual - self.tiempo_inicio_jugador > self.tiempo_maximo_total:
            self.terminar_juego(False, "¡Se acabó el tiempo!")
            return
        
        self.patron_jugador.append((fila, columna))
        self.tiempo_ultimo_click = tiempo_actual
        
        if (fila, columna) == self.patron_actual[indice_actual]:
            self.casilla_resaltada = (fila, columna)
            self.tiempo_resaltado = tiempo_actual
            if len(self.patron_jugador) == len(self.patron_actual):
                self.patron_completado()
        else:
            self.terminar_juego(False, f"¡Perdiste! Casilla incorrecta en la posición {indice_actual + 1}")

    def patron_completado(self):

        self.nivel_actual += 1
        self.patron_longitud += 1
        self.mejor_nivel = max(self.mejor_nivel, self.nivel_actual)
        
        self.estado_juego = self.mostrando_resultado
        self.tiempo_resultado = pygame.time.get_ticks()
        
        if self.sonido_acierto:
            self.sonido_acierto.play()

    def terminar_juego(self, exitoso, mensaje):
        self.estado_juego = self.fin_juego
        self.mensaje_final = mensaje
        
        if self.sonido_fallo and not exitoso:
            self.sonido_fallo.play()

    def obtener_tiempo_restante_total(self):
        if self.estado_juego == self.esparando_jugador:
            tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_inicio_jugador
            tiempo_restante = max(0, self.tiempo_maximo_total - tiempo_transcurrido)
            return tiempo_restante / 1000.0
        return 0

    def obtener_tiempo_restante_click(self):
        if self.estado_juego == self.esparando_jugador:
            tiempo_transcurrido = pygame.time.get_ticks() - self.tiempo_ultimo_click
            tiempo_restante = max(0, self.tiempo_maximo_entre_clicks - tiempo_transcurrido)
            return tiempo_restante / 1000.0
        return 0

    def menu_pausa(self):
        pygame.mixer.music.pause()
        root = tk.Tk()
        root.withdraw()

        volumen = pygame.mixer.music.get_volume()
        while True:
            opcion = messagebox.askquestion("Pausa", f"¿Qué deseas hacer?\n\nVolumen actual: {int(volumen * 100)}%", icon="question", type=messagebox.YESNOCANCEL, default=messagebox.YES, detail="Sí = Reiniciar\nNo = Salir\nCancelar = Menú")

            if opcion == "yes":
                pygame.mixer.music.set_volume(volumen)
                nuevo_juego = JuegoPatrones()
                nuevo_juego.ejecutar()
                break
            elif opcion == "no":
                pygame.quit()
                sys.exit()
            else:
                import subprocess
                subprocess.Popen(["python", "main.py"])
                pygame.quit()
                sys.exit()

    def dibujar(self):
        self.ventana.fill(self.COLOR_FONDO)
        
        pygame.draw.rect(self.ventana, (20, 20, 20), (0, 0, self.ANCHO, 100))
        titulo = self.fuente_titulo.render("MEMORIZACIÓN DE PATRONES", True, self.COLOR_TEXTO)
        self.ventana.blit(titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 30))


        tiempo_actual = pygame.time.get_ticks()
        
        for f in range(self.FILAS):
            for c in range(self.COLUMNAS):
                rect = self.tablero[f][c]
                color = self.COLOR_CASILLA
                
                if self.casilla_resaltada == (f, c):
                    if tiempo_actual - self.tiempo_resaltado < self.duracion_resaltado:
                        if self.estado_juego == self.mostrando_patron:
                            color = self.COLOR_PATRON
                        elif self.estado_juego == self.esparando_jugador:
                            color = self.COLOR_SELECCIONADA
                    else:
                        self.casilla_resaltada = None
                
                pygame.draw.rect(self.ventana, color, rect, border_radius=8)
                pygame.draw.rect(self.ventana, (100, 100, 100), rect, 2, border_radius=8)
                
        if self.estado_juego == self.mostrando_patron:
            estado_texto = "Observa y memoriza el patrón"
            progreso = f"Mostrando: {self.indice_casillas_mostradas}/{len(self.patron_actual)}"
        elif self.estado_juego == self.esparando_jugador:
            estado_texto = f"Repite el patrón de {self.patron_longitud} casillasen el mismo orden"
            progreso = f"Progreso: {len(self.patron_jugador)}/{len(self.patron_actual)}"
            
            tiempo_total = self.obtener_tiempo_restante_total()
            tiempo_click = self.obtener_tiempo_restante_click()
            
            tiempo_info = self.fuente_stats.render(f"    Tiempo total: {tiempo_total:.1f}s      Tiempo entre clicks: {tiempo_click:.1f}s", True, self.COLOR_TEXTO)
            self.ventana.blit(tiempo_info, (20, self.ALTO - 110))
            
        elif self.estado_juego == self.mostrando_resultado:
            estado_texto = "¡Correcto! Preparando siguiente nivel..."
            progreso = f"Nivel completado: {self.nivel_actual - 1}"
        elif self.estado_juego == self.fin_juego:
            estado_texto = self.mensaje_final
            progreso = f"Nivel alcanzado: {self.nivel_actual}"

        estado_render = self.fuente.render(estado_texto, True, self.COLOR_TEXTO)
        progreso_render = self.fuente_stats.render(progreso, True, self.COLOR_TEXTO)
        
        self.ventana.blit(estado_render, (self.ANCHO // 2 - estado_render.get_width() // 2, self.ALTO - 75))
        self.ventana.blit(progreso_render, (self.ANCHO // 2 - progreso_render.get_width() // 2, self.ALTO - 45))

        pygame.display.flip()

    def mostrar_final(self):
        pygame.quit()

        try:
            with open("session.json", "r") as f:
                session_data = json.load(f)
                nombre = self.nombre_jugador
        except (FileNotFoundError, json.JSONDecodeError):
            nombre = "invitado"

        puntuacion = {
            "nombre": nombre,
            "nivel": self.nivel_actual
        }

        try:
            with open("ranking_patrones.json", "r") as archivo:
                ranking = json.load(archivo)
        except FileNotFoundError:
            ranking = []

        ranking.append(puntuacion)
        ranking.sort(key=lambda x: x["nivel"])

        with open("ranking_patrones.json", "w") as archivo:
            json.dump(ranking, archivo, indent=4)

        ventana = tk.Tk()
        ventana.title("Game Over")
        ventana.configure(bg="#2b2b2b")
        ventana.eval('tk::PlaceWindow . center')
        ventana.resizable(False, False)
    
        pausa = Image.open(os.path.join("Imagenes", "pausa.png"))
        pausa = pausa.resize((400, 550))  
        pausa = ImageTk.PhotoImage(pausa)
        
        ventana.overrideredirect(1)
        
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()
        x = (ancho_pantalla - 400) // 2
        y = (alto_pantalla - 400) // 2
        ventana.geometry(f"400x400+{x}+{y}")

        Beladini = tkFont.Font(family="Belanidi Serif", size=12)
        BeladiniT = tkFont.Font(family="Belanidi Serif", size=18)

        tk.Label(ventana, text="Game Over", font=BeladiniT, fg="white", bg="#2b2b2b").place(rely=0.13, relx=0.5, anchor="center")
        tk.Label(ventana, text=f"Nivel alcanzado: {self.nivel_actual}", font=Beladini, fg="white", bg="#2b2b2b").place(rely=0.25, relx=0.5, anchor="center")

        def jugar_de_nuevo():
            ventana.destroy()
            nuevo_juego = JuegoPatrones()
            nuevo_juego.ejecutar()

        def ver_ranking():
            ventana.destroy()
            self.mostrar_ranking()

        def salir():
            ventana.destroy()
            sys.exit()

        tk.Button(ventana, text="Jugar de nuevo", font=Beladini, bg="#7d7648", fg="white", border=3,
                activebackground='#dcc266', width=20, command=jugar_de_nuevo).place(rely=0.4, relx=0.5, anchor="center")
        tk.Button(ventana, text="Ver ranking", font=Beladini, bg="#7d7648", fg="white", border=3,
                activebackground='#dcc266', width=20, command=ver_ranking).place(rely=0.6, relx=0.5, anchor="center")
        tk.Button(ventana, text="Salir", font=Beladini, bg="#F44336", fg="white", border=3,
                activebackground="#C62828", width=20, command=salir).place(rely=0.8, relx=0.5, anchor="center")

        ventana.mainloop()

    def mostrar_ranking(self):
        subprocess.Popen(["python", "hall_of_fame_patrones.py"])

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.paused = True
                        import menu_pausa
                        menu_pausa.mostrar_menu_pausa({
                            "reanudar": lambda: setattr(self, "paused", False),
                            "reiniciar": lambda: self.__init__() or self.ejecutar(),
                            "menu_principal": lambda: (pygame.quit(), subprocess.Popen(["python", "main.py"]), sys.exit()),
                            "salir": sys.exit,
                            "obtener_volumen": lambda: pygame.mixer.music.get_volume(),
                            "ajustar_volumen": lambda v: pygame.mixer.music.set_volume(v)
                        })
                elif evento.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                    if self.estado_juego == self.esparando_jugador:
                        pos = pygame.mouse.get_pos()
                        for f in range(self.FILAS):
                            for c in range(self.COLUMNAS):
                                if self.tablero[f][c].collidepoint(pos):
                                    self.verificar_click_usuario(f, c)
                                    break

            if not self.paused:
                if self.estado_juego == self.mostrando_patron:
                    self.actualizar_mostrar_patron()
                elif self.estado_juego == self.esparando_jugador:
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - self.tiempo_ultimo_click > self.tiempo_maximo_entre_clicks:
                        self.terminar_juego(False, "Tiempo agotado entre casillas")
                    elif tiempo_actual - self.tiempo_inicio_jugador > self.tiempo_maximo_total:
                        self.terminar_juego(False, "Tiempo total agotado")
                elif self.estado_juego == self.mostrando_resultado:

                    if pygame.time.get_ticks() - self.tiempo_resaltado > 2000:
                        self.generar_nuevo_patron()
                elif self.estado_juego == self.fin_juego:

                    if pygame.time.get_ticks() - self.tiempo_resaltado > 3000:
                        self.mostrar_final()
                        break

            self.dibujar()
            self.reloj.tick(60)

        pygame.quit()

if __name__ == "__main__":
    juego = JuegoPatrones()
    juego.ejecutar()
import pygame
import sys
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import json


class Jugador:
    def __init__(self, matriz_imagenes):
        self.matriz = matriz_imagenes
        self.clickeadas = [[False] * 6 for _ in range(6)]
        self.intentos = 0

    def parejas_encontradas(self):
        return sum(row.count(True) for row in self.clickeadas) // 2

class JuegoMemoria:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.sonido_acierto = pygame.mixer.Sound("musica/8-Bit Coin Sound Effect (Copyright Free) (mp3cut.net).mp3")
        self.sonido_fallo = pygame.mixer.Sound("musica/8-bit error game sound effects - wrong invalid denied unauthorized sounds (mp3cut.net).mp3")
        try:
            pygame.mixer.music.load("musica/Gerudo Valley 8 Bit Remix - The Legend of Zelda_ Ocarina of Time (Konami VRC6).mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except:
            print("Música de fondo no encontrada o no cargada.")

        self.ANCHO = 700
        self.ALTO = 820
        self.FILAS = 6
        self.COLUMNAS = 6
        self.MARGEN = 10
        self.TAM_CASILLA = (self.ANCHO - (self.COLUMNAS + 1) * self.MARGEN) // self.COLUMNAS
        self.ventana = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.NOFRAME)
        pygame.display.set_caption("Memory Game - Modo Clásico")
        self.reloj = pygame.time.Clock()

        self.COLOR_FONDO = (30, 30, 30)
        self.COLOR_CASILLA = (50, 50, 50)
        self.COLOR_RESALTADO = (0, 200, 150)
        self.COLOR_TEXTO = (255, 255, 255)

        self.tablero = [[pygame.Rect(self.MARGEN + c * (self.TAM_CASILLA + self.MARGEN),
                                     60 + self.MARGEN + f * (self.TAM_CASILLA + self.MARGEN),
                                     self.TAM_CASILLA, self.TAM_CASILLA)
                         for c in range(self.COLUMNAS)] for f in range(self.FILAS)]

        self.imagenes = self.cargar_imagenes()
        self.jugador1 = Jugador(self.crear_matriz_imagenes())
        self.jugador2 = Jugador(self.crear_matriz_imagenes())
        self.jugador_actual = 1

        self.TIEMPO_INICIAL = 10
        self.tiempo_restante = self.TIEMPO_INICIAL
        self.ultimo_tiempo = pygame.time.get_ticks()

        self.seleccionadas = []
        self.esperando = False
        self.tiempo_espera = 0
        self.acierto_visual = []

        self.paused = False
        
        
        self.fuente = pygame.font.Font("fonts/BelanidiSerif-Regular.ttf", 14)
        self.fuente_titulo = pygame.font.Font("fonts/BelanidiSerif-Regular.ttf", 28)
        
        try:
            with open("session.json", "r") as f:
                data = json.load(f)
        except:
            data = {}

        if "jugador1" not in data or "jugador2" not in data:
            pygame.quit()
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", "Debe haber dos jugadores logueados para iniciar la partida.")
            subprocess.Popen(["python", "main.py"])
            sys.exit()

        self.nombre_j1 = data["jugador1"]
        self.nombre_j2 = data["jugador2"]



    def cargar_imagenes(self):
        imagenes = []
        for i in range(1, 19):
            try:
                img = pygame.image.load(f"imagenes/img{i}.png")
                img = pygame.transform.scale(img, (self.TAM_CASILLA, self.TAM_CASILLA))
                imagenes.append(img)
            except Exception as e:
                print(f"Error cargando img{i}.png: {e}")
                sys.exit()
        return imagenes

    def crear_matriz_imagenes(self):
        lista = self.imagenes * 2
        random.shuffle(lista)
        return [[lista[f * self.COLUMNAS + c] for c in range(self.COLUMNAS)] for f in range(self.FILAS)]

    def cambiar_turno(self):
        self.jugador_actual = 2 if self.jugador_actual == 1 else 1
        self.tiempo_restante = self.TIEMPO_INICIAL
        self.seleccionadas.clear()
        self.esperando = False
        self.acierto_visual.clear()

    def obtener_estado_actual(self):
        return self.jugador1 if self.jugador_actual == 1 else self.jugador2

    def menu_pausa(self):
        pygame.mixer.music.pause()
        root = tk.Tk()
        root.withdraw()

        volumen = pygame.mixer.music.get_volume()
        while True:
            opcion = messagebox.askquestion("Pausa", f"¿Qué deseas hacer?\n\nVolumen actual: {int(volumen * 100)}%", icon="question", type=messagebox.YESNOCANCEL, default=messagebox.YES, detail="Sí = Reiniciar\nNo = Salir\nCancelar = Menú")

            if opcion == "yes":
                pygame.mixer.music.set_volume(volumen)
                nuevo_juego = JuegoMemoria()
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
        jugador = self.obtener_estado_actual()
        for f in range(self.FILAS):
            for c in range(self.COLUMNAS):
                rect = self.tablero[f][c]
                color = self.COLOR_CASILLA
                if (f, c) in self.acierto_visual:
                    color = self.COLOR_RESALTADO
                pygame.draw.rect(self.ventana, color, rect, border_radius=8)
                if jugador.clickeadas[f][c]:
                    self.ventana.blit(jugador.matriz[f][c], (rect.x, rect.y))

        pygame.draw.rect(self.ventana, (20, 20, 20), (0, 0, self.ANCHO, 60))
        titulo = self.fuente_titulo.render("MEMORY GAME", True, self.COLOR_TEXTO)
        self.ventana.blit(titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 10))

        nombre_turno = self.nombre_j1 if self.jugador_actual == 1 else self.nombre_j2
        texto_turno = self.fuente.render(f"Turno: {nombre_turno}", True, self.COLOR_TEXTO)
        texto_tiempo = self.fuente.render(f"Tiempo: {int(self.tiempo_restante)}s", True, self.COLOR_TEXTO)
        texto_intentos = self.fuente.render(f"{self.nombre_j1}: {self.jugador1.intentos} | {self.nombre_j2}: {self.jugador2.intentos}", True, self.COLOR_TEXTO)

        self.ventana.blit(texto_turno, (30, self.ALTO - 50))
        self.ventana.blit(texto_tiempo, (self.ANCHO - 140, self.ALTO - 50))
        self.ventana.blit(texto_intentos, (self.ANCHO // 2 - texto_intentos.get_width() // 2, self.ALTO - 50))

        pygame.display.flip()

    def mostrar_final(self):
        pygame.quit()
        root = tk.Tk()
        root.withdraw()
        resultado = messagebox.askquestion(
            "Juego terminado",
            "¿Qué deseas hacer ahora?",
            icon="question",
            type=messagebox.YESNOCANCEL,
            default=messagebox.YES,
            detail="Sí = Jugar de nuevo\nNo = Salir\nCancelar = Ir al Menú"
        )

        if resultado == "yes":
            nuevo_juego = JuegoMemoria()
            nuevo_juego.ejecutar()
        elif resultado == "no":
            sys.exit()
        else:
            import subprocess
            subprocess.Popen(["python", "main.py"])
            sys.exit()

    def verificar_victoria(self):
        if self.jugador1.parejas_encontradas() == 18 or self.jugador2.parejas_encontradas() == 18:
            ganador = 1 if self.jugador1.parejas_encontradas() == 18 else 2
            puntos = self.obtener_estado_actual().intentos
            nombre = self.nombre_j1 if ganador == 1 else self.nombre_j2
            if nombre:
                try:
                    with open("ranking.json", "r") as archivo:
                        ranking = json.load(archivo)
                except FileNotFoundError:
                    ranking = []
                ranking.append({"nombre": nombre, "puntos": puntos})
                with open("ranking.json", "w") as archivo:
                    json.dump(ranking, archivo, indent=4)
            self.mostrar_final()

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
                elif evento.type == pygame.MOUSEBUTTONDOWN and not self.esperando and not self.paused:
                    pos = pygame.mouse.get_pos()
                    jugador = self.obtener_estado_actual()
                    for f in range(self.FILAS):
                        for c in range(self.COLUMNAS):
                            if self.tablero[f][c].collidepoint(pos) and not jugador.clickeadas[f][c]:
                                self.seleccionadas.append((f, c))
                                jugador.clickeadas[f][c] = True

            if not self.paused:
                tiempo_actual = pygame.time.get_ticks()
                delta = (tiempo_actual - self.ultimo_tiempo) / 1000
                self.ultimo_tiempo = tiempo_actual
                self.tiempo_restante -= delta

                if self.tiempo_restante <= 0:
                    self.cambiar_turno()

                jugador = self.obtener_estado_actual()
                if len(self.seleccionadas) == 2 and not self.esperando:
                    f1, c1 = self.seleccionadas[0]
                    f2, c2 = self.seleccionadas[1]
                    jugador.intentos += 1
                    if jugador.matriz[f1][c1] != jugador.matriz[f2][c2]:
                        self.sonido_fallo.play()
                        self.esperando = True
                        self.tiempo_espera = pygame.time.get_ticks()
                    else:
                        self.sonido_acierto.play()
                        self.acierto_visual = [(f1, c1), (f2, c2)]
                        self.tiempo_restante += 7
                        self.seleccionadas.clear()

                if self.esperando and pygame.time.get_ticks() - self.tiempo_espera > 1000:
                    f1, c1 = self.seleccionadas[0]
                    f2, c2 = self.seleccionadas[1]
                    jugador.clickeadas[f1][c1] = False
                    jugador.clickeadas[f2][c2] = False
                    self.cambiar_turno()

                self.verificar_victoria()

            self.dibujar()
            self.reloj.tick(60)

        pygame.quit()

if __name__ == "__main__":
    juego = JuegoMemoria()
    juego.ejecutar()

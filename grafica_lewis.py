import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import Counter
import re
import math

# =================================================
# CHEMBOT - GENERADOR DE LEWIS + ASISTENTE LOCAL
# No utiliza API ni necesita conexion a internet.
# =================================================

FONDO = "#0B1228"
PANEL = "#121F3D"
PANEL_CLARO = "#1B2B50"
AZUL = "#4385FF"
VIOLETA = "#7564FF"
BLANCO = "#F3F6FF"
GRIS = "#A8B8D8"
VERDE = "#43D9A3"

VALENCIA = {
    "H": 1, "B": 3, "C": 4, "N": 5,
    "O": 6, "F": 7, "P": 5, "S": 6,
    "Cl": 7, "Br": 7, "I": 7
}

# Las estructuras incluidas son plantillas educativas.
MOLECULAS = {
    "H2O": {
        "atoms": ["O", "H", "H"],
        "pos": [(0, 0), (-1, 0.9), (1, 0.9)],
        "bonds": [(0, 1, 1), (0, 2, 1)],
        "lone": [(0, 90), (0, 270)],
        "note": "El oxigeno tiene dos pares de electrones libres."
    },
    "CO2": {
        "atoms": ["O", "C", "O"],
        "pos": [(-1.3, 0), (0,0), (1.3, 0)],
        "bonds": [(0, 1, 2), (1, 2, 2)],
        "lone": [(0, 90), (0, 270), (2, 90), (2, 270)],
        "note": "El carbono forma dos enlaces dobles."
     },
     "NH3": {
         "atoms":["N", "H", "H", "H"],
         "pos": [(0, 0), (-1, 0.8), (1, 0.8), (0, 1.2)],
         "bonds": [(0, 1, 1), (0, 2, 1), (0, 3, 1)],
         "lone": [(0, 270)],
         "note": "El nitrogeno tiene un par libre."
     },
     "CH4": {
         "atoms": ["C", "H", "H", "H", "H"],
         "pos": [(0, 0), (0, -1), (-1, 0), (1, 0), (0, 1)],
         "bonds": [(0, 1, 1), (0, 2, 1),
                   (0, 3, 1), (0, 4, 1)],
         "lone": [],
         "note": "El carbono forma cuatro enlaces sencillos."
     },
     "O2": {
         "atoms": ["O", "O"],
         "pos": [(-0.7, 0), (0.7, 0)],
         "bonds": [(0, 1, 2)],
         "lone": [(0, 90), (0, 270), (1, 90), (1, 270)],
         "note": "Modelo convecional con un enlace doble."
     },
     "N2": {
         "atoms": ["N", "N"],
         "pos": [(-0.7, 0), (0.7, )],
         "bonds": [(0, 1, 3)],
         "lone": [(0, 90), (1, 90)],
         "note": "Los atomos de nitrogeno forman un enlace triple."
     },
     "HCN": {
         "atoms": ["H", "C", "N"],
         "pos": [(-1.3, 0), (0, 0), (1.3, 0)],
         "bonds": [(0, 1, 1), (1, 2, 3)],
         "lone": [(2, 90)],
         "note": "El nitrogeno tiene un par libre."
     },
     "HC1": {
         "atoms": ["H", "C1"],
         "pos": [(-0.7, 0), (0.7, 0)],
         "bonds": [(0, 1, 1)],
         "lone": [(1, 0), (1, 90), (1, 180)],
         "note": "El cloro tiene tres pares libres."
     },
     "BF3": {
         "atoms": ["B", "F", "F", "F"],
         "pos": [(0, 0), (0, -1.1), (-1, 0.7), (1, 0.7)],
         "bonds": [(0, 1, 1), (0, 2, 1), (0, 3, 1)],
         "lone": [
             (1, 0), (1, 90), (1, 180),
             (2, 0), (2, 90), (2, 180),
             (3, 0), (3, 90), (3, 180)
         ],
         "note": "El boro es una excepcion al octeto."
     }
}

# ===================================================
# RESPUESTAS DEL BOT: MOTOR LOCAL DE REGLAS
# ===================================================

RESPUESTAS = [
    (
        ["hola", "buenas", "buenos dias", "buenas tardes"],
        "¡Hola! Soy ChemBot, tu asistente de quimica. "
        "Puedes preguntarme sobre lewis, enlaces, electrones "
        "de valencia, el octeto o las moleculas."
    ),
    (
        ["quien eres", "tu nombre", "que eres"],
        "Soy ChemBot, un asistente educativo programado en Python. "
        "Respondo mediante reglas y una base de conocimiento local."
    ),
    (
        ["estructura de lewis", "lewis"],
        "Una estructura de lewis representa los electrones de "
        "valencia. Los enlaces se dibujan como lineas y los pares "
        "no enlazantes como puntos alrededor de los atomos."
    ),
    (
        ["electrones de valencia", "valencia"],
        "Son electrones de la capa externa de un atomo. "
        "Participan en los enlaces quimicos. Por ejemplo, el carbono "
        "tiene 4, el nitrogeno 5 y el oxigeno 6."
    ),
    (
        ["regla del octeto", "octeto"],
        "La regla del octeto indica que muchos atomos tienden a "
        "formar enlaces hasta quedar rodeados por 8 electrones. "
        "El hidrogeno suele completar 2. Existen excepciones."
    ),
    (
        ["enlace sencillo", "enlace simple"],
        "Un enlace sencillo representa un par de electrones "
        "compartido entre dos atomos."
    ),
    (
        ["enlace doble"],
        "Un enlace doble representa dos pares de electrones "
        "compartidos entre dos atomos. Un ejemplo es 0=0."
    ),
    (
        ["enlace triple"],
        "Un enlace triple representa tres pares de electrones "
        "compartidos. El nitrogeno molecular se representa N=-N. "
    ),
    (
        ["carga formal", "cargas formales"],
        "Carga formal = electrones de valencia - electrones no "
        "enlazantes - la mitad de los electrones enlazantes. "
        "Ayuda a comparar estructuras de Lewis posibles."
    ),
    (
        ["resonancia"],
        "La resonancia se usa cuando una sola estructura de Lewis "
        "no representa adecuadamente la distribucion electronica. "
        "Las estructuras difieren en la ubicacion de electrones, "
        "no en la posicion de los nucleos. "
    ),
    (
        ["agua", "h2o"],
        "En H2O, el oxigeno forma dos enlaces sencillos con H "
        "y conserva dos pares libres."
    ),
    (
        ["dioxido de carbono", "co2"],
        "En CO2, la estructura mas habitual es O=c=O. "
        "El carbono forma dos enlaces dobles."
    ),
    (
        ["amoniaco", "nh3"],
        "En NH3, el nitrogeno forma tres enlaces sencillos con "
        "hidrogenos y conserva un par libre."
    ),
    (
        ["ayuda", "que puedes hacer", "comandos"],
        "Puedo explicar conceptos basicos de Lewis y ayudarte "
        "a utilizar el generador. Prueba preguntar: "
        "¿Que es el octeto?, ¿Que es un enlace doble? "
        "o ¿Como es la estructura del agua?"
    )
]


def responder_bot(mensaje):
    # Normalizacion basica para encontrar palabras claves.
    texto = mensaje.lower().strip()
    texto = (
        texto.replace("a", "a").replace("e", "e")
        .replace("i", "i").replace("o", "o")
        .replace("u", "u").replace("u", "u")
    )

    for palabras, respuestas in RESPUESTAS:
        for palabra in palabras:
            if palabra in texto:
                return respuestas

    return (
        "Todavia no tengo una respuesta preparada para esa pregunta. "
        "Prueba con conceptos como electrones de valencia, enlaces, "
        "regla del octeto, resonancia o carga formal. "
        "Mi conocimiento esta limitado a las reglas programadas."
    )


# ==================================================
# VENTANA PRINCIPAL
# ==================================================

root = tk.Tk()
root.title("grafica lewis | Laboratorio de quimica")
root.geometry("1250x790")
root.minsize(950, 650)
root.configure(bg=FONDO)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TEntry",
    fieldbackground=PANEL_CLARO,
    foreground=BLANCO,
    padding=9
)

# Cabecera
header = tk.Frame(root, bg=PANEL, height=75)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header, text="ChemBot",
    bg=PANEL, fg=BLANCO,
    font=("Segoe UI", 22, "bold")
).pack(side="left", padx=22, pady=15)

tk.Label(
    header, text="LABORATORIO DE ESTRUCTURA DE LEWIS",
    bg=PANEL, fg=GRIS,
    font=("Segoe UI", 10)
).pack(side="right", padx=22)

# Cuerpo
body = tk.Frame(root, bg=FONDO)
body.pack(fill="both", expand=True, padx=14, pady=14)

# Barra lateral
sidebar = tk.Frame(body, bg=PANEL, width=180)
sidebar.pack(side="left", fill="y", padx=(0, 12))
sidebar.pack_propagate(False)

tk.Label(
    sidebar, text="MENU",
    bg=PANEL, fg=GRIS,
    font=("Segoe UI", 10, "bold")
).pack(anchor="w", padx=16, pady=(20, 10))

tk.Label(
    sidebar, text="Inicio",
    bg=PANEL, fg=BLANCO,
    font=("Segoe UI", 12)
).pack(anchor="w", padx=16, pady=9)

tk.Label(
    sidebar, text="Generador",
    bg=PANEL, fg="#81A8FF",
    font=("Segoe UI", 12, "bold")
).pack(anchor="w", padx=16, pady=9)

tk.Label(
    sidebar,
    text="grafica lewis\n\nTu ayudante de quimica\n\nSin API\nSin conexion",
    bg=PANEL, fg=GRIS,
    font=("Segoe UI", 10),
    justify="left"
).pack(side="bottom", anchor="w", padx=16, pady=20)

# Panel central
center = tk.Frame(body, bg=FONDO)
center.pack(side="left", fill="both", expand=True, padx=(0, 12))

tk.Label(
    center,
    text="Generador de estructura lewis",
    bg=FONDO, fg=BLANCO,
    font=("Segoe UI", 18, "bold")
).pack(anchor="w", pady=(2, 5))

tk.Label(
    center,
    text="Escribe una formula y genera su estructura.",
    bg=FONDO, fg=GRIS,
    font=("Segoe UI", 10)
).pack(anchor="w", pady=(0, 12))

fila = tk.Frame(center, bg=FONDO)
fila.pack(fill="x", pady=(0, 12))

formula_entry = ttk.Entry(fila, font=("Segoe UI", 13))
formula_entry.pack(side="left", fill="x", expand=True)
formula_entry.insert(0, "H2O")

canvas = tk.Canvas(
    center,
    bg="#F8FAFF",
    highlightthickness=0,
    height=360
)
canvas.pack(fill="both", expand=True)

info = tk.Label(
    center, text="Selecciona una molecula.",
    bg=PANEL, fg=GRIS,
    font=("Segoe UI", 10),
    justify="left",
    anchor="w",
    padx=12, pady=12,
    wraplength=650
)
info.pack(fill="x", pady=10)

botones = tk.Frame(center, bg=FONDO)
botones.pack(fill="x")

# Panel del bot
chat = tk.Frame(body, bg=PANEL, width=300)
chat.pack(side="right", fill="y")
chat.pack_propagate(False)

tk.Label(
    chat, text="Chembot",
    bg=PANEL, fg=BLANCO,
    font=("Segoe UI", 16, "bold")
).pack(anchor="w", padx=14, pady=(16, 2))

tk.Label(
    chat, text="Disponible sin internet",
    bg=PANEL, fg=VERDE,
    font=("Segoe UI", 9)
).pack(anchor="w", padx=16, pady=(0, 12))

historial = tk.Text(
    chat,
    bg="#0F1932",
    fg=BLANCO,
    font=("Segoe UI", 10),
    wrap="word",
    relief="flat",
    padx=10,
    pady=10,
    state="disabled"
)
historial.pack(fill="both", expand=True, padx=10, pady=(0, 10))

historial.tag_configure(
    "usuario", foreground="#82AEFF",
    spacing1=8, spacing3=5
)
historial.tag_configure(
    "bot", foreground="#E1E8FF",
    spacing1=8, spacing3=8
)

entrada_chat = ttk.Entry(chat, font=("Segoe UI", 10))
entrada_chat.pack(fill="x", padx=10, pady=(0, 8))

# =================================================
# DIBUJO DE LAS ESTRUCTURAS
# =================================================

def dibujar_estructura():
    formula = formula_entry.get().strip()

    canvas.delete("all")

    if formula not in MOLECULAS:
        info.config(
            text="No existe una plantilla para esa formula. "
                 "Prueba H2O, CO2, NH3, CH4, O2, N2, HCN, HCl o BF3."
        )
        return

    datos = MOLECULAS[formula]
    atomos = datos["atoms"]

    ancho = max(canvas.winfo_width(), 400)
    alto = max(canvas.winfo_height(), 300)

    escala = min(ancho / 4.5, alto / 3.5, 105)
    cx, cy = ancho / 2, alto / 2
    puntos = [
        (cx + x * escala, cy + y * escala)
        for x, y in datos["pos"]
    ]

    # Enlaces
    for a, b, orden in datos["bonds"]:
        x1, y1 = puntos[a]
        x2, y2 = puntos[b]

        dx, dy = x2 - x1, y2 - y1
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            continue

        px, py = -dy / distancia, dx / distancia

        for k in range(orden):
            offset = (k - (orden - 1) / 2) * 7
            canvas.create_line(
                x1 + px * offset, y1 + py * offset,
                x2 + px * offset, y2 + py * offset,
                fill="#243252", width=2
            )

    # Pares libres
    for indice, angulo in datos["lone"]:
        x, y = puntos[indice]
        rad = math.radians(angulo)
        px = x + math.cos(rad) * 29
        py = y + math.sin(rad) * 29

        dx = math.cos(rad + math.pi / 2) * 4
        dy = math.sin(rad + math.pi / 2) * 4

        for signo in (-1, 1):
            canvas.create_oval(
                px + signo * dx - 3, py + signo * dy - 3,
                px + signo * dx + 3, py + signo * dy + 3,
                fill=AZUL, outline=AZUL
            )

    # Atomos
    for simbolo, (x, y) in zip(atomos, puntos):
        canvas.create_text(
            x, y, text=simbolo,
            font=("Segoe UI", 23, "bold"),
            fill="#172447"
        )

    # Informacion electronica
    total = sum(VALENCIA[a] for a in atomos)
    electrones_dibujo = (
        sum(orden * 2 for _, _, orden in datos["bonds"])
        + len(datos["lone"]) * 2
    )

    info.config(
        text=(
            f"Formula: {formula}     "
            f"Electrones de valencia: {total}\n"
            f"Electrones representados: {electrones_dibujo}\n"
            f"Nota: {datos['note']}"
        )
    )


def guardar_dibujo():
    ruta = filedialog.asksaveasfilename(
        defaultextension=".ps",
        filetypes=[("Dibujo PostScrip", "*.ps")]
    )
    if ruta:
        canvas.postscrip(file=ruta, colormode="color")
        messagebox.showinfo(
            "Guardado",
            "Dibujo guardado como archivo PostScript (.ps)."
        )


def limpiar_dibujo():
    canvas.delete("all")
    info.config(text="Dibujo limpiado.")

tk.Button(
    fila, text="Generar",
    command=dibujar_estructura,
    bg=VIOLETA, fg="white",
    activebackground=AZUL,
    relief="flat",
    font=("Segoe UI", 11, "bold"),
    padx=15, pady=8
).pack(side="left", padx=(8, 0))

for formula in ["H2O", "CO2", "NH3", "CH4", "HCN"]:
    tk.Button(
        botones, text=formula,
        command=lambda f=formula: (
            formula_entry.delete(0, "end"),
            formula_entry.insert(0, f),
            dibujar_estructura()
        ),
        bg=PANEL_CLARO, fg=BLANCO,
        activebackground=AZUL,
        relief="flat", padx=10, pady=6
    ).pack(side="left", padx=(0, 6))

tk.Button(
    botones, text="Limpiar",
    command=limpiar_dibujo,
    bg=PANEL_CLARO, fg=BLANCO,
    relief="flat", padx=10, pady=6
).pack(side="right")


# =======================================
# CHAT INTEGRADO
# =======================================

def agregar_mensaje(autor, texto, etiqueta):
    historial.config(state="normal")
    historial.insert("end", f"{autor}\n", etiqueta)
    historial.insert("end", f"{texto}\n\n", etiqueta)
    historial.see("end")
    historial.config(state="disabled")


def enviar_mensaje(event=None):
    mensaje = entrada_chat.get().strip()

    if not mensaje:
        return

    entrada_chat.delete(0, "end")
    agregar_mensaje("Tu", mensaje, "usuario")

    respuestas = responder_bot(mensaje)
    agregar_mensaje("ChemBot", respuestas, "bot")


tk.Button(
    chat,
    text="Enviar mensaje",
    command=enviar_mensaje,
    bg=VIOLETA, fg="white",
    activebackground=AZUL,
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    pady=8
).pack(fill="x", padx=10, pady=(0, 10))

entrada_chat.bind("<Return>", enviar_mensaje)

agregar_mensaje(
    "ChemBot",
    "¡Hola! Soy tu asistente de quimica. "
    "Preguntame sobre Lewis, enlaces o electrones de valencia.",
    "bot"
)

canvas.bind("<Configure>", lambda event: dibujar_estructura())

dibujar_estructura()
root.mainloop()
 
        

    
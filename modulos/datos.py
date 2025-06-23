# modules/data.py

# Datos de aulas por piso
AULAS = {
    # Primer Piso
    "P1-A45-1": 45, "P1-A45-2": 45, "P1-A45-3": 45, "P1-A45-4": 45,
    "P1-A60-1": 60, "P1-A60-2": 60,
    "P1-A30-1": 30, "P1-A30-2": 30,
    # Segundo Piso
    "P2-A45-1": 45, "P2-A45-2": 45, "P2-A45-3": 45, "P2-A45-4": 45,
    "P2-A60-1": 60, "P2-A60-2": 60,
    "P2-A30-1": 30, "P2-A30-2": 30,
    # Tercer Piso
    "P3-A60-1": 60, "P3-A60-2": 60, "P3-A60-3": 60, "P3-A60-4": 60,
    "P3-A40-1": 40, "P3-A40-2": 40,
    # Cuarto Piso
    "P4-A60-1": 60, "P4-A60-2": 60, "P4-A60-3": 60, "P4-A60-4": 60,
    "P4-A40-1": 40, "P4-A40-2": 40,
    # Quinto Piso
    "P5-A120-1": 120, "P5-A120-2": 120
}

GRUPOS = {
    "G1": {"estudiantes": 35, "materia": "Cálculo I"},
    "G2": {"estudiantes": 50, "materia": "Física I"},
    "G3": {"estudiantes": 120, "materia": "Introducción a la Ingeniería"},
    "G4": {"estudiantes": 40, "materia": "Redes I"},
    "G5": {"estudiantes": 60, "materia": "Álgebra Lineal"}
}

BLOQUES_HORARIOS = [
    "07:00–09:15",
    "09:15–11:30",
    "11:30–13:45",
    "14:00–16:15",
    "16:15–18:30",
    "18:30–20:45"
]
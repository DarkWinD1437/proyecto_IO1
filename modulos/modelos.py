from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, LpContinuous
from .datos import AULAS, GRUPOS, BLOQUES_HORARIOS


class AsignacionModel:
    def __init__(self):
        self.asignaciones = []

    def validar_datos(self):
        for g in GRUPOS:
            capacidad_minima = GRUPOS[g]["estudiantes"]
            if not any(AULAS[a] >= capacidad_minima for a in AULAS):
                raise ValueError(f"No hay aulas suficientes para el grupo {g}")
        return True

    def aula_ocupada(self, aula, bloque):
        return any(a == aula and b == bloque for _, a, b, *_ in self.asignaciones)

    def grupo_asignado(self, grupo):
        return any(g == grupo for g, *_ in self.asignaciones)

    def agregar_asignacion(self, grupo, aula, bloque, delta, lambd):
        estudiantes = GRUPOS[grupo]["estudiantes"]
        capacidad = AULAS[aula]
        espacio_libre = capacidad - estudiantes
        umbral = delta * capacidad

        if self.grupo_asignado(grupo):
            raise ValueError(f"El grupo {grupo} ya tiene una asignación")
        if self.aula_ocupada(aula, bloque):
            raise ValueError(f"El aula {aula} ya está ocupada en el bloque {bloque}")
        if estudiantes > capacidad:
            raise ValueError(f"El grupo {grupo} no cabe en el aula {aula}")

        penalizacion = max(0, lambd * (espacio_libre - umbral))
        self.asignaciones.append((grupo, aula, bloque, estudiantes, capacidad, espacio_libre, penalizacion))
        return penalizacion

    def resolver_milp(self, delta, lambd):
        self.validar_datos()

        prob = LpProblem("AsignacionAulas", LpMaximize)

        # Variables de decisión
        x = LpVariable.dicts("x", [(g, a, b) for g in GRUPOS
                                   for a in AULAS
                                   for b in BLOQUES_HORARIOS], 0, 1, LpBinary)
        u = LpVariable.dicts("u", [(g, a, b) for g in GRUPOS
                                   for a in AULAS
                                   for b in BLOQUES_HORARIOS], 0, None, LpContinuous)

        # Función objetivo
        prob += (lpSum(GRUPOS[g]["estudiantes"] * x[g, a, b] for g in GRUPOS
                       for a in AULAS
                       for b in BLOQUES_HORARIOS) -
                 lpSum(u[g, a, b] for g in GRUPOS
                       for a in AULAS
                       for b in BLOQUES_HORARIOS)), "Z"

        # Restricciones
        for g in GRUPOS:
            prob += lpSum(x[g, a, b] for a in AULAS for b in BLOQUES_HORARIOS) == 1

        for a in AULAS:
            for b in BLOQUES_HORARIOS:
                prob += lpSum(x[g, a, b] for g in GRUPOS) <= 1

        for g in GRUPOS:
            for a in AULAS:
                for b in BLOQUES_HORARIOS:
                    prob += GRUPOS[g]["estudiantes"] * x[g, a, b] <= AULAS[a]
                    prob += u[g, a, b] >= x[g, a, b] * (AULAS[a] - GRUPOS[g]["estudiantes"] - delta * AULAS[a])

        prob.solve()

        if prob.status != 1:
            raise ValueError("No se encontró una solución óptima")

        self.asignaciones = []
        resultados = []

        for g in GRUPOS:
            for a in AULAS:
                for b in BLOQUES_HORARIOS:
                    if x[g, a, b].value() == 1:
                        estudiantes = GRUPOS[g]["estudiantes"]
                        capacidad = AULAS[a]
                        espacio_libre = capacidad - estudiantes
                        penalizacion = max(0, lambd * (espacio_libre - delta * capacidad))

                        self.asignaciones.append((g, a, b, estudiantes, capacidad, espacio_libre, penalizacion))
                        resultados.append({
                            "grupo": g,
                            "materia": GRUPOS[g]["materia"],
                            "estudiantes": estudiantes,
                            "aula": a,
                            "capacidad": capacidad,
                            "bloque": b,
                            "espacio_libre": espacio_libre,
                            "penalizacion": penalizacion,
                            "penalizado": penalizacion > 0
                        })

        return resultados

    def calcular_metricas(self):
        if not self.asignaciones:
            return {
                "total_grupos": 0,
                "total_estudiantes": 0,
                "total_penalizacion": 0,
                "utilizacion": 0,
                "aulas_utilizadas": 0,
                "bloques_utilizados": 0,
                "grupos_no_asignados": list(GRUPOS.keys())
            }

        total_grupos = len(self.asignaciones)
        total_estudiantes = sum(a[3] for a in self.asignaciones)
        total_penalizacion = sum(a[-1] for a in self.asignaciones)
        utilizacion = (sum(a[3] for a in self.asignaciones) / sum(a[4] for a in self.asignaciones)) * 100
        aulas_utilizadas = len(set(a[1] for a in self.asignaciones))
        bloques_utilizados = len(set(a[2] for a in self.asignaciones))

        grupos_asignados = set(a[0] for a in self.asignaciones)
        grupos_no_asignados = [g for g in GRUPOS if g not in grupos_asignados]

        return {
            "total_grupos": total_grupos,
            "total_estudiantes": total_estudiantes,
            "total_penalizacion": total_penalizacion,
            "utilizacion": utilizacion,
            "aulas_utilizadas": aulas_utilizadas,
            "bloques_utilizados": bloques_utilizados,
            "grupos_no_asignados": grupos_no_asignados
        }
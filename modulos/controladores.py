from tkinter import messagebox
from .modelos import AsignacionModel
from .datos import GRUPOS, AULAS, BLOQUES_HORARIOS


class MainController:
    def __init__(self, view):
        self.view = view
        self.model = AsignacionModel()

    def filtrar_aulas(self, grupo):
        if grupo:
            estudiantes = GRUPOS[grupo]["estudiantes"]
            return [a for a, cap in AULAS.items() if cap >= estudiantes]
        return list(AULAS.keys())

    def asignar_manual(self, grupo, aula, bloque, delta, lambd):
        try:
            delta = float(delta)
            lambd = float(lambd)

            if not grupo or not aula or not bloque:
                raise ValueError("Complete todos los campos")

            penalizacion = self.model.agregar_asignacion(grupo, aula, bloque, delta, lambd)
            resultados = [{
                "grupo": grupo,
                "materia": GRUPOS[grupo]["materia"],
                "estudiantes": GRUPOS[grupo]["estudiantes"],
                "aula": aula,
                "capacidad": AULAS[aula],
                "bloque": bloque,
                "espacio_libre": AULAS[aula] - GRUPOS[grupo]["estudiantes"],
                "penalizacion": penalizacion,
                "penalizado": penalizacion > 0
            }]

            self.view.actualizar_resultados(resultados)
            self.view.actualizar_metricas(self.model.calcular_metricas())
            messagebox.showinfo("Éxito", f"Asignación realizada:\nGrupo {grupo} en {aula} a las {bloque}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def resolver_automatico(self, delta, lambd):
        try:
            delta = float(delta)
            lambd = float(lambd)

            resultados = self.model.resolver_milp(delta, lambd)
            self.view.actualizar_resultados(resultados)
            self.view.actualizar_metricas(self.model.calcular_metricas())

            metricas = self.model.calcular_metricas()
            messagebox.showinfo("Optimización Completa",
                                f"Se asignaron {metricas['total_grupos']} grupos\n"
                                f"Utilización de aulas: {metricas['utilizacion']:.1f}%\n"
                                f"Penalización total: {metricas['total_penalizacion']:.2f}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar_resultados(self):
        self.model.asignaciones = []
        self.view.limpiar_resultados()
        self.view.actualizar_metricas(self.model.calcular_metricas())

    def exportar_resultados(self, tree_items):
        from datetime import datetime
        import csv

        if not tree_items:
            messagebox.showwarning("Sin datos", "No hay asignaciones para exportar")
            return

        filename = f"asignaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Grupo", "Materia", "Estudiantes", "Aula", "Capacidad", "Bloque", "Espacio Libre", "Penalización"])
                for item in tree_items:
                    writer.writerow(item)
            messagebox.showinfo("Éxito", f"Resultados exportados a {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
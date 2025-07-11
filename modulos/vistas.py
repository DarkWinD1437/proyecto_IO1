import tkinter as tk
from tkinter import ttk
from .datos import GRUPOS, AULAS, BLOQUES_HORARIOS


class MainView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Sistema de Optimización de Asignación de Aulas")
        self.root.geometry("1100x700")

        # Configurar estilo
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=('Arial', 10))
        style.configure("TButton", font=('Arial', 10), padding=5)
        style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        style.configure("TCombobox", padding=5)

        # Frame principal
        main_frame = ttk.Frame(self.root, padding=(20, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frames secundarios
        self.setup_config_frame(main_frame)
        self.setup_results_frame(main_frame)
        self.setup_metrics_frame(main_frame)

        # Configurar grid
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=3)

        # Inicializar métricas
        self.actualizar_metricas({
            "total_grupos": 0,
            "total_estudiantes": 0,
            "total_penalizacion": 0,
            "utilizacion": 0,
            "aulas_utilizadas": "0/16",
            "bloques_utilizados": "0/6",
            "grupos_no_asignados": list(GRUPOS.keys())
        })

    def setup_config_frame(self, parent):
        config_frame = ttk.LabelFrame(parent, text="Configuración de Asignación", padding=(15, 10))
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Combobox para grupos
        ttk.Label(config_frame, text="Grupo:", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.combo_grupo = ttk.Combobox(config_frame, values=list(GRUPOS.keys()), width=25)
        self.combo_grupo.grid(row=0, column=1, sticky="ew", padx=5, pady=(0, 5))
        self.combo_grupo.bind("<<ComboboxSelected>>", self.on_grupo_selected)

        # Combobox para aulas
        ttk.Label(config_frame, text="Aula:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.combo_aula = ttk.Combobox(config_frame, values=list(AULAS.keys()), width=25)
        self.combo_aula.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 5))

        # Combobox para bloques
        ttk.Label(config_frame, text="Bloque horario:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.combo_bloque = ttk.Combobox(config_frame, values=BLOQUES_HORARIOS, width=25)
        self.combo_bloque.grid(row=2, column=1, sticky="ew", padx=5, pady=(0, 5))

        # Entradas para delta y lambda
        ttk.Label(config_frame, text="Umbral de subutilización (δ):").grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.entry_delta = ttk.Entry(config_frame)
        self.entry_delta.insert(0, "0.2")
        self.entry_delta.grid(row=3, column=1, sticky="ew", padx=5, pady=(0, 5))

        ttk.Label(config_frame, text="Factor de penalización (λ):").grid(row=4, column=0, sticky="w", pady=(0, 10))
        self.entry_lambda = ttk.Entry(config_frame)
        self.entry_lambda.insert(0, "1")
        self.entry_lambda.grid(row=4, column=1, sticky="ew", padx=5, pady=(0, 10))

        # Frame para botones
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Asignación Manual", command=self.on_asignar_manual, width=15).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(btn_frame, text="Optimizar Automático", command=self.on_optimizar_auto, width=15).pack(side=tk.LEFT,
                                                                                                          padx=5)
        ttk.Button(btn_frame, text="Limpiar Todo", command=self.on_limpiar, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar", command=self.on_exportar, width=15).pack(side=tk.LEFT, padx=5)

    def setup_results_frame(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Resultados de Asignación", padding=(15, 10))
        results_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Treeview para resultados
        self.tree = ttk.Treeview(results_frame,
                                 columns=("Grupo", "Materia", "Estudiantes", "Aula", "Capacidad", "Bloque", "Libre",
                                          "Penalización"),
                                 show="headings", height=15)

        column_widths = [80, 150, 80, 100, 80, 120, 60, 90]
        for idx, col in enumerate(self.tree["columns"]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[idx], anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para resaltado
        self.tree.tag_configure('penalizado', background='#ffdddd')

    def setup_metrics_frame(self, parent):
        metrics_frame = ttk.LabelFrame(parent, text="Métricas Globales", padding=(15, 10))
        metrics_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Métricas principales
        self.metrics_vars = {}
        metrics_labels = {
            "total_grupos": "Grupos asignados:",
            "total_estudiantes": "Estudiantes asignados:",
            "total_penalizacion": "Penalización total:",
            "utilizacion": "Utilización de aulas:",
            "aulas_utilizadas": "Aulas utilizadas:",
            "bloques_utilizados": "Bloques utilizados:"
        }

        for i, (key, text) in enumerate(metrics_labels.items()):
            ttk.Label(metrics_frame, text=text).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            self.metrics_vars[key] = tk.StringVar(value="0")
            ttk.Label(metrics_frame, textvariable=self.metrics_vars[key], font=('Arial', 10, 'bold')).grid(row=i,
                                                                                                           column=1,
                                                                                                           sticky="e",
                                                                                                           padx=5,
                                                                                                           pady=2)

        # Separador
        ttk.Separator(metrics_frame, orient=tk.HORIZONTAL).grid(row=len(metrics_labels), column=0, columnspan=2,
                                                                sticky="ew", pady=10)

        # Grupos no asignados
        ttk.Label(metrics_frame, text="Grupos no asignados:", style="Header.TLabel").grid(
            row=len(metrics_labels) + 1, column=0, columnspan=2, sticky="w", pady=(10, 5))

        self.unassigned_text = tk.Text(metrics_frame, height=4, width=30, state=tk.DISABLED, font=('Arial', 9))
        self.unassigned_text.grid(row=len(metrics_labels) + 2, column=0, columnspan=2, sticky="nsew")

    # Métodos para actualizar la vista
    def actualizar_resultados(self, resultados):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for resultado in resultados:
            item_id = self.tree.insert("", "end", values=(
                resultado["grupo"],
                resultado["materia"],
                resultado["estudiantes"],
                resultado["aula"],
                resultado["capacidad"],
                resultado["bloque"],
                resultado["espacio_libre"],
                f"{resultado['penalizacion']:.2f}"
            ))

            if resultado["penalizado"]:
                self.tree.item(item_id, tags=('penalizado',))

    def actualizar_metricas(self, metricas):
        self.metrics_vars["total_grupos"].set(metricas["total_grupos"])
        self.metrics_vars["total_estudiantes"].set(metricas["total_estudiantes"])
        self.metrics_vars["total_penalizacion"].set(f"{metricas['total_penalizacion']:.2f}")
        self.metrics_vars["utilizacion"].set(f"{metricas['utilizacion']:.1f}%")
        self.metrics_vars["aulas_utilizadas"].set(f"{metricas['aulas_utilizadas']}/{len(AULAS)}")
        self.metrics_vars["bloques_utilizados"].set(f"{metricas['bloques_utilizados']}/{len(BLOQUES_HORARIOS)}")

        self.unassigned_text.config(state=tk.NORMAL)
        self.unassigned_text.delete(1.0, tk.END)

        if metricas["grupos_no_asignados"]:
            self.unassigned_text.insert(tk.END, "\n".join(
                f"{g} - {GRUPOS[g]['materia']}" for g in metricas["grupos_no_asignados"]))
        else:
            self.unassigned_text.insert(tk.END, "Todos los grupos asignados")

        self.unassigned_text.config(state=tk.DISABLED)

    def limpiar_resultados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # Handlers de eventos
    def on_grupo_selected(self, event):
        grupo = self.combo_grupo.get()
        aulas_filtradas = self.controller.filtrar_aulas(grupo)
        self.combo_aula['values'] = aulas_filtradas
        self.combo_aula.set('')

    def on_asignar_manual(self):
        grupo = self.combo_grupo.get()
        aula = self.combo_aula.get()
        bloque = self.combo_bloque.get()
        delta = self.entry_delta.get()
        lambd = self.entry_lambda.get()

        self.controller.asignar_manual(grupo, aula, bloque, delta, lambd)

    def on_optimizar_auto(self):
        delta = self.entry_delta.get()
        lambd = self.entry_lambda.get()
        self.controller.resolver_automatico(delta, lambd)

    def on_limpiar(self):
        self.controller.limpiar_resultados()

    def on_exportar(self):
        items = [self.tree.item(item)['values'] for item in self.tree.get_children()]
        self.controller.exportar_resultados(items)
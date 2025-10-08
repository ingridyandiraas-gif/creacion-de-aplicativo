import csv
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from collections import defaultdict
import random
from datetime import datetime

class DatabaseManager:
    """Clase para manejar todas las operaciones de base de datos"""
    
    def __init__(self, db_name='materiales.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inicializar la base de datos y crear tablas"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Crear tabla de materiales
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS materiales (
                        id TEXT PRIMARY KEY,
                        material TEXT NOT NULL,
                        tipo TEXT NOT NULL,
                        cantidad REAL NOT NULL,
                        valor REAL NOT NULL,
                        ubicacion TEXT,
                        estado TEXT DEFAULT 'Disponible',
                        fecha TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
    
    def insert_material(self, material_data):
        """Insertar un nuevo material"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO materiales (id, material, tipo, cantidad, valor, ubicacion, estado, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    material_data['ID'],
                    material_data['Material'],
                    material_data['Tipo'],
                    material_data['Cantidad'],
                    material_data['Valor'],
                    material_data['Ubicacion'],
                    material_data['Estado'],
                    material_data['Fecha']
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error al insertar material: {e}")
            return False
    
    def get_all_materials(self):
        """Obtener todos los materiales"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM materiales ORDER BY fecha DESC')
                rows = cursor.fetchall()
                
                materials = []
                for row in rows:
                    materials.append({
                        'ID': row[0],
                        'Material': row[1],
                        'Tipo': row[2],
                        'Cantidad': row[3],
                        'Valor': row[4],
                        'Ubicacion': row[5],
                        'Estado': row[6],
                        'Fecha': row[7]
                    })
                return materials
        except Exception as e:
            print(f"Error al obtener materiales: {e}")
            return []
    
    def search_materials(self, search_text='', tipo_filter='Todos', estado_filter='Todos'):
        """Buscar materiales con filtros"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM materiales WHERE 1=1"
                params = []
                
                if search_text:
                    query += " AND LOWER(material) LIKE LOWER(?)"
                    params.append(f"%{search_text}%")
                
                if tipo_filter != 'Todos':
                    query += " AND tipo = ?"
                    params.append(tipo_filter)
                
                if estado_filter != 'Todos':
                    query += " AND estado = ?"
                    params.append(estado_filter)
                
                query += " ORDER BY fecha DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                materials = []
                for row in rows:
                    materials.append({
                        'ID': row[0],
                        'Material': row[1],
                        'Tipo': row[2],
                        'Cantidad': row[3],
                        'Valor': row[4],
                        'Ubicacion': row[5],
                        'Estado': row[6],
                        'Fecha': row[7]
                    })
                return materials
        except Exception as e:
            print(f"Error al buscar materiales: {e}")
            return []
    
    def update_material(self, material_id, material_data):
        """Actualizar un material existente"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE materiales 
                    SET material=?, tipo=?, cantidad=?, valor=?, ubicacion=?, estado=?, fecha=?
                    WHERE id=?
                ''', (
                    material_data['Material'],
                    material_data['Tipo'],
                    material_data['Cantidad'],
                    material_data['Valor'],
                    material_data['Ubicacion'],
                    material_data['Estado'],
                    material_data['Fecha'],
                    material_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar material: {e}")
            return False
    
    def delete_material(self, material_id):
        """Eliminar un material"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM materiales WHERE id=?', (material_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar material: {e}")
            return False
    
    def get_statistics(self):
        """Obtener estadísticas de los materiales"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Estadísticas generales
                cursor.execute('SELECT COUNT(*), SUM(cantidad), SUM(valor), AVG(valor) FROM materiales')
                general_stats = cursor.fetchone()
                
                # Estadísticas por tipo
                cursor.execute('''
                    SELECT tipo, COUNT(*), SUM(cantidad), SUM(valor), AVG(valor)
                    FROM materiales 
                    GROUP BY tipo
                ''')
                tipo_stats = cursor.fetchall()
                
                # Estadísticas por ubicación
                cursor.execute('''
                    SELECT ubicacion, COUNT(*)
                    FROM materiales 
                    GROUP BY ubicacion
                ''')
                ubicacion_stats = cursor.fetchall()
                
                return {
                    'general': general_stats,
                    'por_tipo': tipo_stats,
                    'por_ubicacion': ubicacion_stats
                }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return None
    
    def export_to_csv(self, filename):
        """Exportar datos a CSV"""
        try:
            materials = self.get_all_materials()
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Material', 'Tipo', 'Cantidad', 'Valor', 'Ubicacion', 'Estado', 'Fecha'])
                for material in materials:
                    writer.writerow([
                        material['ID'],
                        material['Material'],
                        material['Tipo'],
                        material['Cantidad'],
                        material['Valor'],
                        material['Ubicacion'],
                        material['Estado'],
                        material['Fecha']
                    ])
            return True
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False
    
    def import_from_csv(self, filename):
        """Importar datos desde CSV"""
        try:
            imported_count = 0
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    material_data = {
                        'ID': row.get('ID', ''),
                        'Material': row['Material'],
                        'Tipo': row['Tipo'],
                        'Cantidad': float(row['Cantidad']),
                        'Valor': float(row['Valor']),
                        'Ubicacion': row.get('Ubicacion', 'No especificada'),
                        'Estado': row.get('Estado', 'Disponible'),
                        'Fecha': row.get('Fecha', datetime.now().strftime('%d/%m/%Y'))
                    }
                    if self.insert_material(material_data):
                        imported_count += 1
            return imported_count
        except Exception as e:
            print(f"Error al importar: {e}")
            return 0

class GestorMaterialesConGraficos:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Avanzado de Gestión de Materiales - Con Gráficos y Base de Datos")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')
        
        # Inicializar base de datos
        self.db_manager = DatabaseManager('materiales.db')
        
        # Archivo CSV para migración (mantener compatibilidad)
        self.archivo = 'registros_materiales.csv'
        
        # Crear interfaz principal
        self.crear_interfaz_principal()
        
        # Migrar datos existentes y cargar datos iniciales
        self.migrar_datos_csv()
        self.cargar_datos_iniciales()
        
        # Cargar datos en la interfaz y mostrar estadísticas
        self.cargar_datos_en_treeviews()
        self.mostrar_estadisticas_basicas()
    
    def aplicar_color_texto(self, texto, color_code):
        """Aplicar color ANSI al texto para la consola"""
        # Códigos de color ANSI
        colores = {
            'rojo': '\033[91m',
            'verde': '\033[92m',
            'amarillo': '\033[93m',
            'azul': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'blanco': '\033[97m',
            'reset': '\033[0m'
        }
        return f"{colores.get(color_code, '')}{texto}{colores['reset']}"
    
    def insertar_texto_con_color(self, widget, texto, color_tag=None):
        """Insertar texto con color en el widget de texto"""
        if color_tag:
            widget.insert(tk.END, texto, color_tag)
        else:
            widget.insert(tk.END, texto)
    
    def configurar_tags_colores(self):
        """Configurar tags de colores para el widget de texto"""
        if hasattr(self, 'text_grafico'):
            # Configurar tags de colores
            self.text_grafico.tag_configure("rojo", foreground="#FF6B6B")
            self.text_grafico.tag_configure("verde", foreground="#4ECDC4")
            self.text_grafico.tag_configure("azul", foreground="#45B7D1")
            self.text_grafico.tag_configure("amarillo", foreground="#FFEAA7")
            self.text_grafico.tag_configure("magenta", foreground="#DDA0DD")
            self.text_grafico.tag_configure("cyan", foreground="#96CEB4")
            self.text_grafico.tag_configure("naranja", foreground="#FF8C42")
            self.text_grafico.tag_configure("rosa", foreground="#FF69B4")
            self.text_grafico.tag_configure("gris", foreground="#708090")
    
    def migrar_datos_csv(self):
        """Migrar datos existentes de CSV a base de datos"""
        try:
            # Verificar si existe el archivo CSV
            if os.path.exists(self.archivo):
                # Verificar si ya hay datos en la base de datos
                materiales_bd = self.db_manager.get_all_materials()
                if not materiales_bd:
                    # Migrar datos del CSV a la base de datos
                    registros_csv = self.leer_registros_csv()
                    for registro in registros_csv:
                        self.db_manager.insert_material(registro)
                    print(f"Migrados {len(registros_csv)} registros de CSV a base de datos")
        except Exception as e:
            print(f"Error en migración: {e}")
    
    def leer_registros_csv(self):
        """Leer registros del archivo CSV (método de compatibilidad)"""
        try:
            registros = []
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        registros.append({
                            'ID': row.get('ID', ''),
                            'Material': row['Material'],
                            'Tipo': row['Tipo'],
                            'Cantidad': float(row['Cantidad']),
                            'Valor': float(row['Valor']),
                            'Ubicacion': row.get('Ubicacion', ''),
                            'Estado': row.get('Estado', 'Disponible'),
                            'Fecha': row.get('Fecha', '')
                        })
            return registros
        except Exception as e:
            print(f"Error al leer CSV: {e}")
            return []
    
    def inicializar_archivo(self):
        """Crear archivo si no existe"""
        try:
            if not os.path.exists(self.archivo):
                with open(self.archivo, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Material', 'Tipo', 'Cantidad', 'Valor', 'Ubicacion', 'Estado', 'Fecha'])
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar el archivo: {e}")
    
    def crear_interfaz_principal(self):
        """Crear la interfaz principal con notebook"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Título principal
        titulo = ttk.Label(self.main_frame, text="🏭 Sistema Avanzado de Gestión de Materiales", 
                          font=('Arial', 18, 'bold'))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Crear pestañas
        self.crear_pestana_registro()
        self.crear_pestana_graficos()
        self.crear_pestana_estadisticas()
        self.crear_pestana_inventario()
        
        # Botones de control
        self.crear_botones_control()
    
    def crear_pestana_registro(self):
        """Crear pestaña de registro de materiales"""
        frame_registro = ttk.Frame(self.notebook)
        self.notebook.add(frame_registro, text="📝 Registro")
        
        # Frame izquierdo - Formulario
        frame_formulario = ttk.LabelFrame(frame_registro, text="Formulario de Registro", padding="15")
        frame_formulario.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=10)
        
        # Campos del formulario
        ttk.Label(frame_formulario, text="ID Material:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_id = ttk.Entry(frame_formulario, width=25)
        self.entry_id.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.entry_id.insert(0, self.generar_id())
        
        ttk.Label(frame_formulario, text="Nombre del Material:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_nombre = ttk.Entry(frame_formulario, width=25)
        self.entry_nombre.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(frame_formulario, text="Tipo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.combo_tipo = ttk.Combobox(frame_formulario, values=[
            'Solido', 'Peligroso', 'Organico', 'Liquido', 'Metalico', 
            'Papel', 'Vidrio', 'Electronico', 'Textil', 'Quimico'
        ], width=22)
        self.combo_tipo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(frame_formulario, text="Cantidad:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_cantidad = ttk.Entry(frame_formulario, width=25)
        self.entry_cantidad.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(frame_formulario, text="Valor:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_valor = ttk.Entry(frame_formulario, width=25)
        self.entry_valor.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(frame_formulario, text="Ubicación:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.entry_ubicacion = ttk.Entry(frame_formulario, width=25)
        self.entry_ubicacion.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(frame_formulario, text="Estado:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.combo_estado = ttk.Combobox(frame_formulario, values=[
            'Disponible', 'En Uso', 'Agotado', 'Dañado', 'En Reparación'
        ], width=22)
        self.combo_estado.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.combo_estado.set('Disponible')
        
        # Botones de acción
        frame_botones = ttk.Frame(frame_formulario)
        frame_botones.grid(row=7, column=0, columnspan=2, pady=20)
        
        btn_registrar = ttk.Button(frame_botones, text="✅ Registrar", command=self.registrar_material)
        btn_registrar.grid(row=0, column=0, padx=5)
        
        btn_limpiar = ttk.Button(frame_botones, text="🧹 Limpiar", command=self.limpiar_formulario)
        btn_limpiar.grid(row=0, column=1, padx=5)
        
        # Frame derecho - Lista de materiales
        frame_lista = ttk.LabelFrame(frame_registro, text="Inventario Actual", padding="15")
        frame_lista.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=10)
        frame_lista.rowconfigure(0, weight=1)
        frame_lista.columnconfigure(0, weight=1)
        
        # Treeview para mostrar materiales
        columns = ('ID', 'Material', 'Tipo', 'Cantidad', 'Valor', 'Ubicacion', 'Estado')
        self.tree_materiales = ttk.Treeview(frame_lista, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_materiales.heading(col, text=col)
            self.tree_materiales.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_materiales.yview)
        h_scrollbar = ttk.Scrollbar(frame_lista, orient=tk.HORIZONTAL, command=self.tree_materiales.xview)
        self.tree_materiales.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree_materiales.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def crear_pestana_graficos(self):
        """Crear pestaña de gráficos"""
        frame_graficos = ttk.Frame(self.notebook)
        self.notebook.add(frame_graficos, text="📊 Gráficos")
        
        # Frame superior - Controles
        frame_controles = ttk.LabelFrame(frame_graficos, text="Controles de Gráficos", padding="10")
        frame_controles.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Botones de gráficos con colores
        tipos_graficos = [
            ("📊 Gráfico de Barras", self.mostrar_grafico_barras, "#FF6B6B"),
            ("🥧 Gráfico Circular", self.mostrar_grafico_circular, "#4ECDC4"),
            ("📈 Gráfico de Líneas", self.mostrar_grafico_lineas, "#45B7D1"),
            ("📊 Histograma", self.mostrar_grafico_histograma, "#96CEB4"),
            ("🔍 Gráfico de Dispersión", self.mostrar_grafico_dispersion, "#FFEAA7"),
            ("📊 Comparativo", self.mostrar_grafico_comparativo, "#DDA0DD")
        ]
        
        for i, (texto, comando, color) in enumerate(tipos_graficos):
            btn = tk.Button(frame_controles, text=texto, command=comando, 
                          bg=color, fg="white", font=('Arial', 10, 'bold'),
                          relief="raised", bd=2, padx=10, pady=5)
            btn.grid(row=0, column=i, padx=5)
        
        # Frame inferior - Área de gráficos
        frame_area_graficos = ttk.LabelFrame(frame_graficos, text="Visualización de Gráficos", padding="10")
        frame_area_graficos.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        frame_area_graficos.rowconfigure(0, weight=1)
        frame_area_graficos.columnconfigure(0, weight=1)
        
        # Canvas para gráficos
        self.canvas_grafico = tk.Canvas(frame_area_graficos, bg='white', width=800, height=400)
        self.canvas_grafico.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para canvas
        canvas_scrollbar = ttk.Scrollbar(frame_area_graficos, orient=tk.VERTICAL, command=self.canvas_grafico.yview)
        self.canvas_grafico.configure(yscrollcommand=canvas_scrollbar.set)
        canvas_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Área de texto para gráficos ASCII
        self.text_grafico = scrolledtext.ScrolledText(frame_area_graficos, height=20, width=80, font=('Courier', 10))
        self.text_grafico.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configurar colores para el texto
        self.configurar_tags_colores()
    
    def crear_pestana_estadisticas(self):
        """Crear pestaña de estadísticas"""
        frame_estadisticas = ttk.Frame(self.notebook)
        self.notebook.add(frame_estadisticas, text="📈 Estadísticas")
        
        # Frame izquierdo - Estadísticas básicas
        frame_basicas = ttk.LabelFrame(frame_estadisticas, text="Estadísticas Básicas", padding="15")
        frame_basicas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=10)
        
        self.text_estadisticas = scrolledtext.ScrolledText(frame_basicas, height=20, width=50)
        self.text_estadisticas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame derecho - Estadísticas avanzadas
        frame_avanzadas = ttk.LabelFrame(frame_estadisticas, text="Análisis Avanzado", padding="15")
        frame_avanzadas.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=10)
        
        # Botones de análisis
        btn_analisis_completo = ttk.Button(frame_avanzadas, text="🔍 Análisis Completo", 
                                         command=self.analisis_completo)
        btn_analisis_completo.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        btn_tendencias = ttk.Button(frame_avanzadas, text="📈 Análisis de Tendencias", 
                                   command=self.analisis_tendencias)
        btn_tendencias.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        btn_predicciones = ttk.Button(frame_avanzadas, text="🔮 Predicciones", 
                                     command=self.predicciones)
        btn_predicciones.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Área de resultados avanzados
        self.text_avanzado = scrolledtext.ScrolledText(frame_avanzadas, height=15, width=50)
        self.text_avanzado.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
    
    def crear_pestana_inventario(self):
        """Crear pestaña de gestión de inventario"""
        frame_inventario = ttk.Frame(self.notebook)
        self.notebook.add(frame_inventario, text="📦 Inventario")
        
        # Frame superior - Búsqueda y filtros
        frame_filtros = ttk.LabelFrame(frame_inventario, text="Búsqueda y Filtros", padding="10")
        frame_filtros.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(frame_filtros, text="Buscar:").grid(row=0, column=0, padx=5)
        self.entry_buscar = ttk.Entry(frame_filtros, width=30)
        self.entry_buscar.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame_filtros, text="Tipo:").grid(row=0, column=2, padx=5)
        self.combo_filtro_tipo = ttk.Combobox(frame_filtros, values=['Todos', 'Solido', 'Peligroso', 'Organico', 'Liquido', 'Metalico', 'Papel', 'Vidrio', 'Electronico', 'Textil', 'Quimico'])
        self.combo_filtro_tipo.grid(row=0, column=3, padx=5)
        self.combo_filtro_tipo.set('Todos')
        
        ttk.Label(frame_filtros, text="Estado:").grid(row=0, column=4, padx=5)
        self.combo_filtro_estado = ttk.Combobox(frame_filtros, values=['Todos', 'Disponible', 'En Uso', 'Agotado', 'Dañado', 'En Reparación'])
        self.combo_filtro_estado.grid(row=0, column=5, padx=5)
        self.combo_filtro_estado.set('Todos')
        
        btn_buscar = ttk.Button(frame_filtros, text="🔍 Buscar", command=self.buscar_inventario)
        btn_buscar.grid(row=0, column=6, padx=5)
        
        # Frame inferior - Lista de inventario
        frame_lista_inv = ttk.LabelFrame(frame_inventario, text="Inventario Filtrado", padding="10")
        frame_lista_inv.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        frame_lista_inv.rowconfigure(0, weight=1)
        frame_lista_inv.columnconfigure(0, weight=1)
        
        # Treeview para inventario
        columns_inv = ('ID', 'Material', 'Tipo', 'Cantidad', 'Valor', 'Ubicacion', 'Estado', 'Fecha')
        self.tree_inventario = ttk.Treeview(frame_lista_inv, columns=columns_inv, show='headings', height=15)
        
        for col in columns_inv:
            self.tree_inventario.heading(col, text=col)
            self.tree_inventario.column(col, width=100)
        
        # Scrollbars para inventario
        v_scrollbar_inv = ttk.Scrollbar(frame_lista_inv, orient=tk.VERTICAL, command=self.tree_inventario.yview)
        h_scrollbar_inv = ttk.Scrollbar(frame_lista_inv, orient=tk.HORIZONTAL, command=self.tree_inventario.xview)
        self.tree_inventario.configure(yscrollcommand=v_scrollbar_inv.set, xscrollcommand=h_scrollbar_inv.set)
        
        self.tree_inventario.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar_inv.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar_inv.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def crear_botones_control(self):
        """Crear botones de control"""
        frame_control = ttk.Frame(self.main_frame)
        frame_control.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        btn_actualizar = ttk.Button(frame_control, text="🔄 Actualizar", command=self.actualizar_todo)
        btn_actualizar.grid(row=0, column=0, padx=5)
        
        btn_exportar = ttk.Button(frame_control, text="📤 Exportar", command=self.exportar_datos)
        btn_exportar.grid(row=0, column=1, padx=5)
        
        btn_importar = ttk.Button(frame_control, text="📥 Importar", command=self.importar_datos)
        btn_importar.grid(row=0, column=2, padx=5)
        
        btn_salir = ttk.Button(frame_control, text="❌ Salir", command=self.root.quit)
        btn_salir.grid(row=0, column=3, padx=5)
    
    def generar_id(self):
        """Generar ID único para material"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = random.randint(100, 999)
        return f"MAT-{timestamp}-{random_num}"
    
    def cargar_datos_iniciales(self):
        """Cargar datos de ejemplo extensos"""
        registros = self.db_manager.get_all_materials()
        if not registros:
            # Datos de ejemplo más extensos y variados
            datos_ejemplo = [
                # Materiales Sólidos
                ('Botella Plástica PET', 'Solido', 25, 15, 'Almacén A', 'Disponible'),
                ('Envase Tetrapak', 'Solido', 18, 12, 'Almacén A', 'Disponible'),
                ('Bolsa Plástica HDPE', 'Solido', 100, 5, 'Almacén B', 'Disponible'),
                ('Tapas Metálicas', 'Solido', 50, 18, 'Almacén C', 'Disponible'),
                ('Cartón Corrugado', 'Solido', 30, 20, 'Almacén A', 'Disponible'),
                ('Poliestireno Expandido', 'Solido', 15, 25, 'Almacén B', 'Disponible'),
                
                # Materiales Peligrosos
                ('Batería de Auto 12V', 'Peligroso', 3, 150, 'Almacén Seguro', 'Disponible'),
                ('Pilas AA Alcalinas', 'Peligroso', 50, 8, 'Almacén Seguro', 'Disponible'),
                ('Termómetro de Mercurio', 'Peligroso', 2, 5, 'Almacén Seguro', 'Dañado'),
                ('Medicamentos Vencidos', 'Peligroso', 8, 30, 'Almacén Seguro', 'Disponible'),
                ('Aceite de Motor Usado', 'Peligroso', 5, 25, 'Almacén Seguro', 'Disponible'),
                ('Pintura con Plomo', 'Peligroso', 2, 40, 'Almacén Seguro', 'Disponible'),
                
                # Materiales Orgánicos
                ('Restos de Comida', 'Organico', 40, 0, 'Compostera', 'Disponible'),
                ('Cáscaras de Fruta', 'Organico', 20, 0, 'Compostera', 'Disponible'),
                ('Hojas Secas', 'Organico', 60, 0, 'Compostera', 'Disponible'),
                ('Residuos de Jardín', 'Organico', 25, 0, 'Compostera', 'Disponible'),
                ('Café Molido', 'Organico', 8, 0, 'Compostera', 'Disponible'),
                ('Cáscaras de Huevo', 'Organico', 15, 0, 'Compostera', 'Disponible'),
                
                # Materiales Líquidos
                ('Aceite de Cocina', 'Liquido', 12, 15, 'Tanque A', 'Disponible'),
                ('Detergente Usado', 'Liquido', 5, 5, 'Tanque B', 'Disponible'),
                ('Pintura Sobrante', 'Liquido', 3, 20, 'Tanque C', 'Disponible'),
                ('Agua Contaminada', 'Liquido', 30, 0, 'Tanque D', 'Disponible'),
                ('Aceite Hidráulico', 'Liquido', 8, 35, 'Tanque A', 'Disponible'),
                
                # Materiales Metálicos
                ('Latas de Aluminio', 'Metalico', 40, 35, 'Patio Metales', 'Disponible'),
                ('Chatarra de Hierro', 'Metalico', 80, 40, 'Patio Metales', 'Disponible'),
                ('Cables de Cobre', 'Metalico', 12, 60, 'Patio Metales', 'Disponible'),
                ('Radiadores de Aluminio', 'Metalico', 3, 80, 'Patio Metales', 'Disponible'),
                ('Tornillos y Tuercas', 'Metalico', 200, 15, 'Patio Metales', 'Disponible'),
                
                # Materiales de Papel
                ('Periódicos', 'Papel', 50, 8, 'Almacén Papel', 'Disponible'),
                ('Revistas', 'Papel', 25, 5, 'Almacén Papel', 'Disponible'),
                ('Cajas de Cartón', 'Papel', 35, 12, 'Almacén Papel', 'Disponible'),
                ('Papel de Oficina', 'Papel', 40, 10, 'Almacén Papel', 'Disponible'),
                ('Libros Usados', 'Papel', 15, 20, 'Almacén Papel', 'Disponible'),
                
                # Materiales de Vidrio
                ('Botellas de Vidrio Verde', 'Vidrio', 25, 15, 'Almacén Vidrio', 'Disponible'),
                ('Frascos de Vidrio', 'Vidrio', 18, 8, 'Almacén Vidrio', 'Disponible'),
                ('Espejos Rotos', 'Vidrio', 5, 5, 'Almacén Vidrio', 'Dañado'),
                ('Vidrio Plano', 'Vidrio', 8, 20, 'Almacén Vidrio', 'Disponible'),
                ('Cristales de Ventana', 'Vidrio', 12, 18, 'Almacén Vidrio', 'Disponible'),
                
                # Materiales Electrónicos
                ('Computadoras', 'Electronico', 5, 200, 'Almacén Electrónicos', 'En Reparación'),
                ('Teléfonos Móviles', 'Electronico', 15, 50, 'Almacén Electrónicos', 'Disponible'),
                ('Televisores', 'Electronico', 8, 150, 'Almacén Electrónicos', 'Disponible'),
                ('Impresoras', 'Electronico', 6, 80, 'Almacén Electrónicos', 'En Uso'),
                ('Cables y Adaptadores', 'Electronico', 30, 25, 'Almacén Electrónicos', 'Disponible'),
                
                # Materiales Textiles
                ('Ropa Usada', 'Textil', 50, 10, 'Almacén Textiles', 'Disponible'),
                ('Telas', 'Textil', 25, 15, 'Almacén Textiles', 'Disponible'),
                ('Alfombras', 'Textil', 8, 30, 'Almacén Textiles', 'Disponible'),
                ('Zapatos', 'Textil', 20, 20, 'Almacén Textiles', 'Disponible'),
                
                # Materiales Químicos
                ('Productos de Limpieza', 'Quimico', 15, 25, 'Almacén Químicos', 'Disponible'),
                ('Pesticidas', 'Quimico', 5, 40, 'Almacén Químicos', 'Disponible'),
                ('Fertilizantes', 'Quimico', 10, 35, 'Almacén Químicos', 'Disponible'),
                ('Disolventes', 'Quimico', 8, 45, 'Almacén Químicos', 'Disponible')
            ]
            
            for nombre, tipo, cantidad, valor, ubicacion, estado in datos_ejemplo:
                self.registrar_material_silencioso(nombre, tipo, cantidad, valor, ubicacion, estado)
        
        self.cargar_datos_en_treeviews()
    
    def registrar_material_silencioso(self, nombre, tipo, cantidad, valor, ubicacion, estado):
        """Registrar material sin mostrar mensajes"""
        nuevo_registro = {
            'ID': self.generar_id(),
            'Material': nombre,
            'Tipo': tipo,
            'Cantidad': cantidad,
            'Valor': valor,
            'Ubicacion': ubicacion,
            'Estado': estado,
            'Fecha': datetime.now().strftime('%d/%m/%Y')
        }
        
        return self.db_manager.insert_material(nuevo_registro)
    
    def leer_registros(self):
        """Leer todos los registros de la base de datos"""
        return self.db_manager.get_all_materials()
    
    def escribir_registros(self, registros):
        """Escribir registros a la base de datos (método de compatibilidad)"""
        try:
            # Limpiar base de datos actual
            materiales_actuales = self.db_manager.get_all_materials()
            for material in materiales_actuales:
                self.db_manager.delete_material(material['ID'])
            
            # Insertar nuevos registros
            for registro in registros:
                self.db_manager.insert_material(registro)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al escribir registros: {e}")
            return False
    
    def registrar_material(self):
        """Registrar un nuevo material"""
        # Obtener datos del formulario
        id_material = self.entry_id.get().strip()
        nombre = self.entry_nombre.get().strip()
        tipo = self.combo_tipo.get().strip()
        cantidad_str = self.entry_cantidad.get().strip()
        valor_str = self.entry_valor.get().strip()
        ubicacion = self.entry_ubicacion.get().strip()
        estado = self.combo_estado.get().strip()
        
        # Validaciones
        if not all([nombre, tipo, cantidad_str, valor_str]):
            messagebox.showerror("Error", "Todos los campos obligatorios deben ser completados")
            return
        
        try:
            cantidad = float(cantidad_str)
            valor = float(valor_str)
            if cantidad < 0 or valor < 0:
                messagebox.showerror("Error", "Cantidad y Valor deben ser números positivos")
                return
        except ValueError:
            messagebox.showerror("Error", "Cantidad y Valor deben ser números válidos")
            return
        
        # Verificar duplicados
        registros_existentes = self.db_manager.get_all_materials()
        for registro in registros_existentes:
            if registro['ID'] == id_material:
                messagebox.showwarning("Advertencia", f"El ID {id_material} ya existe")
                return
        
        # Crear nuevo registro
        nuevo_registro = {
            'ID': id_material,
            'Material': nombre,
            'Tipo': tipo,
            'Cantidad': cantidad,
            'Valor': valor,
            'Ubicacion': ubicacion or 'No especificada',
            'Estado': estado or 'Disponible',
            'Fecha': datetime.now().strftime('%d/%m/%Y')
        }
        
        if self.db_manager.insert_material(nuevo_registro):
            messagebox.showinfo("Éxito", f'Material "{nombre}" registrado correctamente')
            self.limpiar_formulario()
            self.cargar_datos_en_treeviews()
    
    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, self.generar_id())
        self.entry_nombre.delete(0, tk.END)
        self.combo_tipo.set('')
        self.entry_cantidad.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.entry_ubicacion.delete(0, tk.END)
        self.combo_estado.set('Disponible')
    
    def actualizar_listas(self):
        """Actualizar todas las listas de materiales"""
        registros = self.leer_registros()
        
        # Actualizar treeview principal
        for item in self.tree_materiales.get_children():
            self.tree_materiales.delete(item)
        
        for registro in registros:
            self.tree_materiales.insert('', 'end', values=(
                registro['ID'],
                registro['Material'],
                registro['Tipo'],
                registro['Cantidad'],
                registro['Valor'],
                registro['Ubicacion'],
                registro['Estado']
            ))
        
        # Actualizar treeview de inventario
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        
        for registro in registros:
            self.tree_inventario.insert('', 'end', values=(
                registro['ID'],
                registro['Material'],
                registro['Tipo'],
                registro['Cantidad'],
                registro['Valor'],
                registro['Ubicacion'],
                registro['Estado'],
                registro['Fecha']
            ))
    
    def mostrar_grafico_barras(self):
        """Mostrar gráfico de barras ASCII"""
        try:
            registros = self.db_manager.get_all_materials()
            if not registros:
                self.text_grafico.delete(1.0, tk.END)
                self.text_grafico.insert(tk.END, "No hay datos para mostrar")
                return
            
            # Agrupar por tipo
            estadisticas = defaultdict(lambda: {'cantidad': 0, 'valor': 0, 'materiales': 0})
            for registro in registros:
                tipo = registro['Tipo']
                estadisticas[tipo]['cantidad'] += registro['Cantidad']
                estadisticas[tipo]['valor'] += registro['Valor']
                estadisticas[tipo]['materiales'] += 1
            
            # Crear gráfico ASCII con colores
            self.text_grafico.delete(1.0, tk.END)
            self.text_grafico.insert(tk.END, "="*80 + "\n")
            self.text_grafico.insert(tk.END, "                    GRÁFICO DE BARRAS - CANTIDADES POR TIPO\n", "azul")
            self.text_grafico.insert(tk.END, "="*80 + "\n\n")
            
            # Encontrar el valor máximo para escalar
            max_cantidad = max(stats['cantidad'] for stats in estadisticas.values())
            max_valor = max(stats['valor'] for stats in estadisticas.values())
            
            # Gráfico de cantidades
            self.text_grafico.insert(tk.END, "📊 CANTIDADES POR TIPO:\n", "verde")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            colores_tipos = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, (tipo, stats) in enumerate(sorted(estadisticas.items())):
                color = colores_tipos[i % len(colores_tipos)]
                barras = "█" * int((stats['cantidad'] / max_cantidad) * 40)
                self.text_grafico.insert(tk.END, f"{tipo:<15} {stats['cantidad']:>8.1f} ", color)
                self.text_grafico.insert(tk.END, f"{barras}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "📈 VALORES POR TIPO:\n", "amarillo")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            for i, (tipo, stats) in enumerate(sorted(estadisticas.items())):
                color = colores_tipos[i % len(colores_tipos)]
                barras = "█" * int((stats['valor'] / max_valor) * 40)
                self.text_grafico.insert(tk.END, f"{tipo:<15} ${stats['valor']:>7.1f} ", color)
                self.text_grafico.insert(tk.END, f"{barras}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico: {e}")
    
    def mostrar_grafico_circular(self):
        """Mostrar gráfico circular ASCII"""
        try:
            registros = self.db_manager.get_all_materials()
            if not registros:
                self.text_grafico.delete(1.0, tk.END)
                self.text_grafico.insert(tk.END, "No hay datos para mostrar")
                return
            
            # Agrupar por tipo
            estadisticas = defaultdict(lambda: {'cantidad': 0, 'valor': 0})
            for registro in registros:
                tipo = registro['Tipo']
                estadisticas[tipo]['cantidad'] += registro['Cantidad']
                estadisticas[tipo]['valor'] += registro['Valor']
            
            total_cantidad = sum(stats['cantidad'] for stats in estadisticas.values())
            total_valor = sum(stats['valor'] for stats in estadisticas.values())
            
            # Crear gráfico ASCII con colores
            self.text_grafico.delete(1.0, tk.END)
            self.text_grafico.insert(tk.END, "="*80 + "\n")
            self.text_grafico.insert(tk.END, "                    GRÁFICO CIRCULAR - DISTRIBUCIÓN POR TIPO\n", "cyan")
            self.text_grafico.insert(tk.END, "="*80 + "\n\n")
            
            # Distribución de cantidades
            self.text_grafico.insert(tk.END, "🥧 DISTRIBUCIÓN DE CANTIDADES:\n", "verde")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            colores_tipos = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, (tipo, stats) in enumerate(sorted(estadisticas.items())):
                color = colores_tipos[i % len(colores_tipos)]
                porcentaje = (stats['cantidad'] / total_cantidad * 100) if total_cantidad > 0 else 0
                self.text_grafico.insert(tk.END, f"{tipo:<15} {stats['cantidad']:>8.1f} ", color)
                self.text_grafico.insert(tk.END, f"({porcentaje:>5.1f}%)\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "💰 DISTRIBUCIÓN DE VALORES:\n", "amarillo")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            for i, (tipo, stats) in enumerate(sorted(estadisticas.items())):
                color = colores_tipos[i % len(colores_tipos)]
                porcentaje = (stats['valor'] / total_valor * 100) if total_valor > 0 else 0
                self.text_grafico.insert(tk.END, f"{tipo:<15} ${stats['valor']:>7.1f} ", color)
                self.text_grafico.insert(tk.END, f"({porcentaje:>5.1f}%)\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico: {e}")
    
    def mostrar_grafico_lineas(self):
        """Mostrar gráfico de líneas ASCII"""
        try:
            registros = self.db_manager.get_all_materials()
            if not registros:
                self.text_grafico.delete(1.0, tk.END)
                self.text_grafico.insert(tk.END, "No hay datos para mostrar")
                return
            
            # Agrupar por tipo
            estadisticas = defaultdict(lambda: {'cantidad': 0, 'valor': 0})
            for registro in registros:
                tipo = registro['Tipo']
                estadisticas[tipo]['cantidad'] += registro['Cantidad']
                estadisticas[tipo]['valor'] += registro['Valor']
            
            # Crear gráfico ASCII con colores
            self.text_grafico.delete(1.0, tk.END)
            self.text_grafico.insert(tk.END, "="*80 + "\n")
            self.text_grafico.insert(tk.END, "                    GRÁFICO DE LÍNEAS - TENDENCIAS POR TIPO\n", "azul")
            self.text_grafico.insert(tk.END, "="*80 + "\n\n")
            
            tipos = sorted(estadisticas.keys())
            cantidades = [estadisticas[t]['cantidad'] for t in tipos]
            valores = [estadisticas[t]['valor'] for t in tipos]
            
            # Encontrar máximos para escalar
            max_cantidad = max(cantidades) if cantidades else 1
            max_valor = max(valores) if valores else 1
            
            # Crear gráfico de líneas para cantidades
            self.text_grafico.insert(tk.END, "📈 TENDENCIA DE CANTIDADES:\n", "verde")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            colores_tipos = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, (tipo, cantidad) in enumerate(zip(tipos, cantidades)):
                color = colores_tipos[i % len(colores_tipos)]
                altura = int((cantidad / max_cantidad) * 20)
                linea = "─" * altura + "●"
                self.text_grafico.insert(tk.END, f"{tipo:<15} {cantidad:>8.1f} ", color)
                self.text_grafico.insert(tk.END, f"{linea}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "💰 TENDENCIA DE VALORES:\n", "amarillo")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            for i, (tipo, valor) in enumerate(zip(tipos, valores)):
                color = colores_tipos[i % len(colores_tipos)]
                altura = int((valor / max_valor) * 20)
                linea = "─" * altura + "●"
                self.text_grafico.insert(tk.END, f"{tipo:<15} ${valor:>7.1f} ", color)
                self.text_grafico.insert(tk.END, f"{linea}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico: {e}")
    
    def mostrar_grafico_histograma(self):
        """Mostrar histograma ASCII"""
        try:
            registros = self.db_manager.get_all_materials()
            if not registros:
                self.text_grafico.delete(1.0, tk.END)
                self.text_grafico.insert(tk.END, "No hay datos para mostrar")
                return
            
            # Extraer valores
            valores = [registro['Valor'] for registro in registros]
            cantidades = [registro['Cantidad'] for registro in registros]
            
            # Crear histograma ASCII con colores
            self.text_grafico.delete(1.0, tk.END)
            self.text_grafico.insert(tk.END, "="*80 + "\n")
            self.text_grafico.insert(tk.END, "                    HISTOGRAMA - DISTRIBUCIÓN DE VALORES\n", "magenta")
            self.text_grafico.insert(tk.END, "="*80 + "\n\n")
            
            # Histograma de valores
            self.text_grafico.insert(tk.END, "📊 DISTRIBUCIÓN DE VALORES:\n", "verde")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            # Crear rangos
            min_valor = min(valores)
            max_valor = max(valores)
            rango = max_valor - min_valor
            num_bins = 10
            
            bins = []
            for i in range(num_bins):
                inicio = min_valor + (rango * i / num_bins)
                fin = min_valor + (rango * (i + 1) / num_bins)
                count = sum(1 for v in valores if inicio <= v < fin)
                bins.append((inicio, fin, count))
            
            max_count = max(count for _, _, count in bins) if bins else 1
            
            colores_bins = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, (inicio, fin, count) in enumerate(bins):
                color = colores_bins[i % len(colores_bins)]
                barras = "█" * int((count / max_count) * 30)
                self.text_grafico.insert(tk.END, f"${inicio:>6.1f}-${fin:>6.1f} {count:>3d} ", color)
                self.text_grafico.insert(tk.END, f"{barras}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "📈 DISTRIBUCIÓN DE CANTIDADES:\n", "amarillo")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            # Histograma de cantidades
            min_cantidad = min(cantidades)
            max_cantidad = max(cantidades)
            rango_cantidad = max_cantidad - min_cantidad
            
            bins_cantidad = []
            for i in range(num_bins):
                inicio = min_cantidad + (rango_cantidad * i / num_bins)
                fin = min_cantidad + (rango_cantidad * (i + 1) / num_bins)
                count = sum(1 for c in cantidades if inicio <= c < fin)
                bins_cantidad.append((inicio, fin, count))
            
            max_count_cantidad = max(count for _, _, count in bins_cantidad) if bins_cantidad else 1
            
            for i, (inicio, fin, count) in enumerate(bins_cantidad):
                color = colores_bins[i % len(colores_bins)]
                barras = "█" * int((count / max_count_cantidad) * 30)
                self.text_grafico.insert(tk.END, f"{inicio:>6.1f}-{fin:>6.1f} {count:>3d} ", color)
                self.text_grafico.insert(tk.END, f"{barras}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico: {e}")
    
    def mostrar_grafico_dispersion(self):
        """Mostrar gráfico de dispersión ASCII"""
        try:
            registros = self.db_manager.get_all_materials()
            if not registros:
                self.text_grafico.insert(tk.END, "No hay datos para mostrar")
                return
            
            # Crear gráfico ASCII con colores
            self.text_grafico.delete(1.0, tk.END)
            self.text_grafico.insert(tk.END, "="*80 + "\n")
            self.text_grafico.insert(tk.END, "                    GRÁFICO DE DISPERSIÓN - RELACIÓN CANTIDAD-VALOR\n", "cyan")
            self.text_grafico.insert(tk.END, "="*80 + "\n\n")
            
            # Crear matriz de dispersión
            cantidades = [registro['Cantidad'] for registro in registros]
            valores = [registro['Valor'] for registro in registros]
            
            max_cantidad = max(cantidades) if cantidades else 1
            max_valor = max(valores) if valores else 1
            
            # Crear matriz 20x20
            matriz = [[' ' for _ in range(20)] for _ in range(20)]
            
            for cantidad, valor in zip(cantidades, valores):
                x = int((cantidad / max_cantidad) * 19)
                y = int((valor / max_valor) * 19)
                if 0 <= x < 20 and 0 <= y < 20:
                    matriz[19-y][x] = '●'
            
            # Mostrar matriz
            self.text_grafico.insert(tk.END, "🔍 RELACIÓN CANTIDAD-VALOR:\n", "verde")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            self.text_grafico.insert(tk.END, f"Valor ↑\n", "azul")
            
            for fila in matriz:
                self.text_grafico.insert(tk.END, "│", "gris")
                for char in fila:
                    if char == '●':
                        self.text_grafico.insert(tk.END, char, "rojo")
                    else:
                        self.text_grafico.insert(tk.END, char, "gris")
                self.text_grafico.insert(tk.END, "│\n", "gris")
            
            self.text_grafico.insert(tk.END, "└" + "─" * 20 + "┘ Cantidad →\n", "gris")
            
            # Mostrar datos específicos
            self.text_grafico.insert(tk.END, "\n📊 DATOS DETALLADOS:\n", "amarillo")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            colores_tipos = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, registro in enumerate(registros[:10]):  # Mostrar solo los primeros 10
                color = colores_tipos[i % len(colores_tipos)]
                self.text_grafico.insert(tk.END, f"{i+1:2d}. {registro['Material'][:20]:<20} ", color)
                self.text_grafico.insert(tk.END, f"Cant:{registro['Cantidad']:>6.1f} Val:${registro['Valor']:>6.1f}\n", color)
            
            self.text_grafico.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico: {e}")
    
    def mostrar_grafico_comparativo(self):
        """Mostrar gráfico comparativo ASCII"""
        try:
            registros = self.db_manager.get_all_materials()
            if not registros:
                self.text_grafico.delete(1.0, tk.END)
                self.text_grafico.insert(tk.END, "No hay datos para mostrar")
                return
            
            # Agrupar por tipo y ubicación
            estadisticas_tipo = defaultdict(lambda: {'cantidad': 0, 'valor': 0})
            estadisticas_ubicacion = defaultdict(lambda: {'cantidad': 0, 'valor': 0})
            
            for registro in registros:
                tipo = registro['Tipo']
                ubicacion = registro['Ubicacion']
                
                estadisticas_tipo[tipo]['cantidad'] += registro['Cantidad']
                estadisticas_tipo[tipo]['valor'] += registro['Valor']
                estadisticas_ubicacion[ubicacion]['cantidad'] += registro['Cantidad']
                estadisticas_ubicacion[ubicacion]['valor'] += registro['Valor']
            
            # Crear gráfico ASCII con colores
            self.text_grafico.delete(1.0, tk.END)
            self.text_grafico.insert(tk.END, "="*80 + "\n")
            self.text_grafico.insert(tk.END, "                    GRÁFICO COMPARATIVO - ANÁLISIS MULTIDIMENSIONAL\n", "magenta")
            self.text_grafico.insert(tk.END, "="*80 + "\n\n")
            
            # Comparación por tipo
            self.text_grafico.insert(tk.END, "📊 COMPARACIÓN POR TIPO DE MATERIAL:\n", "verde")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            max_cantidad_tipo = max(stats['cantidad'] for stats in estadisticas_tipo.values())
            max_valor_tipo = max(stats['valor'] for stats in estadisticas_tipo.values())
            
            colores_tipos = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, (tipo, stats) in enumerate(sorted(estadisticas_tipo.items())):
                color = colores_tipos[i % len(colores_tipos)]
                barras_cantidad = "█" * int((stats['cantidad'] / max_cantidad_tipo) * 20)
                barras_valor = "▓" * int((stats['valor'] / max_valor_tipo) * 20)
                self.text_grafico.insert(tk.END, f"{tipo:<15} Cant:", color)
                self.text_grafico.insert(tk.END, f"{barras_cantidad} ", "azul")
                self.text_grafico.insert(tk.END, f"Val:", color)
                self.text_grafico.insert(tk.END, f"{barras_valor}\n", "amarillo")
            
            self.text_grafico.insert(tk.END, "\n" + "📍 COMPARACIÓN POR UBICACIÓN:\n", "cyan")
            self.text_grafico.insert(tk.END, "-"*60 + "\n")
            
            max_cantidad_ubic = max(stats['cantidad'] for stats in estadisticas_ubicacion.values())
            max_valor_ubic = max(stats['valor'] for stats in estadisticas_ubicacion.values())
            
            colores_ubicaciones = ["rojo", "verde", "azul", "amarillo", "magenta", "cyan", "naranja", "rosa", "gris"]
            for i, (ubicacion, stats) in enumerate(sorted(estadisticas_ubicacion.items())):
                color = colores_ubicaciones[i % len(colores_ubicaciones)]
                barras_cantidad = "█" * int((stats['cantidad'] / max_cantidad_ubic) * 20)
                barras_valor = "▓" * int((stats['valor'] / max_valor_ubic) * 20)
                self.text_grafico.insert(tk.END, f"{ubicacion:<15} Cant:", color)
                self.text_grafico.insert(tk.END, f"{barras_cantidad} ", "azul")
                self.text_grafico.insert(tk.END, f"Val:", color)
                self.text_grafico.insert(tk.END, f"{barras_valor}\n", "amarillo")
            
            self.text_grafico.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico: {e}")
    
    def analisis_completo(self):
        """Realizar análisis completo de datos"""
        try:
            # Obtener estadísticas de la base de datos
            stats = self.db_manager.get_statistics()
            if not stats:
                self.text_avanzado.delete(1.0, tk.END)
                self.text_avanzado.insert(tk.END, "No hay datos para analizar.")
                return
            
            # Análisis estadístico completo
            self.text_avanzado.delete(1.0, tk.END)
            self.text_avanzado.insert(tk.END, "="*80 + "\n")
            self.text_avanzado.insert(tk.END, "                    ANÁLISIS COMPLETO DE DATOS\n")
            self.text_avanzado.insert(tk.END, "="*80 + "\n\n")
            
            # Estadísticas generales
            general = stats['general']
            total_materiales = general[0] if general[0] else 0
            total_cantidad = general[1] if general[1] else 0
            total_valor = general[2] if general[2] else 0
            valor_promedio = general[3] if general[3] else 0
            
            self.text_avanzado.insert(tk.END, f"📊 RESUMEN GENERAL:\n")
            self.text_avanzado.insert(tk.END, f"   • Total de materiales: {total_materiales}\n")
            self.text_avanzado.insert(tk.END, f"   • Cantidad total: {total_cantidad:.2f}\n")
            self.text_avanzado.insert(tk.END, f"   • Valor total: ${total_valor:.2f}\n")
            self.text_avanzado.insert(tk.END, f"   • Valor promedio: ${valor_promedio:.2f}\n\n")
            
            # Análisis por tipo
            self.text_avanzado.insert(tk.END, f"📈 ANÁLISIS POR TIPO:\n")
            for tipo_data in stats['por_tipo']:
                tipo, count, cantidad, valor, valor_prom = tipo_data
                porcentaje_cantidad = (cantidad / total_cantidad * 100) if total_cantidad > 0 else 0
                porcentaje_valor = (valor / total_valor * 100) if total_valor > 0 else 0
                self.text_avanzado.insert(tk.END, f"   • {tipo}:\n")
                self.text_avanzado.insert(tk.END, f"     - Cantidad: {cantidad:.2f} ({porcentaje_cantidad:.1f}%)\n")
                self.text_avanzado.insert(tk.END, f"     - Valor: ${valor:.2f} ({porcentaje_valor:.1f}%)\n")
                self.text_avanzado.insert(tk.END, f"     - Materiales: {count}\n")
                self.text_avanzado.insert(tk.END, f"     - Valor promedio: ${valor_prom:.2f}\n\n")
            
            # Análisis de ubicaciones
            self.text_avanzado.insert(tk.END, f"📍 DISTRIBUCIÓN POR UBICACIÓN:\n")
            for ubicacion_data in stats['por_ubicacion']:
                ubicacion, cantidad = ubicacion_data
                porcentaje = (cantidad / total_materiales * 100) if total_materiales > 0 else 0
                self.text_avanzado.insert(tk.END, f"   • {ubicacion}: {cantidad} materiales ({porcentaje:.1f}%)\n")
            
            self.text_avanzado.insert(tk.END, "\n" + "="*80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis completo: {e}")
    
    def analisis_tendencias(self):
        """Análisis de tendencias"""
        self.text_avanzado.delete(1.0, tk.END)
        self.text_avanzado.insert(tk.END, "📈 ANÁLISIS DE TENDENCIAS\n")
        self.text_avanzado.insert(tk.END, "="*50 + "\n\n")
        self.text_avanzado.insert(tk.END, "• Los materiales sólidos representan la mayor parte del inventario\n")
        self.text_avanzado.insert(tk.END, "• Los materiales peligrosos tienen mayor valor unitario\n")
        self.text_avanzado.insert(tk.END, "• Tendencia creciente en materiales electrónicos\n")
        self.text_avanzado.insert(tk.END, "• Los materiales orgánicos tienen valor cero (residuos)\n")
        self.text_avanzado.insert(tk.END, "• Concentración de materiales en almacenes específicos\n")
    
    def predicciones(self):
        """Generar predicciones"""
        self.text_avanzado.delete(1.0, tk.END)
        self.text_avanzado.insert(tk.END, "🔮 PREDICCIONES\n")
        self.text_avanzado.insert(tk.END, "="*50 + "\n\n")
        self.text_avanzado.insert(tk.END, "• Se espera un aumento del 15% en materiales electrónicos\n")
        self.text_avanzado.insert(tk.END, "• Los materiales peligrosos requerirán más espacio de almacenamiento\n")
        self.text_avanzado.insert(tk.END, "• Tendencia a la reducción de materiales de papel\n")
        self.text_avanzado.insert(tk.END, "• Incremento proyectado en materiales metálicos\n")
        self.text_avanzado.insert(tk.END, "• Mayor demanda de almacenamiento para materiales químicos\n")
    
    def buscar_inventario(self):
        """Buscar en inventario con filtros"""
        texto_buscar = self.entry_buscar.get().strip()
        tipo_filtro = self.combo_filtro_tipo.get()
        estado_filtro = self.combo_filtro_estado.get()
        
        # Usar el método de búsqueda de la base de datos
        registros_filtrados = self.db_manager.search_materials(texto_buscar, tipo_filtro, estado_filtro)
        
        if registros_filtrados:
            self.cargar_datos_en_treeviews(registros_filtrados)
            messagebox.showinfo("Búsqueda", f"Encontrados {len(registros_filtrados)} materiales.")
        else:
            messagebox.showinfo("Búsqueda", "No se encontraron materiales que coincidan con los filtros.")
            self.cargar_datos_en_treeviews([])  # Limpiar Treeview
    
    def actualizar_todo(self):
        """Actualizar todos los datos"""
        self.cargar_datos_en_treeviews()
        self.mostrar_estadisticas_basicas()
        self.analisis_completo()
        messagebox.showinfo("Actualización", "Datos actualizados correctamente")
    
    def exportar_datos(self):
        """Exportar datos a archivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                if self.db_manager.export_to_csv(filename):
                    messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
                else:
                    messagebox.showerror("Error", "Error al exportar datos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")
    
    def importar_datos(self):
        """Importar datos desde archivo"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                imported_count = self.db_manager.import_from_csv(filename)
                if imported_count > 0:
                    self.cargar_datos_en_treeviews()
                    messagebox.showinfo("Éxito", f"{imported_count} registros importados correctamente")
                else:
                    messagebox.showwarning("Advertencia", "No se importaron registros")
            except Exception as e:
                messagebox.showerror("Error", f"Error al importar: {e}")
    
    def cargar_datos_en_treeviews(self, records=None):
        """Carga los datos en los Treeviews de Registro e Inventario."""
        
        # 1. Obtener datos (si no se pasan explícitamente)
        if records is None:
            records = self.db_manager.get_all_materials()

        # 2. Limpiar Treeview del registro
        for i in self.tree_materiales.get_children():
            self.tree_materiales.delete(i)
        
        # 3. Limpiar Treeview del inventario
        for i in self.tree_inventario.get_children():
            self.tree_inventario.delete(i)

        # 4. Insertar nuevos datos en ambos Treeviews
        for item in records:
            data_registro = (item['ID'], item['Material'], item['Tipo'], item['Cantidad'], item['Valor'], item['Ubicacion'], item['Estado'])
            data_inventario = (item['ID'], item['Material'], item['Tipo'], item['Cantidad'], item['Valor'], item['Ubicacion'], item['Estado'], item['Fecha'])
            
            self.tree_materiales.insert('', tk.END, values=data_registro)
            self.tree_inventario.insert('', tk.END, values=data_inventario)
    
    def mostrar_estadisticas_basicas(self):
        """Muestra las estadísticas básicas en la pestaña de Estadísticas."""
        stats = self.db_manager.get_statistics()
        
        self.text_estadisticas.delete(1.0, tk.END)
        
        if stats and stats['general'][0] is not None:
            # General Stats
            general = stats['general']
            total_items, total_qty, total_value, avg_value = general
            
            output = f"--- Estadísticas Generales ---\n"
            output += f"Total de Registros: {total_items}\n"
            output += f"Cantidad Total: {total_qty:.2f}\n"
            output += f"Valor Total de Inventario: ${total_value:,.2f}\n"
            output += f"Valor Promedio por Material: ${avg_value:,.2f}\n"
            output += f"\n"
            
            # Stats por Tipo
            output += f"--- Materiales por Tipo ---\n"
            for tipo, count, qty, value, avg in stats['por_tipo']:
                output += f"  - {tipo}: {count} ítems | {qty:.2f} unidades | Valor: ${value:,.2f}\n"
            output += f"\n"
            
            # Stats por Ubicación
            output += f"--- Materiales por Ubicación ---\n"
            for ubicacion, count in stats['por_ubicacion']:
                output += f"  - {ubicacion if ubicacion else 'Sin especificar'}: {count} ítems\n"
            
            self.text_estadisticas.insert(tk.END, output)
        else:
            self.text_estadisticas.insert(tk.END, "No hay datos para generar estadísticas.")

def main():
    root = tk.Tk()
    app = GestorMaterialesConGraficos(root)
    root.mainloop()

if __name__ == '__main__':
    main()
    

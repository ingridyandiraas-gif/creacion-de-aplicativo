import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict

class GestorMateriales:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Materiales - Interfaz Gráfica")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Archivo CSV para guardar datos
        self.archivo = 'registros.csv'
        
        # Inicializar archivo
        self.inicializar_archivo()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()
    
    def inicializar_archivo(self):
        """Crear archivo si no existe"""
        try:
            if not os.path.exists(self.archivo):
                with open(self.archivo, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Material', 'Tipo', 'Cantidad', 'Valor'])
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar el archivo: {e}")
    
    def leer_registros(self):
        """Leer todos los registros del archivo CSV"""
        try:
            registros = []
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        registros.append({
                            'Material': row['Material'],
                            'Tipo': row['Tipo'],
                            'Cantidad': float(row['Cantidad']),
                            'Valor': float(row['Valor'])
                        })
            return registros
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo: {e}")
            return []
    
    def escribir_registros(self, registros):
        """Escribir todos los registros al archivo CSV"""
        try:
            with open(self.archivo, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Material', 'Tipo', 'Cantidad', 'Valor'])
                for registro in registros:
                    writer.writerow([registro['Material'], registro['Tipo'], 
                                   registro['Cantidad'], registro['Valor']])
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al escribir el archivo: {e}")
            return False
    
    def crear_interfaz(self):
        """Crear la interfaz gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Gestor de Materiales", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame para registro de materiales
        frame_registro = ttk.LabelFrame(main_frame, text="Registrar Nuevo Material", padding="10")
        frame_registro.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Campos de entrada
        ttk.Label(frame_registro, text="Nombre del Material:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_nombre = ttk.Entry(frame_registro, width=30)
        self.entry_nombre.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(frame_registro, text="Tipo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.combo_tipo = ttk.Combobox(frame_registro, values=['Solido', 'Peligroso', 'Organico', 'Liquido'], width=27)
        self.combo_tipo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(frame_registro, text="Cantidad:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_cantidad = ttk.Entry(frame_registro, width=30)
        self.entry_cantidad.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(frame_registro, text="Valor:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_valor = ttk.Entry(frame_registro, width=30)
        self.entry_valor.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Botón registrar
        btn_registrar = ttk.Button(frame_registro, text="Registrar Material", 
                                  command=self.registrar_material)
        btn_registrar.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Frame para búsqueda
        frame_busqueda = ttk.LabelFrame(main_frame, text="Buscar Materiales", padding="10")
        frame_busqueda.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(frame_busqueda, text="Tipo a buscar:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.combo_buscar = ttk.Combobox(frame_busqueda, values=['Todos', 'Solido', 'Peligroso', 'Organico', 'Liquido'], width=27)
        self.combo_buscar.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.combo_buscar.set('Todos')
        
        btn_buscar = ttk.Button(frame_busqueda, text="Buscar", command=self.buscar_materiales)
        btn_buscar.grid(row=0, column=2, padx=(5, 0))
        
        btn_estadisticas = ttk.Button(frame_busqueda, text="Ver Estadísticas", command=self.mostrar_estadisticas)
        btn_estadisticas.grid(row=0, column=3, padx=(5, 0))
        
        # Área de resultados
        frame_resultados = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        frame_resultados.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        frame_resultados.rowconfigure(0, weight=1)
        frame_resultados.columnconfigure(0, weight=1)
        
        # Treeview para mostrar datos
        columns = ('Material', 'Tipo', 'Cantidad', 'Valor')
        self.tree = ttk.Treeview(frame_resultados, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(frame_resultados, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame para estadísticas
        frame_stats = ttk.LabelFrame(main_frame, text="Estadísticas", padding="10")
        frame_stats.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.text_stats = scrolledtext.ScrolledText(frame_stats, height=6, width=70)
        self.text_stats.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Botones adicionales
        frame_botones = ttk.Frame(main_frame)
        frame_botones.grid(row=5, column=0, columnspan=3, pady=10)
        
        btn_limpiar = ttk.Button(frame_botones, text="Limpiar Campos", command=self.limpiar_campos)
        btn_limpiar.grid(row=0, column=0, padx=5)
        
        btn_actualizar = ttk.Button(frame_botones, text="Actualizar Lista", command=self.actualizar_lista)
        btn_actualizar.grid(row=0, column=1, padx=5)
        
        btn_salir = ttk.Button(frame_botones, text="Salir", command=self.root.quit)
        btn_salir.grid(row=0, column=2, padx=5)
    
    def cargar_datos_iniciales(self):
        """Cargar datos de ejemplo al iniciar"""
        # Verificar si ya hay datos
        registros = self.leer_registros()
        if not registros:
            # Agregar datos de ejemplo
            datos_ejemplo = [
                ('Botella Plástica', 'Solido', 5, 10),
                ('Batería', 'Peligroso', 2, 15),
                ('Restos de Comida', 'Organico', 3, 0)
            ]
            
            for nombre, tipo, cantidad, valor in datos_ejemplo:
                self.registrar_material_silencioso(nombre, tipo, cantidad, valor)
        
        # Actualizar la lista
        self.actualizar_lista()
    
    def registrar_material_silencioso(self, nombre, tipo, cantidad, valor):
        """Registrar material sin mostrar mensajes"""
        registros = self.leer_registros()
        
        # Evitar duplicados
        for registro in registros:
            if (registro['Material'].lower() == nombre.lower() and 
                registro['Tipo'].lower() == tipo.lower()):
                return False
        
        nuevo_registro = {
            'Material': nombre,
            'Tipo': tipo,
            'Cantidad': cantidad,
            'Valor': valor
        }
        registros.append(nuevo_registro)
        
        return self.escribir_registros(registros)
    
    def registrar_material(self):
        """Registrar un nuevo material"""
        nombre = self.entry_nombre.get().strip()
        tipo = self.combo_tipo.get().strip()
        cantidad_str = self.entry_cantidad.get().strip()
        valor_str = self.entry_valor.get().strip()
        
        # Validaciones
        if not nombre or not tipo:
            messagebox.showerror("Error", "El nombre y tipo no pueden estar vacíos")
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
        
        # Leer registros existentes
        registros = self.leer_registros()
        
        # Evitar duplicados
        for registro in registros:
            if (registro['Material'].lower() == nombre.lower() and 
                registro['Tipo'].lower() == tipo.lower()):
                messagebox.showwarning("Advertencia", f'El material "{nombre}" de tipo "{tipo}" ya está registrado')
                return
        
        # Agregar nuevo registro
        nuevo_registro = {
            'Material': nombre,
            'Tipo': tipo,
            'Cantidad': cantidad,
            'Valor': valor
        }
        registros.append(nuevo_registro)
        
        if self.escribir_registros(registros):
            messagebox.showinfo("Éxito", f'Material "{nombre}" registrado correctamente')
            self.limpiar_campos()
            self.actualizar_lista()
    
    def buscar_materiales(self):
        """Buscar materiales por tipo"""
        tipo_buscar = self.combo_buscar.get()
        registros = self.leer_registros()
        
        if not registros:
            messagebox.showinfo("Información", "No hay materiales registrados")
            return
        
        # Filtrar por tipo
        if tipo_buscar == 'Todos':
            materiales_filtrados = registros
        else:
            materiales_filtrados = [r for r in registros if r['Tipo'].lower() == tipo_buscar.lower()]
        
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Mostrar resultados
        if not materiales_filtrados:
            messagebox.showinfo("Información", f"No hay materiales del tipo: {tipo_buscar}")
        else:
            for material in materiales_filtrados:
                self.tree.insert('', 'end', values=(
                    material['Material'],
                    material['Tipo'],
                    material['Cantidad'],
                    material['Valor']
                ))
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas en el área de texto"""
        registros = self.leer_registros()
        
        if not registros:
            self.text_stats.delete(1.0, tk.END)
            self.text_stats.insert(tk.END, "No hay datos para mostrar estadísticas.")
            return
        
        # Agrupar por tipo
        estadisticas = defaultdict(lambda: {'Cantidad': 0, 'Valor': 0})
        
        for registro in registros:
            tipo = registro['Tipo']
            estadisticas[tipo]['Cantidad'] += registro['Cantidad']
            estadisticas[tipo]['Valor'] += registro['Valor']
        
        # Mostrar estadísticas
        self.text_stats.delete(1.0, tk.END)
        self.text_stats.insert(tk.END, "--- Resumen Estadístico ---\n")
        self.text_stats.insert(tk.END, f"{'Tipo':<15} {'Total Cantidad':<15} {'Total Valor':<15}\n")
        self.text_stats.insert(tk.END, "-" * 45 + "\n")
        
        for tipo, stats in estadisticas.items():
            self.text_stats.insert(tk.END, f"{tipo:<15} {stats['Cantidad']:<15} {stats['Valor']:<15}\n")
    
    def limpiar_campos(self):
        """Limpiar todos los campos de entrada"""
        self.entry_nombre.delete(0, tk.END)
        self.combo_tipo.set('')
        self.entry_cantidad.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
    
    def actualizar_lista(self):
        """Actualizar la lista con todos los materiales"""
        registros = self.leer_registros()
        
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Mostrar todos los registros
        for material in registros:
            self.tree.insert('', 'end', values=(
                material['Material'],
                material['Tipo'],
                material['Cantidad'],
                material['Valor']
            ))

def main():
    root = tk.Tk()
    app = GestorMateriales(root)
    root.mainloop()

if __name__ == '__main__':
    main()
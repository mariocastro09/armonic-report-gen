import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk # ttk añadido
import sqlite3
import pandas as pd
import plotly.express as px
import os
import webbrowser
import traceback # Para imprimir errores completos
import re # Para expresiones regulares (ayuda a extraer prefijos)
from collections import defaultdict # Para crear diccionarios con valores por defecto
import threading # Para ejecutar la generación en un hilo separado y no bloquear la GUI
from pathlib import Path # Para manejar nombres de archivo de forma más robusta

# --- Funciones del script original de generación de Plotly (lógica principal) ---
# (Estas funciones se mantienen, solo se adaptará cómo se llaman desde la nueva GUI
# y cómo interactúan con los widgets de la GUI, especialmente para el logging)

gui_log_text_widget = None # Variable global para el widget de log de la GUI

def log_message(message):
    """Función para imprimir mensajes tanto en consola como en la GUI si está disponible."""
    print(message) # Mantener el log en consola
    if gui_log_text_widget:
        if gui_log_text_widget.winfo_exists():
            gui_log_text_widget.insert(tk.END, message + "\n")
            gui_log_text_widget.see(tk.END)
            gui_log_text_widget.update_idletasks()

def get_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    return tables

def validate_and_prepare_data(df, table_name):
    if df.empty:
        return df
    if len(df) < 2:
        log_message(f"  - Warning: Table {table_name} has only {len(df)} data points. Plot may not be meaningful.")
    if "spectrum" in table_name.lower():
        if 'ValueX' in df.columns:
            negative_x = df['ValueX'] < 0
            if negative_x.any():
                log_message(f"  - Warning: Removing {negative_x.sum()} negative ValueX values from {table_name}")
                df = df[~negative_x]
                if df.empty:
                    log_message(f"  - Table {table_name} became empty after removing negative ValueX. Skipping plot.")
                    return df
    MAX_POINTS = 10000
    if len(df) > MAX_POINTS:
        log_message(f"  - Info: Sampling {MAX_POINTS} points from {len(df)} total points in {table_name}")
        df = df.sample(n=MAX_POINTS, random_state=42).sort_values('ValueX')
    return df

def get_sorted_table_list(table_names_from_db, tables_to_omit_lower):
    grouped_tables = defaultdict(list)
    processed_tables = set()
    type_priority = {"hz": 1, "order": 2, "waveform": 3, "other": 4}
    suffix_patterns = [
        (re.compile(r"^(.*?)_Spectrum_Hz_?\d*$", re.IGNORECASE), "hz"),
        (re.compile(r"^(.*?)_Spectrum_Order_?\d*$", re.IGNORECASE), "order"),
        (re.compile(r"^(.*?)_Waveform_?\d*$", re.IGNORECASE), "waveform"),
    ]
    other_tables_to_plot = []
    for table_name in table_names_from_db:
        if table_name.lower() in tables_to_omit_lower:
            continue
        matched = False
        for pattern, type_key in suffix_patterns:
            match = pattern.match(table_name)
            if match:
                prefix = match.group(1)
                if table_name not in processed_tables:
                    grouped_tables[prefix].append((type_priority[type_key], type_key, table_name))
                    processed_tables.add(table_name)
                matched = True
                break
        if not matched and table_name not in processed_tables:
            other_tables_to_plot.append(table_name)
    for prefix in grouped_tables:
        grouped_tables[prefix].sort(key=lambda x: x[0])
    sorted_prefixes = sorted(grouped_tables.keys())
    final_ordered_tables = []
    for prefix in sorted_prefixes:
        for priority, type_key, full_table_name in grouped_tables[prefix]:
            final_ordered_tables.append(full_table_name)
    for table_name in other_tables_to_plot:
        if table_name not in final_ordered_tables:
             final_ordered_tables.append(table_name)
    if not final_ordered_tables and not other_tables_to_plot:
        return table_names_from_db
    return final_ordered_tables

def generate_html_report_process(db_path, output_html_filename):
    if not db_path:
        log_message("No database file selected.")
        messagebox.showerror("Error", "No database file selected.")
        return
    if not output_html_filename:
        log_message("No output HTML file specified.")
        messagebox.showerror("Error", "No output HTML file specified.")
        return

    STANDARD_WIDTH = 700
    STANDARD_HEIGHT = 500
    MARGIN_CONFIG = dict(l=60, r=60, t=60, b=60)
    try:
        conn = sqlite3.connect(db_path)
        all_table_names_from_db = get_table_names(conn)
        tables_to_omit = ["DeviceID_IID", "SystemFrequency"]
        tables_to_omit_lower = [name.lower() for name in tables_to_omit]
        ordered_tables_to_process = get_sorted_table_list(all_table_names_from_db, tables_to_omit_lower)
        log_message(f"Database: {os.path.basename(db_path)}")
        log_message(f"Found {len(all_table_names_from_db)} tables in DB.")
        log_message(f"Processing {len(ordered_tables_to_process)} tables in sorted order.")
        plot_html_parts = []
        processed_tables_count = 0
        for table_name in ordered_tables_to_process:
            if table_name.lower() in tables_to_omit_lower:
                continue
            log_message(f"Processing table: {table_name}")
            try:
                df = pd.read_sql_query(f"SELECT * FROM \"{table_name}\";", conn)
                if df.empty:
                    log_message(f"  - Table {table_name} is empty initially. Skipping plot.")
                    continue
                required_cols = ['ValueX', 'ValueY']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    log_message(f"  - Table {table_name} is missing required column(s): {', '.join(missing_cols)}. Skipping plot.")
                    log_message(f"    Available columns: {df.columns.tolist()}")
                    continue
                df['ValueX'] = pd.to_numeric(df['ValueX'], errors='coerce')
                df['ValueY'] = pd.to_numeric(df['ValueY'], errors='coerce')
                df.dropna(subset=['ValueX', 'ValueY'], inplace=True)
                df = validate_and_prepare_data(df, table_name)
                if df.empty:
                    log_message(f"  - Table {table_name} is empty after data validation. Skipping plot.")
                    continue
                fig = None
                title_base_text = f"{table_name}" 
                table_name_lower = table_name.lower()
                if "waveform" in table_name_lower:
                    hover_data = list(df.columns.difference(['ValueX', 'ValueY']))
                    df_sorted = df.sort_values(by='ValueX')
                    fig = px.line(df_sorted, x='ValueX', y='ValueY', title=title_base_text, hover_data=hover_data)
                    fig.update_layout(width=STANDARD_WIDTH, height=STANDARD_HEIGHT, margin=MARGIN_CONFIG, showlegend=False, xaxis_title="Tiempo (s)", yaxis_title="Amplitud (unidad)")
                    fig.update_traces(line=dict(width=1.5))
                    log_message(f"  - Type: Waveform (line plot). Sorting by ValueX. Columns: {df_sorted.columns.tolist()}")
                elif "spectrum_hz" in table_name_lower:
                    df_sorted = df.sort_values(by='ValueX')
                    df_sorted['ValueX_display'] = df_sorted['ValueX'].astype(str)
                    fig = px.bar(df_sorted, x='ValueX_display', y='ValueY', title=title_base_text)
                    fig.update_traces(width=0.4, marker=dict(line=dict(width=0.5, color='darkblue'), color='lightblue'))
                    fig.update_layout(width=STANDARD_WIDTH, height=STANDARD_HEIGHT, margin=MARGIN_CONFIG, showlegend=False, xaxis_title="Frecuencia (Hz)", yaxis_title="Magnitud (Hz)", bargap=0.1)
                    fig.update_xaxes(type='category')
                    log_message(f"  - Type: Spectrum Hz (bar plot). Columns: {df_sorted.columns.tolist()}")
                elif "spectrum_order" in table_name_lower:
                    df_sorted = df.sort_values(by='ValueX')
                    df_sorted['ValueX_display'] = df_sorted['ValueX'].astype(str)
                    fig = px.bar(df_sorted, x='ValueX_display', y='ValueY', title=title_base_text)
                    fig.update_traces(width=0.4, marker=dict(line=dict(width=0.5, color='darkslateblue'), color='lightsteelblue'))
                    fig.update_layout(width=STANDARD_WIDTH, height=STANDARD_HEIGHT, margin=MARGIN_CONFIG, showlegend=False, xaxis_title="Orden", yaxis_title="Magnitud (Orden)", bargap=0.1)
                    fig.update_xaxes(type='category')
                    log_message(f"  - Type: Spectrum Order (bar plot). Columns: {df_sorted.columns.tolist()}")
                else:
                    df_sorted = df.sort_values(by='ValueX')
                    fig = px.scatter(df_sorted, x='ValueX', y='ValueY', title=title_base_text)
                    fig.update_traces(marker=dict(size=6, opacity=0.7, line=dict(width=1, color='darkblue')))
                    fig.update_layout(width=STANDARD_WIDTH, height=STANDARD_HEIGHT, margin=MARGIN_CONFIG, showlegend=False, xaxis_title="Valor X (genérico)", yaxis_title="Valor Y (genérico)")
                    log_message(f"  - Type: Generic Scatter plot. Columns: {df_sorted.columns.tolist()}")
                if fig:
                    fig.update_layout(
                        title=dict(text=title_base_text, x=0.5, font=dict(size=14, color='darkblue')),
                        plot_bgcolor='white', paper_bgcolor='white', font=dict(size=11),
                        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray', showline=True, linewidth=1, linecolor='black'),
                        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray', showline=True, linewidth=1, linecolor='black')
                    )
                    if processed_tables_count < 3:
                        log_message(f"--- DEBUG INFO FOR: {table_name} ---")
                        log_message(f"Data points: {len(df)}")
                        if not df.empty:
                            log_message(f"ValueX range: {df['ValueX'].min():.2f} to {df['ValueX'].max():.2f}")
                            log_message(f"ValueY range: {df['ValueY'].min():.2f} to {df['ValueY'].max():.2f}")
                        else:
                            log_message("DataFrame is empty, cannot show ranges.")
                        log_message(f"Plot size: {STANDARD_WIDTH}x{STANDARD_HEIGHT}")
                        log_message("---")
                    plot_html_parts.append(fig.to_html(full_html=False, include_plotlyjs=False))
                    processed_tables_count += 1
                else:
                    log_message(f"  - Figure was not generated for table {table_name} despite passing data checks.")
            except pd.errors.DatabaseError as e:
                log_message(f"Pandas DatabaseError reading table {table_name}: {e}")
            except Exception as e:
                log_message(f"An unexpected error occurred while processing table {table_name}: {e}")
                if gui_log_text_widget:
                    gui_log_text_widget.insert(tk.END, traceback.format_exc() + "\n")
                    gui_log_text_widget.see(tk.END)
                else:
                    traceback.print_exc()
        conn.close()
        html_start = f"""
        <html><head><meta charset="UTF-8">
        <title>Database Plot Report - {os.path.basename(db_path)}</title>
        <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; color: #333; line-height: 1.6; }}
            h1 {{ text-align: center; color: #2c3e50; margin-bottom: 10px; }}
            .report-header {{ text-align: center; margin-bottom: 600px; padding: 40px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .plot-container {{ border: 1px solid #dee2e6; margin: 200px auto; padding: 15px; background-color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: visible; width: {STANDARD_WIDTH + 50}px; max-width: 95vw; }}
            .plot-container > div {{ margin: 0 auto; }}
            @media (max-width: {STANDARD_WIDTH + 100}px) {{ .plot-container {{ width: 95%; padding: 10px; }} }}
        </style></head><body>
        <div class="report-header">
            <h1>📊 REPORTE ESPECTRO ARMONICO-FORMAS DE ONDA</h1>
            <p>Generado desde: <strong>{os.path.basename(db_path)}</strong></p>
            <p>Total de gráficos generados: <strong>{processed_tables_count}</strong></p>
            <p><em>Todos los gráficos están estandarizados a {STANDARD_WIDTH}x{STANDARD_HEIGHT}px</em></p>
        </div>
        """
        if not plot_html_parts:
            log_message("\nNo data to plot or no suitable tables found.")
            html_content = html_start + f"""
            <div style="text-align: center; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px auto; max-width: 750px;">
                <h2>No se generaron gráficos</h2>
                <p>No se pudieron generar gráficos. Revise la consola/log para detalles.</p>
            </div></body></html>"""
            with open(output_html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            log_message(f"Generated empty report: {os.path.abspath(output_html_filename)}")
            try:
                webbrowser.open(f"file://{os.path.abspath(output_html_filename)}")
            except Exception as e:
                log_message(f"Could not automatically open the HTML file: {e}")
            messagebox.showinfo("Reporte Vacío", f"No se generaron gráficos. El reporte vacío se guardó en:\n{output_html_filename}")
            return
        html_end = "</body></html>"
        final_html_content = html_start
        for i, plot_div in enumerate(plot_html_parts):
            final_html_content += f"<div class='plot-container' id='plot-{i}'>\n{plot_div}\n</div>\n"
        final_html_content += html_end
        with open(output_html_filename, 'w', encoding='utf-8') as f:
            f.write(final_html_content)
        log_message(f"\nSuccessfully generated HTML report with {processed_tables_count} plot(s): {os.path.abspath(output_html_filename)}")
        messagebox.showinfo("Éxito", f"Reporte HTML generado con éxito:\n{output_html_filename}")
        try:
            webbrowser.open(f"file://{os.path.abspath(output_html_filename)}")
        except Exception as e:
            log_message(f"Could not automatically open the HTML file: {e}")
    except sqlite3.Error as e:
        log_message(f"SQLite error: {e}")
        messagebox.showerror("SQLite Error", f"Error con la base de datos:\n{e}")
    except Exception as e:
        log_message(f"An critical unexpected error occurred: {e}")
        if gui_log_text_widget:
            gui_log_text_widget.insert(tk.END, traceback.format_exc() + "\n")
            gui_log_text_widget.see(tk.END)
        else:
            traceback.print_exc()
        messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado:\n{e}")

# --- Funciones para la GUI (adaptadas del segundo script) ---
class ReportGeneratorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("REPORTES DE ESPECTRO ARMONICOS Y FORMAS DE ONDA")
        self.root.geometry("750x600") # Ajustar tamaño

        # Aplicar un tema ttk si está disponible para mejorar la estética
        try:
            style = ttk.Style(self.root)
            # Intentar usar un tema que se vea bien en la mayoría de los sistemas
            available_themes = style.theme_names()
            if "clam" in available_themes:
                style.theme_use("clam")
            elif "alt" in available_themes:
                style.theme_use("alt")
            elif "default" in available_themes: # Windows
                 style.theme_use("default")
            # Podrías añadir más fallbacks o temas específicos para OS
        except tk.TclError:
            print("TTK theming not fully available or error applying theme.")


        self.db_file_path = tk.StringVar()
        self.html_output_path = tk.StringVar()
        self.html_output_path.set(os.path.join(os.getcwd(), "reporte_graficos_plotly.html")) # Default

        self.setup_ui()

    def setup_ui(self):
        global gui_log_text_widget # Para que la función log_message pueda acceder al widget

        main_frame = ttk.Frame(self.root, padding="20") # Más padding general
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1) # Permitir que la columna del frame se expanda

        # --- Título y Subtítulo ---
        ttk.Label(main_frame, text="ESPECTRO ARMONICOS Y FORMA DE ONDA - ETAP",
                  font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        ttk.Label(main_frame, text="Seleccione una base de datos SQLite y genere un reporte HTML con gráficos Plotly.",
                  font=("Arial", 10), foreground="gray").grid(row=1, column=0, columnspan=3, pady=(0, 25), sticky="ew")

        # --- Sección 1: Selección de Base de Datos ---
        ttk.Label(main_frame, text="1. Seleccionar Base de Datos SQLite:",
                  font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))

        db_select_frame = ttk.Frame(main_frame)
        db_select_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        db_select_frame.columnconfigure(1, weight=1) # Para que el entry se expanda

        self.db_entry = ttk.Entry(db_select_frame, textvariable=self.db_file_path, width=60)
        self.db_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0,10))
        ttk.Button(db_select_frame, text="Seleccionar BD...",
                   command=self.select_database_file).grid(row=0, column=0, padx=(0,10))


        # --- Sección 2: Archivo de Salida HTML ---
        ttk.Label(main_frame, text="2. Especificar Archivo de Salida HTML:",
                  font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))

        html_output_frame = ttk.Frame(main_frame)
        html_output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        html_output_frame.columnconfigure(1, weight=1)

        self.html_entry = ttk.Entry(html_output_frame, textvariable=self.html_output_path, width=60)
        self.html_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0,10))
        ttk.Button(html_output_frame, text="Guardar Como...",
                   command=self.select_html_file).grid(row=0, column=0, padx=(0,10))


        # --- Botón de Generación ---
        # Usar un estilo para el botón principal
        s = ttk.Style()
        s.configure('Accent.TButton', font=('Arial', 12, 'bold'), padding=10)
        self.generate_button = ttk.Button(main_frame, text="🚀 GENERAR ESPECTRO ARMONICOS Y FORMAS DE ONDA",
                                          command=self.start_report_generation_thread,
                                          style="Accent.TButton")
        self.generate_button.grid(row=6, column=0, columnspan=3, pady=30, sticky="ew", ipady=5)


        # --- Área de Log ---
        log_frame = ttk.LabelFrame(main_frame, text="Avance del Proceso", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10,0))
        main_frame.rowconfigure(7, weight=1) # Permitir que el frame del log se expanda
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, state=tk.NORMAL,
                                                  font=("Courier New", 9))
        self.log_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        gui_log_text_widget = self.log_area # Asignar para la función log_message

        # --- Etiqueta de Estado (opcional, podría ir en el log) ---
        self.status_label = ttk.Label(main_frame, text="Listo.", font=("Arial", 10), foreground="green")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=(10,0), sticky="ew")


    def select_database_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Base de Datos SQLite",
            filetypes=(("All files", "*.*"), )
        )
        if file_path:
            self.db_file_path.set(file_path)
            self.update_status(f"Base de datos seleccionada: {Path(file_path).name}", "blue")

    def select_html_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Guardar Reporte HTML Como",
            defaultextension=".html",
            initialfile=Path(self.html_output_path.get()).name, # Sugerir nombre actual
            initialdir=Path(self.html_output_path.get()).parent, # Sugerir directorio actual
            filetypes=(("HTML files", "*.html"), ("All files", "*.*"))
        )
        if file_path:
            # Asegurarse de que termine con .html
            if not file_path.lower().endswith(".html"):
                file_path += ".html"
            self.html_output_path.set(file_path)
            self.update_status(f"Archivo de salida HTML: {Path(file_path).name}", "blue")

    def start_report_generation_thread(self):
        db_path = self.db_file_path.get()
        html_path = self.html_output_path.get()

        if not db_path:
            messagebox.showerror("Entrada Faltante", "Por favor, seleccione un archivo de base de datos.")
            return
        if not html_path:
            messagebox.showerror("Entrada Faltante", "Por favor, especifique un archivo HTML de salida.")
            return

        self.generate_button.config(state=tk.DISABLED, text="Generando...")
        self.log_area.delete(1.0, tk.END)
        self.update_status("Iniciando generación del reporte...", "darkorange")
        log_message("Iniciando generación del reporte...") # También al log

        thread = threading.Thread(target=self.run_generation_process, args=(db_path, html_path), daemon=True)
        thread.start()

    def run_generation_process(self, db_path, html_path):
        try:
            generate_html_report_process(db_path, html_path) # Llama a la función de lógica principal
            self.update_status("Proceso de generación finalizado.", "green")
        except Exception as e:
            log_message(f"Error mayor durante la generación: {e}") # Loguear el error
            traceback.print_exc() # Imprimir traceback completo en consola
            if gui_log_text_widget: # Y en la GUI
                gui_log_text_widget.insert(tk.END, f"ERROR MAYOR: {e}\n{traceback.format_exc()}\n")
                gui_log_text_widget.see(tk.END)
            self.update_status(f"Error durante la generación: {e}", "red")
            messagebox.showerror("Error en Proceso", f"Ocurrió un error durante la generación:\n{e}")
        finally:
            if self.generate_button.winfo_exists():
                self.generate_button.config(state=tk.NORMAL, text="🚀 Generar Reporte HTML")


    def update_status(self, message, color="black"):
        if self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground=color)
        # self.root.update_idletasks() # No siempre es necesario si el log ya lo hace

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ReportGeneratorApp()
    app.run()
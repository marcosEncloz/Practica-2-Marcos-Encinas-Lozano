import tkinter as tk
from tkinter import scrolledtext
from IndustryApplication_v1 import SensorReceiver   # Clase para recibir datos MQTT
from SistemaComunicacion import SistemaComunicacion # Clase para enviar/recibir mensajes Meshtastic
from PIL import Image, ImageTk   # Para mostrar gráficas guardadas como imágenes
from tkintermapview import TkinterMapView #mapa de cooredenadas
import tkinter.messagebox as tkmsg

# ------------------------------------------------------------
# Clase principal de la aplicación gráfica
# ------------------------------------------------------------
class SupervivenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana
        self.title("Panel Supervivencia")
        self.geometry("900x600")

        # Guardamos el receptor MQTT para poder iniciar/detenerlo
        self.receiver = None

        # Contenedor principal donde se mostrarán las pantallas
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Diccionario que guarda las pantallas (frames)
        self.frames = {}

        # --------------------------------------------------------
        # Menú superior: cada opción abre una pantalla distinta
        # --------------------------------------------------------
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        menubar.add_command(label="1. Recibir datos MQTT", command=lambda: self.show_frame("MQTT"))
        menubar.add_command(label="2. Enviar mensaje Meshtastic", command=lambda: self.show_frame("Enviar"))
        menubar.add_command(label="3. Recibir mensajes Meshtastic", command=lambda: self.show_frame("Recibir"))
        menubar.add_command(label="4. Guardar y graficar", command=lambda: self.show_frame("Graficas"))

        menubar.add_command(label="5. Mapa", command=lambda: self.show_frame("Mapa"))

        menubar.add_command(label="6. Salir", command=self.quit)



        # --------------------------------------------------------
        # Crear las pantallas (frames) correspondientes a cada opción
        # --------------------------------------------------------
        self.create_mqtt_frame()
        self.create_enviar_frame()
        self.create_recibir_frame()
        self.create_graficas_frame()
        self.create_mapa_frame()


        # Mostrar pantalla inicial (MQTT)
        self.show_frame("MQTT")

    # ------------------------------------------------------------
    # Función para mostrar una pantalla concreta
    # ------------------------------------------------------------
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()


   # ------------------------------------------------------------
    # Función para añadir texto al área de salida
    # ------------------------------------------------------------
    def append_output(self, text):
        self.output_mqtt.configure(state="normal")
        self.output_mqtt.insert("end", text + "\n")
        self.output_mqtt.see("end")
        self.output_mqtt.configure(state="disabled")  







# ------------------------------------------------------------
# Pantalla 1: Recibir datos MQTT
# ------------------------------------------------------------
    def create_mqtt_frame(self):
        frame = tk.Frame(self.container, bg="#59C3E1")
        frame.place(relwidth=1, relheight=1)
        self.frames["MQTT"] = frame

        tk.Label(frame, text="-~o0o~- Recepción de datos MQTT -~o0o~-",
                font=("Times", 18), bg="#CFF9F9").pack(pady=10)

        # Botones de control
        botones = tk.Frame(frame, bg="#59C3E1")
        botones.pack(pady=5)

        tk.Button(botones, text="Recibir datos", command=self.recibir_datos_mqtt,
                bg="#BC861A", font=("Times", 13, "italic")).pack(side="left", padx=10)

        tk.Button(botones, text="Parar recepción", command=self.parar_datos_mqtt,
                bg="#BC861A", font=("Times", 13, "italic")).pack(side="left", padx=10)

        # Cuadro tipo terminal para mostrar mensajes recibidos
        self.output_mqtt = tk.Text(frame, height=40, bg="#000000", fg="#00E8BE", font=("Consolas", 11))
        self.output_mqtt.pack(fill="both", padx=20, pady=10)
        self.output_mqtt.configure(state="disabled")  # Inicialmente desactivado


#                --------------------------- Apariencia ---------------------------


    # ------------------------------------------------------------
    # Callback que llama a append_output desde el hilo principal
    # ------------------------------------------------------------
    def mostrar_mqtt(self, texto):
        self.after(0, self.append_output, texto)

    # ------------------------------------------------------------
    # Método para imprimir texto en el cuadro de la interfaz
    # ------------------------------------------------------------
    def append_output(self, text):
        self.output_mqtt.configure(state="normal")
        self.output_mqtt.insert(tk.END, text + "\n")
        self.output_mqtt.see(tk.END)
        self.output_mqtt.configure(state="disabled")


    # ------------------------------------------------------------
    # Iniciar receptor MQTT con el callback correcto
    # ------------------------------------------------------------
    def recibir_datos_mqtt(self):
        if self.receiver:
            self.parar_datos_mqtt()

        self.receiver = SensorReceiver(
            broker="broker.emqx.io",
            port=1883,
            topics=["sensor/data/sen55", "sensor/data/gas_sensor"],
            callback=self.mostrar_mqtt
        )
        self.receiver.start()

    # ------------------------------------------------------------
    # Detener receptor MQTT
    # ------------------------------------------------------------
    def parar_datos_mqtt(self):
        if self.receiver:
            try:
                self.receiver.stop()  # usa el método de la clase
                self.mostrar_mqtt("Recepción detenida.\n")
            except Exception as e:
                self.mostrar_mqtt(f"Error al detener recepción: {e}")





    # ============================================================
    # Pantalla 2: Enviar mensaje Meshtastic
    # ============================================================
    def create_enviar_frame(self):
        frame = tk.Frame(self.container, bg="#76E159")
        frame.place(relwidth=1, relheight=1)
        self.frames["Enviar"] = frame

        tk.Label(frame, text="-~o0o~- Enviar mensaje Meshtastic -~o0o~-",
                  font=("Times", 18), bg="#CFF9CF").pack(pady=10)

        # Cuadro de entrada para escribir mensaje
        self.message_entry = tk.Entry(frame)
        self.message_entry.insert(0, "Escribe tu mensaje aqui <--(borra el texto )")
        self.message_entry.pack(fill="x", padx=20, pady=5)

        # Botón enviar
        tk.Button(frame, text="Enviar", command=self.enviar_mensaje,
                  bg="#BC861A", font=("Times", 13, "italic")).pack(pady=5)

        # Cuadro grande para mostrar confirmaciones
        self.output_enviar = tk.Text(frame, height=40, bg="#000000", fg="#17E800", font=("Consolas", 11))
        self.output_enviar.pack(fill="both", padx=20, pady=10)


#                --------------------------- Apariencia ---------------------------

    def enviar_mensaje(self):
        mensaje = self.message_entry.get().strip()
        comunicador = SistemaComunicacion()
        try:
            comunicador.enviar_mensaje(mensaje)
            self.output_enviar.configure(state="normal")
            self.output_enviar.insert(tk.END, f"✔ Mensaje enviado: {mensaje}\n")
            self.output_enviar.see(tk.END)
            self.output_enviar.configure(state="disabled")
        except Exception as e:
            self.output_enviar.configure(state="normal")
            self.output_enviar.insert(tk.END, f"✘ Error al enviar mensaje: {e}\n")
            self.output_enviar.see(tk.END)
            self.output_enviar.configure(state="disabled")







    # ============================================================
    # Pantalla 3: Recibir mensajes Meshtastic
    # ============================================================
    def create_recibir_frame(self):
        frame = tk.Frame(self.container, bg="#E15959")
        frame.place(relwidth=1, relheight=1)
        self.frames["Recibir"] = frame

        tk.Label(frame, text="-~o0o~- Recibir mensajes Meshtastic -~o0o~-",
                  font=("Times", 18), bg="#F9CFCF").pack(pady=10)

        # Botón para iniciar recepción
        tk.Button(frame, text="Comenzar recepcion", command=self.recibir_mensajes,
                  bg="#BC861A", font=("Times", 13, "italic")).pack(pady=5)
        #boton para parar la recepcion
        tk.Button(frame, text="Parar recepcion", command=self.parar_recepcion_meshtastic,
                  bg="#BC861A", font=("Times", 13, "italic")).pack(side="left", padx=10)

        # Cuadro grande para mostrar mensajes recibidos
        self.output_recibir = tk.Text(frame, height=40, bg="#000000", fg="#E80000", font=("Consolas", 11))
        self.output_recibir.pack(fill="both", padx=20, pady=10)


#                --------------------------- Apariencia ---------------------------


    def procesar_mensaje(self, texto):
        # Mostrar siempre en pantalla 3
        self.mostrar_meshtastic(texto)
        # Intentar también mostrar en mapa si el texto parece coordenadas
        self.mostrar_coords_en_mapa(texto)


    def recibir_mensajes(self):
        self.output_recibir.insert(tk.END, "Escuchando mensajes Meshtastic...\n")
        self.comunicador = SistemaComunicacion(callback=self.procesar_mensaje)

        import threading
        threading.Thread(target=self.comunicador.recibir_mensajes, daemon=True).start()



# ------------------------------------------------------------
# imprime mensajes para pantalla 3 
# ------------------------------------------------------------
    def mostrar_meshtastic(self, texto):
        def _print():
            self.output_recibir.insert("end", texto + "\n")
            self.output_recibir.see("end")
        self.after(0, _print)

    def parar_recepcion_meshtastic(self):
        if hasattr(self, "comunicador") and self.comunicador:
            self.comunicador.stop()
            self.output_recibir.insert(tk.END, "Recepción Meshtastic detenida.\n")




    # ============================================================
    # Pantalla 4: Guardar y graficar
    # ============================================================
    def create_graficas_frame(self):
        frame = tk.Frame(self.container, bg="#E159D3")
        frame.place(relwidth=1, relheight=1)
        self.frames["Graficas"] = frame

        tk.Label(frame, text="-~o0o~- Guardar datos y generar gráficas -~o0o~-",
                font=("Times", 18), bg="#F5CFF9").pack(pady=10)

        tk.Button(frame, text="Guardar y graficar", command=self.guardar_y_graficar,
                bg="#BC861A", font=("Times", 13, "italic")).pack(pady=5)

        self.output_graficas = tk.Text(frame, height=5, bg="#000000", fg="#E800E0", font=("Consolas", 11))
        self.output_graficas.pack(fill="x", padx=20, pady=10)

        # Scroll horizontal + canvas para imágenes
        canvas_frame = tk.Frame(frame)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.graph_scroll = tk.Scrollbar(canvas_frame, orient="horizontal")
        self.graph_scroll.pack(side="bottom", fill="x")

        self.graph_canvas = tk.Canvas(canvas_frame, bg="#FFFFFF", xscrollcommand=self.graph_scroll.set)
        self.graph_canvas.pack(side="left", fill="both", expand=True)

        self.graph_scroll.config(command=self.graph_canvas.xview)

        # Frame interno donde se colocan las imágenes
        self.graph_inner = tk.Frame(self.graph_canvas, bg="#FFFFFF")
        self.graph_canvas.create_window((0, 0), window=self.graph_inner, anchor="nw")

        # Actualizar scroll cuando se añadan imágenes
        self.graph_inner.bind("<Configure>", lambda e:
                               self.graph_canvas.configure(scrollregion=self.graph_canvas.bbox("all")))


#                --------------------------- Apariencia ---------------------------


    def guardar_y_graficar(self):
        if self.receiver:
            self.receiver.guardar_todo()
        self.output_graficas.insert(tk.END, "Datos guardados y gráficas generadas.\n")

        #imprimir todas las imagenes
        rutas = [
            "resultados/grafica_GM102B.png",
            "resultados/grafica_GM302B.png",
            "resultados/grafica_GM502B.png",
            "resultados/grafica_GM702B.png",
            "resultados/grafica_humedad.png",
            "resultados/grafica_pm25.png",
            "resultados/grafica_temperatura.png"
        ]

        self.graph_imgs = []

        # Limpiar canvas antes de añadir nuevas imágenes
        for widget in self.graph_inner.winfo_children():
            widget.destroy()

        for ruta in rutas:
            try:
                img = Image.open(ruta).resize((600, 500))
                photo = ImageTk.PhotoImage(img)
                self.graph_imgs.append(photo)
                tk.Label(self.graph_inner, image=photo, bg="#FFFFFF").pack(side="left", padx=10, pady=10)
            except Exception:
                self.output_graficas.insert(tk.END, f"No se encontró la gráfica {ruta}\n")





    # ============================================================
    # Pantalla 5: Mapa coordenadas
    # ============================================================


    def create_mapa_frame(self):
        frame = tk.Frame(self.container, bg="#E0E24F")
        frame.place(relwidth=1, relheight=1)
        self.frames["Mapa"] = frame

        tk.Label(frame, text="-~o0o~- Mapa y coordenadas -~o0o~-",
                font=("Times", 18), bg="#F0F9CF").pack(pady=10)

        # Contenedor para el mapa
        map_container = tk.Frame(frame, bg="#B7B34B")
        map_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Crea el widget del mapa
        self.map_view = TkinterMapView(map_container, width=800, height=450, corner_radius=0)
        self.map_view.pack(fill="both", expand=True)

        # Fuente del mapa (OpenStreetMap por defecto)
        self.map_view.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)

        # Posición inicial (Burgos aprox.)
        self.map_view.set_position(42.3439, -3.6969)
        self.map_view.set_zoom(12)

        # Campo y botones para probar coordenadas
        controls = tk.Frame(frame, bg="#B7B34B")
        controls.pack(fill="x", padx=20, pady=10)

        tk.Label(controls, text="Lat:", bg="#A5B74B", fg="#FFFFFF").pack(side="left")
        self.lat_entry = tk.Entry(controls, width=12)
        self.lat_entry.insert(0, "42.3439")
        self.lat_entry.pack(side="left", padx=5)

        tk.Label(controls, text="Lon:", bg="#B5B74B", fg="#FFFFFF").pack(side="left")
        self.lon_entry = tk.Entry(controls, width=12)
        self.lon_entry.insert(0, "-3.6969")
        self.lon_entry.pack(side="left", padx=5)

        tk.Button(controls, text="Centrar", command=self.centrar_mapa,
                bg="#BC861A", font=("Times", 12, "italic")).pack(side="left", padx=10)

        tk.Button(controls, text="Añadir marcador", command=self.anadir_marcador_manual,
                bg="#BC861A", font=("Times", 12, "italic")).pack(side="left", padx=10)

        # Mantener referencia de marcadores para actualizarlos
        self.marcadores = []

#                --------------------------- Apariencia ---------------------------

    def centrar_mapa(self):
        try:
            lat = float(self.lat_entry.get().strip())
            lon = float(self.lon_entry.get().strip())
        except ValueError:
            # Feedback rápido en pantalla (puedes usar un Text si prefieres)
            tk.messagebox.showerror("Coordenadas inválidas", "Lat/Lon deben ser números.")
            return
        self.map_view.set_position(lat, lon)

    def anadir_marcador_manual(self):
        try:
            lat = float(self.lat_entry.get().strip())
            lon = float(self.lon_entry.get().strip())
        except ValueError:
            tk.messagebox.showerror("Coordenadas inválidas", "Lat/Lon deben ser números.")
            return
        marker = self.map_view.set_marker(lat, lon, text=f"{lat:.5f}, {lon:.5f}")
        self.marcadores.append(marker)

    def actualizar_marcador(self, lat, lon, etiqueta="Nodo"):
        # Borra último marcador y añade uno nuevo, manteniendo solo el más reciente
        for m in self.marcadores:
            try:
                m.delete()
            except Exception:
                pass
        self.marcadores.clear()
        marker = self.map_view.set_marker(lat, lon, text=etiqueta)
        self.marcadores.append(marker)
        self.map_view.set_position(lat, lon)

    def mostrar_coords_en_mapa(self, texto):
    # Espera texto como "lat,lon" o "lat=<>, lon=<>" y actualiza el mapa
        def _update():
            try:
                # Intento 1: formato "lat,lon"
                if "," in texto:
                    lat_s, lon_s = texto.split(",", 1)
                    lat = float(lat_s.strip())
                    lon = float(lon_s.strip())
                else:
                    # Intento 2: formato "lat=.. lon=.."
                    parts = texto.replace(",", " ").split()
                    nums = [p.split("=")[1] for p in parts if "=" in p]
                    lat = float(nums[0]); lon = float(nums[1])
                self.actualizar_marcador(lat, lon, etiqueta="Posición recibida")
            except Exception:
                # Si no son coords, ignorar
                pass
        self.after(0, _update)




# ============================================================
# Ejecución principal
# ============================================================
if __name__ == "__main__":
    app = SupervivenciaApp()
    app.mainloop()

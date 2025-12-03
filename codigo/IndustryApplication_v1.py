import json
import os
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import csv

###########################################
class SensorReceiver:
    def __init__(self, broker, port, topics, callback=None):
        self.broker = broker
        self.port = port
        self.topics = topics
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.data_log = []
        self.callback = callback

#################################################

    # Configuración del cliente MQTT
    BROKER = "broker.emqx.io"  # Cambia esto por tu broker MQTT
    PORT = 1883  # Puerto del broker MQTT
    TOPICS = ["sensor/data/sen55", "sensor/data/gas_sensor"]  # Temas a los que se suscribirá el cliente       

###################################################

    def crear_carpeta_resultados(self):
        if not os.path.exists("resultados"):
            os.makedirs("resultados")



#==============================================================================================================   
# para interfaz  
#==============================================================================================================        
   # Callback cuando se establece la conexión con el broker
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._emit("Conexión exitosa al broker MQTT")
            for topic in self.topics:
                client.subscribe(topic)
                self._emit(f"Suscrito al tema '{topic}'")
        else:
            self._emit(f"Error de conexión, código: {rc}")
   
   
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            self.data_log.append(payload)
            self._emit(f"Mensaje recibido en {msg.topic}:\n{json.dumps(payload, indent=4)}")
        except Exception as e:
            self._emit(f"Error procesando mensaje: {e}")



    # ------------------------------------------------------------
    # Guardar todo y graficar (se llama desde la interfaz)
    # ------------------------------------------------------------
    def guardar_todo(self, sobrescribir=False):
        self.save_to_json(sobrescribir=True)  # forzar sobrescritura
        self.save_to_csv()
        self.graficar_desde_archivo()

            
#==============================================================================================================  
# para interfaz      
#==============================================================================================================        
#===========================================================================================================================
# interfaz
#===========================================================================================================================
    def _emit(self, texto):
        print(texto)  # terminal
        if self.callback:
            self.callback(texto)  # interfaz


    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self._emit("Esperando mensajes...")
        self.client.loop_start()   # no bloquea, corre en segundo plano


    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        self._emit("Recepción detenida.")

#===========================================================================================================================
#===========================================================================================================================
# Callback cuando se recibe un mensaje en los temas suscritos

#    def on_message(self, client, userdata, msg):
#        print(f"Mensaje recibido en el tema '{msg.topic}':")
#        print(msg.payload.decode("utf-8"))

#        try:
            # Decodificar y convertir el mensaje de JSON a diccionario
#            payload = json.loads(msg.payload.decode("utf-8"))
#            print(json.dumps(payload, indent=4))  # Mostrar el mensaje formateado
#            self.data_log.append(payload)
#        except json.JSONDecodeError as e:
#            print(f"Error decodificando JSON: {e}")


    # ------------------------------------------------------------
    # Guardar datos en JSON (sobrescribe siempre)
    # ------------------------------------------------------------
    def save_to_json(self, ruta="resultados/datos_sensores.json", sobrescribir=False):
        self.crear_carpeta_resultados()
        if not self.data_log:
            print("No hay datos nuevos en memoria. Se usaran los datos guardados para generar graficas.")
            return

        datos_previos = []
        if not sobrescribir and os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                try:
                    datos_previos = json.load(f)
                except json.JSONDecodeError:
                    datos_previos = []

        datos_combinados = datos_previos + self.data_log
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos_combinados, f, indent=4)
        print(f"Datos guardados en {ruta}")

    # ------------------------------------------------------------
    # Cargar datos previos de JSON (por si quieres graficar sin datos en memoria)
    # ------------------------------------------------------------
    def _cargar_json_existente(self, ruta):
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []




    # ------------------------------------------------------------
    # Guardar datos en CSV (sobrescribe siempre)
    # ------------------------------------------------------------
    def save_to_csv(self, filename="resultados/datos_sensores.csv"):
        self.crear_carpeta_resultados()
        if not self.data_log:
            print("No hay datos en memoria para guardar en CSV.")
            return

        ordered_keys = [
            "MassConcentrationPm1p0", "MassConcentrationPm2p5",
            "MassConcentrationPm4p0", "MassConcentrationPm10p0",
            "AmbientTemperature", "AmbientHumidity",
            "VocIndex", "NoxIndex",
            "GM102B", "GM302B", "GM502B", "GM702B"   #  añadir gases
        ]

        with open(filename, "w", encoding="utf-8") as f:  # sobrescribir siempre
            for d in self.data_log:
                fila = {k: d.get(k, "") for k in ordered_keys}
                linea = " | ".join([f"{k}: {fila[k]}" for k in ordered_keys])
                f.write(linea + "\n")
        print(f"Datos guardados en {filename}")


    def guardar_todo(self):
        self.save_to_json(sobrescribir=True)  # forzar sobrescritura SIEMPRE
        self.save_to_csv()
        self.graficar_desde_archivo()






    def graficar_temperatura(self, ruta="resultados/grafica_temperatura.png"):
        temperaturas = [d["AmbientTemperature"] for d in self.data_log if "AmbientTemperature" in d]
        plt.plot(temperaturas, color ="yellow")
        plt.title("Evolución de la temperatura")
        plt.xlabel("Muestras")
        plt.ylabel("Temperatura (°C)")
        plt.grid(True)
        plt.savefig(ruta)
        plt.close()

    def graficar_humedad(self, ruta="resultados/grafica_humedad.png"):
        humedad = [d["AmbientHumidity"] for d in self.data_log if "AmbientHumidity" in d]
        plt.plot(humedad, color="blue")
        plt.title("Evolución de la humedad")
        plt.xlabel("Muestras")
        plt.ylabel("Humedad (%)")
        plt.grid(True)
        plt.savefig(ruta)
        plt.close()

    def graficar_pm25(self, ruta="resultados/grafica_pm25.png"):
        pm25 = [d["MassConcentrationPm2p5"] for d in self.data_log if "MassConcentrationPm2p5" in d]
        plt.plot(pm25, color="green")
        plt.title("Concentración de PM2.5")
        plt.xlabel("Muestras")
        plt.ylabel("µg/m³")
        plt.grid(True)
        plt.savefig(ruta)
        plt.close()

    def graficar_gas(self, gas_name=None, ruta=None):
        gases_detectados = set()
        for d in self.data_log:
            gases_detectados.update(k for k in d.keys() if k.startswith("GM"))

        for gas in gases_detectados:
            gas_values = [d[gas] for d in self.data_log if gas in d]
            plt.plot(gas_values, label=gas)
            plt.title(f"Evolución de {gas}")
            plt.xlabel("Muestras")
            plt.ylabel("Intensidad")
            plt.grid(True)
            plt.legend()
            ruta_final = ruta or f"resultados/grafica_{gas}.png"
            plt.savefig(ruta_final)
            plt.close()



    def graficar_desde_archivo(self, ruta_json="resultados/datos_sensores.json"):
        if not os.path.exists(ruta_json):
            print("No hay datos guardados para graficar.")
            return

        with open(ruta_json, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                print("Error al leer el archivo JSON.")
                return

        if not datos:
            if not datos:
                print("El archivo JSON esta vacio. No se generaran graficas.")
                return


        # Graficar temperatura
        temperaturas = [d["AmbientTemperature"] for d in datos if "AmbientTemperature" in d]
        if temperaturas:
            plt.plot(temperaturas , color="red")
            plt.title("Evolución de la temperatura")
            plt.xlabel("Muestras")
            plt.ylabel("Temperatura (°C)")
            plt.grid(True)
            plt.savefig("resultados/grafica_temperatura.png")
            plt.close()

        # Graficar humedad
        humedad = [d["AmbientHumidity"] for d in datos if "AmbientHumidity" in d]
        if humedad:
            plt.plot(humedad, color="pink")
            plt.title("Evolución de la humedad")
            plt.xlabel("Muestras")
            plt.ylabel("Humedad (%)")
            plt.grid(True)
            plt.savefig("resultados/grafica_humedad.png")
            plt.close()

        # Graficar PM2.5
        pm25 = [d["MassConcentrationPm2p5"] for d in datos if "MassConcentrationPm2p5" in d]
        if pm25:
            plt.plot(pm25, color="orange")
            plt.title("Concentración de PM2.5")
            plt.xlabel("Muestras")
            plt.ylabel("µg/m³")
            plt.grid(True)
            plt.savefig("resultados/grafica_pm25.png")
            plt.close()

        # Graficar gases detectados
        gases_detectados = set()
        for d in datos:
            gases_detectados.update(k for k in d.keys() if k.startswith("GM"))

        for gas in gases_detectados:
            gas_values = [d[gas] for d in datos if gas in d]
            if gas_values:
                plt.plot(gas_values, label=gas)
                plt.title(f"Evolución de {gas}")
                plt.xlabel("Muestras")
                plt.ylabel("Intensidad")
                plt.grid(True)
                plt.legend()
                plt.savefig(f"resultados/grafica_{gas}.png")
                plt.close()


#    def save_to_json(self, sobrescribir=False):
#        modo = "w" if sobrescribir else "a"
#        with open("resultados/datos_sensores.json", modo) as f:
#            json.dump(self.data_log, f, indent=4)
        #  vaciar el buffer para que no se acumulen datos entre sesiones
#        self.data_log = []


if __name__ == "__main__":
    receiver = SensorReceiver(
        broker="broker.emqx.io",
        port=1883,
        topics=["sensor/data/sen55", "sensor/data/gas_sensor"]
    )
    try:
        receiver.start()
    except KeyboardInterrupt:
        receiver.guardar_todo()
        print("Datos guardados y gráficas generadas en la carpeta 'resultados/'.")


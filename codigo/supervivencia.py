import os
from IndustryApplication_v1 import SensorReceiver
from SistemaComunicacion import SistemaComunicacion

os.makedirs("resultados", exist_ok=True)

def mostrar_menu():
    print('''   --- MENÚ PRINCIPAL ---
    1. Recibir datos por MQTT
    2. Enviar mensaje por Meshtastic
    3. Recibir mensajes por Meshtastic
    4. Guardar datos y generar gráficas
    5. Salir''')

def main():
    receiver = None  # mantener referencia

    while True:
        mostrar_menu()
        try:
            opcion = input("Selecciona una opción (1-5): ")
        except KeyboardInterrupt:
            print("\nInterrupción detectada. Saliendo del programa...")
            if receiver:
                receiver.guardar_todo()
            break

#-------------------------------------------------------------------------------------------------------------------

        if opcion == "1":
            if not receiver:
                receiver = SensorReceiver(
                    broker="broker.emqx.io",
                    port=1883,
                    topics=["sensor/data/sen55", "sensor/data/gas_sensor"]
                )
                receiver.start()
                print("Receptor MQTT iniciado.")
            else:
                print("Ya hay un receptor activo.")

#-------------------------------------------------------------------------------------------------------------------

        elif opcion == "2":
            mensaje = input("Escribe el mensaje a enviar: ")
            comunicador = SistemaComunicacion()
            comunicador.enviar_mensaje(mensaje)

#-------------------------------------------------------------------------------------------------------------------

        elif opcion == "3":
            comunicador = SistemaComunicacion()
            comunicador.recibir_mensajes()

#-------------------------------------------------------------------------------------------------------------------

        elif opcion == "4":
            if receiver:
                receiver.guardar_todo()
                print("Datos guardados y gráficas generadas en la carpeta 'resultados/'.")
            else:
                print("No hay receptor activo para guardar datos.")

#-------------------------------------------------------------------------------------------------------------------

        elif opcion == "5":
            print("Saliendo del programa...")
            if receiver:
                receiver.guardar_todo()
            break

#-------------------------------------------------------------------------------------------------------------------

        else:
            print("Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    main()

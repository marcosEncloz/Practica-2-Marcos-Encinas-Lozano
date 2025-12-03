import argparse
from IndustryApplication_v1 import SensorReceiver
from SistemaComunicacion import SistemaComunicacion 

class InterfazTerminal:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Aplicación de comunicación industrial")
        self.parser.add_argument("--modo", choices=["mqtt", "meshtastic"], required=True, help="Modo de operación")
        self.parser.add_argument("--accion", choices=["recibir", "enviar"], required=True, help="Acción a realizar")
        self.parser.add_argument("--mensaje", type=str, help="Mensaje a enviar (solo en modo enviar)")

    def ejecutar(self):
        args = self.parser.parse_args()

        if args.modo == "mqtt":
            receiver = SensorReceiver(
                broker="broker.emqx.io",
                port=1883,
                topics=["sensor/data/sen55", "sensor/data/gas_sensor"]
            )
            if args.accion == "recibir":
                receiver.start()
            else:
                print("Modo MQTT no admite envío de mensajes")

        elif args.modo == "meshtastic":
            comunicador = SistemaComunicacion()
            if args.accion == "enviar" and args.mensaje:
                comunicador.enviar_mensaje(args.mensaje)
            elif args.accion == "recibir":
                comunicador.recibir_mensajes()
            else:
                print("Falta el mensaje para enviar")



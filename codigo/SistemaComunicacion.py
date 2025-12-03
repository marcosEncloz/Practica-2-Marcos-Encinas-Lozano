import time
import random
import base64
import re
import paho.mqtt.client as mqtt
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2
from meshtastic import BROADCAST_NUM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
      
        
class SistemaComunicacion:
    def __init__(self, callback=None):
        # Configuración MQTT / Meshtastic
        self.mqtt_broker = "mqtt.meshtastic.org"
        self.mqtt_port = 1883
        self.mqtt_username = "meshdev"
        self.mqtt_password = "large4cats"
        self.root_topic = "msh/EU_868/ES/2/e/"
        self.channel = "TestMQTT"
        self.key = "ymACgCy9Tdb8jHbLxUxZ/4ADX+BWLOGVihmKHcHTVyo="

        # Opcional: activar debugging local para prints de diagnóstico
        self.debug = False

        self.callback = callback
        self.mqtt_broker = "mqtt.meshtastic.org"
        self._running = False

        # Nodo fijo asignado por ti (no regenerar)
        self.node_name = '!abcd65e8'
        # derivar node_number de forma segura y limitar a 32 bits
        hexpart = re.sub(r'[^0-9a-fA-F]', '', self.node_name.lstrip('!'))
        hexpart = hexpart[-8:] if hexpart else "0"
        self.node_number = int(hexpart, 16) & 0xFFFFFFFF

        # id global acotado a 32 bits
        self.global_message_id = random.getrandbits(32) & 0xFFFFFFFF

        # Topics (se rellenan en set_topic)
        self.subscribe_topic = ""
        self.publish_topic = ""

        # Cliente MQTT (se crea en _ensure_client / connect_mqtt)
        self.client = None
        self._auto_subscribe = False





    # Helpers
    def set_topic(self):
        # No sobrescribir node_name fijo
        self.subscribe_topic = self.root_topic + self.channel + "/#"
        self.publish_topic = self.root_topic + self.channel + "/" + self.node_name
        if self.debug: print("set_topic:", self.subscribe_topic, self.publish_topic)

    def _b64decode_safe(self, s):
        s = s.strip()
        s += "=" * ((4 - len(s) % 4) % 4)
        return base64.b64decode(s.encode('ascii'))

    def xor_hash(self, data):
        result = 0
        for char in data:
            result ^= char
        return result

    def generate_hash(self, name, key):
        # Use safe base64 decode for key handling
        replaced_key = key.replace('-', '+').replace('_', '/')
        try:
            key_bytes = self._b64decode_safe(replaced_key)
        except Exception:
            # fallback: try plain b64decode (original behavior)
            key_bytes = base64.b64decode(replaced_key.encode('utf-8'))
        h_name = self.xor_hash(bytes(name, 'utf-8'))
        h_key = self.xor_hash(key_bytes)
        return h_name ^ h_key

    # MQTT client creation / reuse
    def _ensure_client(self):
        if self.client is None:
            # Use same signature as mqtt-client de la clase para compatibilidad
            try:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="", clean_session=True, userdata=None)
            except Exception:
                # Fallback a constructor simple si la versión no está disponible
                self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            # on_disconnect definido más abajo; si existe, asignarlo
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            if self.debug: print("Cliente MQTT creado")

    # MQTT callbacks (compatibles con distintos bindings)
    def on_connect(self, client, userdata, *args):
        # Tolerar firmas v3/v5: buscar código de resultado en args
        print("DEBUG on_connect: auto_subscribe =", getattr(self, "_auto_subscribe", None))

        rc = 0
        if len(args) >= 1:
            try:
                rc = int(args[0])
            except Exception:
                rc = 0
        if self.debug: print("on_connect rc:", rc)
        # asegurar topics y suscripción si se solicitó
        self.set_topic()
        if rc == 0:
            print("Conectado al broker Meshtastic")
            if getattr(self, "_auto_subscribe", False):
                try:
                    client.subscribe(self.subscribe_topic)
                    print(f"Suscrito al tema: {self.subscribe_topic}")
                except Exception as e:
                    if self.debug: print("Error suscribiendo:", e)
        else:
            if self.debug: print("Conexión fallida, rc:", rc)




    def on_disconnect(self, client, userdata, reason_code, properties=None, flags=None):
        print("Desconectado del broker")



    def on_message(self, client, userdata, msg):
        se = mqtt_pb2.ServiceEnvelope()
        try:
            se.ParseFromString(msg.payload)
            mp = se.packet
        except Exception:
            return

            # Ignorar otros tipos (position, nodeinfo, etc.)

        if mp.HasField("decoded"):
            port = mp.decoded.portnum
            if port == portnums_pb2.TEXT_MESSAGE_APP:
                try:
                    text = mp.decoded.payload.decode("utf-8", errors="ignore").strip()
                    if text:
                        # Si existe el callback (la interfaz), enviamos el texto ahí
                        if self.callback:
                            self.callback(f"Mensaje recibido: {text}")
                        else:
                            print(f"Mensaje recibido: {text}")
                except Exception:
                    pass







    # desencriptado
    def decode_encrypted(self, mp):
        try:
            key_bytes = self._b64decode_safe(self.key)
            nonce_packet_id = getattr(mp, "id").to_bytes(8, "little")
            nonce_from_node = getattr(mp, "from").to_bytes(8, "little")
            nonce = nonce_packet_id + nonce_from_node
            cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
            decryptor = cipher.decryptor()
            encrypted_bytes = getattr(mp, "encrypted")
            decrypted_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()
            data = mesh_pb2.Data()
            data.ParseFromString(decrypted_bytes)
            mp.decoded.CopyFrom(data)
        except Exception:
            return

    def encrypt_message(self, mesh_packet, encoded_message):
        padded_key_bytes = self._b64decode_safe(self.key)
        nonce_packet_id = mesh_packet.id.to_bytes(8, "little")
        nonce_from_node = self.node_number.to_bytes(8, "little")
        nonce = nonce_packet_id + nonce_from_node
        cipher = Cipher(algorithms.AES(padded_key_bytes), modes.CTR(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_bytes = encryptor.update(encoded_message.SerializeToString()) + encryptor.finalize()
        return encrypted_bytes

    # Conexión MQTT controlada y consistente
    def connect_mqtt(self, subscribe=False, timeout=5.0):
        self._ensure_client()
        self._auto_subscribe = bool(subscribe)
        # asegurar topics antes de conectar
        self.set_topic()
        # credenciales antes de conectar
        try:
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        except Exception:
            pass
        # conectar y arrancar loop
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        except Exception as e:
            print("ERROR: fallo al conectar al broker:", e)
            return False
        self.client.loop_start()
        # esperar a que la conexión suba
        start = time.time()
        while time.time() - start < timeout:
            try:
                if self.client.is_connected():
                    return True
            except Exception:
                pass
            time.sleep(0.1)
        if self.debug: print("ERROR: no conectado tras timeout")
        return False

    # Enviar mensaje compacto y sin permanecer escuchando
    def enviar_mensaje(self, mensaje):
        # asegurar topics y conectar mínimo
        self.set_topic()
        ok = self.connect_mqtt(subscribe=False, timeout=5.0)
        if not ok:
            print("No se pudo conectar para enviar el mensaje.")
            return

        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.TEXT_MESSAGE_APP
        encoded_message.payload = mensaje.encode("utf-8")

        mesh_packet = mesh_pb2.MeshPacket()
        mesh_packet.id = int(self.global_message_id & 0xFFFFFFFF)
        self.global_message_id = (self.global_message_id + 1) & 0xFFFFFFFF

        setattr(mesh_packet, "from", int(self.node_number & 0xFFFFFFFF))
        mesh_packet.to = BROADCAST_NUM
        mesh_packet.want_ack = False
        mesh_packet.channel = self.generate_hash(self.channel, self.key)
        mesh_packet.hop_limit = 3

        if self.key:
            mesh_packet.encrypted = self.encrypt_message(mesh_packet, encoded_message)
        else:
            mesh_packet.decoded.CopyFrom(encoded_message)

        service_envelope = mqtt_pb2.ServiceEnvelope()
        service_envelope.packet.CopyFrom(mesh_packet)
        service_envelope.channel_id = self.channel
        service_envelope.gateway_id = self.node_name

        payload = service_envelope.SerializeToString()

        # comprobación de seguridad antes de publicar
        if not self.publish_topic:
            self.set_topic()
        try:
            # debug info temporal
            if self.debug:
                print("DEBUG send:", self.node_name, hex(self.node_number), "msg_id:", mesh_packet.id, "topic:", self.publish_topic)
            self.client.publish(self.publish_topic, payload)
            print(f"Mensaje enviado: {mensaje}")
        except Exception as e:
            print("ERROR publicando mensaje:", e)

        # desconectar loop pero conservar la instancia del cliente para reutilizarla
        time.sleep(0.2)
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass
        # conservar self.client para evitar recreaciones incompletas

    # Modo receptor: se suscribe y muestra solo textos
    def recibir_mensajes(self):
        self.set_topic()
        if self.debug: 
            print("DEBUG: recibir_mensajes - client antes:", self.client)
        ok = self.connect_mqtt(subscribe=True, timeout=6.0)
        if not ok:
            print("No se pudo conectar para recibir mensajes.")
            return

        print("Escuchando mensajes Meshtastic... Presiona Ctrl+C para salir.")
        self._running = True
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Deteniendo escucha...")
        finally:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            # conservar self.client para reutilizar la instancia 
            
    def stop(self):
        # Simula Ctrl+C: rompe el bucle
        self._running = False
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
# Practica-2-Marcos-Encinas-Lozano


_____________
+ Objetivos del sistema:
_____________

Enviar y recibir mensajes entre nodos Meshtastic.

Recibir datos de sensores (temperatura, humedad, gases) vía MQTT.

Almacenar mensajes, posiciones GPS y datos en formato JSON y CSV.

Visualizar gráficas de evolución ambiental.

Automatizar la organización de resultados para entrega profesional.

Incorporar conceptos avanzados de POO: clases abstractas, herencia múltiple, programación defensiva, decoradores y excepciones personalizadas.

Añadir un extra opcional: interfaz gráfica con visualización de coordenadas en un mapa.

+Implementar los anterioires puntos en una interfaz que sea perfectamente funcional.

_____________
+ Estructura del proyecto:
_____________

Código

├── supervivencia.py ------------> # Menú principal del sistema  

├── SistemaComunicacion.py -------> # Comunicación Meshtastic (envío y recepción, herencia múltiple, decoradores)  

├── IndustryApplication_v1.py ----> # Recepción de datos de sensores vía MQTT (adaptado a interfaz gráfica)  

├── interfazterminal.py ----------> # Interfaz CLI para modo y acción  

├── mqtt-client.py ---------------> # Herramienta de diagnóstico y verificación de mensajes  

├── interfaz_tuf_prueba.py --------> # Interfaz gráfica con pantallas y mapa (extra opcional)  

_____________
+ Ejecución:
_____________

Desde VS code:  
Ejecutar `interfaz_tuf_prueba.py` y aparecerá una nueva ventana en la cual se puede seleccionar la acción que quiere llevar a cabo:

funciones que se pueden llevara  cabo
Pantalla 1. Recibir datos por MQTT  
Pantalla 2. Enviar mensaje por Meshtastic  
Pantalla 3. Recibir mensajes por Meshtastic  
Pantalla 4. Graficar datos de sensores  
Pantalla 5. Visualizar mapa con coordenadas  
         6. Salir  

_____________
+ Ejemplos de uso:
_____________

Opción 1: Recibe datos de sensores y guarda en `resultados/datos_sensores.json` y `.csv`.  

Opción 2: Envía un mensaje a todos los nodos Meshtastic conectados.  

Opción 3: Escucha mensajes entrantes en el canal Meshtastic.  

Opción 4: Genera gráficas de evolución ambiental a partir de los datos recibidos.  

Opción 5: Muestra un mapa interactivo con coordenadas recibidas en tiempo real.  

Opción 6: Finaliza el programa.  

_____________
+ Resultados generados:
_____________

`datos_sensores.json`: historial de datos ambientales.  

`grafica_temperatura.png`, `grafica_humedad.png`, etc.: visualización de evolución ambiental.  

Mensajes y posiciones GPS recibidas se almacenan en JSON y se muestran en el mapa.  

_____________
+ Diseño y documentación:
_____________

Consulta el informe PDF adjunto para:  
-Introducción. 
-Objetivos.
-Metodología/Desarrollo (con imagenes).
-Conclusiones.  
-Incidencias. 
-Anexos.   

------------------------------
Marcos Encinas Lozano  
Universidad de Burgos  
Programación orientada a objetos  
3/12/2025

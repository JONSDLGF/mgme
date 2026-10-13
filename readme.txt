roadmap:
    crear un passer para los modelos

bootstrap.py
| - serverx.py
|   | - vm engine * expone la api -api> rendere.json
|   | - rendere client * lee el rendere.json -> dibuja lo que hay dentro de ello

render.json:
{
 "CAP": [[0,0,[...],0]] ; [actibate, enumtype, [types], *cam]; types [enumtype, **] 2D 0 = text, 1 = texture 3D 0 = idmodeltype
 "MOD": {} ; modelos 3D
 "IMG": {} ; imagenes
 "CAM": [ [[0,0,0], [1.4,6,3]] ] ; [pos, tortex/cos-sin]
}



# FGEngine — Arquitectura

> Borrador inicial basado en la arquitectura descrita. Algunos detalles quedan pendientes de definir.

## Objetivo

Separar la lógica y los scripts de la representación visual. **FGEngine** ejecuta la lógica; el **renderer SDL2** dibuja y recoge la interacción del usuario. **ServisX** inicia y coordina los servicios, mientras que **Snet** gestiona la mensajería con el exterior.

Esta separación permite cambiar el renderer, añadir servicios o conectar otros clientes sin tener que meter toda la lógica en la aplicación gráfica.

## Componentes

### ServisX

Supervisor y coordinador del sistema. Sus responsabilidades son:

- Inicializar los servicios en el orden adecuado.
- Coordinar y enrutar mensajes entre ellos.
- Supervisar errores y estados de los servicios.
- Gestionar el apagado ordenado.
- Recibir la solicitud de cierre del renderer mediante `render_user_shutdown`.

El renderer puede solicitar el apagado, pero ServisX es quien lo coordina y lo completa.

### FGEngine

Motor de lógica y ejecución. Sus responsabilidades pueden incluir:

- Ejecutar scripts.
- Mantener o actualizar el estado de la aplicación o del juego.
- Procesar acciones recibidas desde el renderer u otros servicios.
- Ofrecer una interfaz para que plugins amplíen sus capacidades.

FGEngine no debería depender de SDL2 ni de detalles gráficos.

### Renderer SDL2

Aplicación de presentación. Sus responsabilidades son:

- Dibujar el estado que recibe de FGEngine.
- Capturar eventos de teclado, ratón u otros dispositivos.
- Enviar esas acciones al motor mediante mensajes.
- Solicitar el apagado cuando el usuario cierre la aplicación.

El renderer no debería ejecutar scripts ni ser responsable de la lógica principal.

### Snet

Servicio de mensajería con el exterior. Gestiona el intercambio de mensajes entre FGEngine y clientes o sistemas externos. El transporte podría ser TCP u otra opción, según si la comunicación ocurre en la misma máquina, una red local o Internet.

Snet se ocupa de transportar mensajes; ServisX mantiene la coordinación entre servicios.

### Servicio de plugins

Administra los plugins y permite extender FGEngine. Los plugins deberían comunicarse mediante una interfaz definida, en lugar de acceder directamente a las estructuras internas del motor.

## Flujo general

```text
                    ┌──────────────┐
                    │    Snet      │ ⇄ Exterior
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   ServisX    │
                    └───┬───────┬──┘
                        │       │
              ┌─────────▼─┐   ┌─▼──────────┐
              │ FGEngine  │   │ Renderer   │
              │ + scripts │   │   SDL2     │
              └────┬──────┘   └────────────┘
                   │
            ┌──────▼───────┐
            │   Plugins    │
            └──────────────┘
```

Un ejemplo de interacción sería:

1. El usuario presiona una tecla.
2. El renderer convierte la entrada en un mensaje.
3. ServisX enruta el mensaje a FGEngine.
4. FGEngine procesa la acción y actualiza el estado.
5. El nuevo estado llega al renderer.
6. El renderer lo dibuja.

Ejemplo de mensaje:

```json
{
  "type": "input",
  "action": "move",
  "x": 1,
  "y": 0
}
```

Ejemplo de estado enviado al renderer:

```json
{
  "type": "state",
  "objects": [
    {"id": 1, "x": 120, "y": 80}
  ]
}
```

## Apagado ordenado

El cierre podría seguir este flujo:

```text
Renderer → ServisX: render_user_shutdown
ServisX → Servicios: prepare_shutdown
Servicios → ServisX: ready_to_stop
ServisX → Servicios: stop
```

Así el renderer expresa la intención de cerrar, pero ServisX se encarga de detener los servicios de forma coordinada. Sería útil definir qué ocurre si algún servicio no responde a tiempo.

## Decisiones pendientes

1. **¿Para qué se diseña FGEngine?**  
   ¿Principalmente para juegos, para aplicaciones generales o para ambos? Esto afecta qué servicios conviene incluir en el núcleo.

2. **¿Qué significan los “cheats” en este proyecto?**  
   ¿Códigos de trucos para juegos, comandos de consola para desarrolladores, herramientas de pruebas o modificaciones permitidas por plugins? Según la respuesta, podrían ser una función del motor, un plugin o una interfaz de depuración separada.

3. **¿Cómo se escriben los scripts?**  
   ¿Quieres usar un lenguaje existente, como Lua, o crear uno propio? ¿Los scripts deberían poder acceder a todas las funciones del motor o solo a una API limitada?

4. **¿Será multiplataforma?**  
   ¿Qué sistemas operativos quieres admitir? SDL2 facilita una capa gráfica multiplataforma, pero también habría que considerar la compilación, los plugins, la comunicación entre servicios y las diferencias entre sistemas.

5. **¿Los servicios serán procesos separados?**  
   Si lo son, habrá que definir cómo se comunican y qué pasa si uno falla. Si inicialmente viven dentro de un solo proceso, la arquitectura puede conservar las mismas interfaces y separarlos más adelante.

6. **¿Qué puede conectarse a Snet?**  
   ¿Solo clientes locales, otras aplicaciones de la red o también conexiones remotas? Para conexiones externas habría que definir autenticación, permisos y límites a los mensajes.

7. **¿Qué tipo de aplicaciones quieres habilitar?**  
   ¿El motor mantendrá un estado por fotogramas, como en un juego, o también podrá ejecutar tareas y aplicaciones orientadas a eventos?

8. **¿Cómo se administran los plugins?**  
   ¿Se cargan al iniciar, se pueden activar y desactivar durante la ejecución, y qué permisos tienen?

9. **¿Cómo se ordenan los mensajes?**  
   ¿Necesitas respuesta inmediata para entradas y acciones, o también mensajes de eventos que el renderer pueda procesar en su siguiente ciclo?

10. **¿Qué responsabilidad tiene `render_user_shutdown`?**  
    ¿Es un mensaje enviado una sola vez al cerrar, o un flag persistente que ServisX consulta? Un mensaje de cierre explícito suele hacer más fácil distinguir entre una petición, una confirmación y un error.

11. **¿Cómo se guardan los proyectos y recursos?**  
    ¿Los scripts, imágenes, sonidos y configuración forman parte de un paquete del proyecto, o cada plugin puede distribuir sus propios recursos?

12. **¿Qué debe pasar si el renderer se cierra inesperadamente?**  
    ¿FGEngine sigue ejecutándose, se apaga todo el sistema o queda en espera de que otro renderer se conecte?

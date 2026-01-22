[README_SIMULADOR.txt](https://github.com/user-attachments/files/22070251/README_SIMULADOR.txt)
# Simulador de Procesos y Memoria  

## Descripción  
Este proyecto implementa un simulador de gestión de procesos y asignación de memoria en **Python**, utilizando **Tkinter** para la interfaz gráfica.  
El objetivo es representar, de forma visual e interactiva, cómo se gestionan los procesos en un sistema operativo básico bajo el algoritmo de planificación **Round Robin** y con **memoria particionada fija**.  

## Características principales  
- **Planificación Round Robin** con *quantum* configurable.  
- **Asignación de memoria con particiones fijas** mediante el algoritmo *first-fit*.  
- Visualización en tiempo real de:  
  - Procesos en distintos estados: Listo, Ejecutando, Bloqueado, Terminado.  
  - Ocupación de memoria en bloques.  
  - Tabla de procesos con información detallada.  
- **Interfaz gráfica interactiva**:  
  - Botón *Auto* para ejecución automática.  
  - Botón *Tick* para avanzar la simulación paso a paso.  
  - Botón *Agregar proceso*.  
  - Botón *Ajustes…* para modificar parámetros de la simulación.  
- **Ordenamiento de tabla** por columnas, con flechas de dirección (ascendente/descendente).  
- Opciones de configuración avanzadas:  
  - Velocidad de simulación (ms por tick).  
  - Quantum de Round Robin.  
  - Rango de CPU inicial para nuevos procesos.  
  - Probabilidad de bloqueo por tick.  
  - Rango de duración de operaciones de I/O.  
  - Reaplicar configuración de CPU a procesos existentes.  
  - Reiniciar particiones de memoria con un nuevo esquema.  

## Requisitos  
- Python 3.9 o superior (probado en Python 3.11).  
- Librería Tkinter (incluida en la mayoría de instalaciones estándar de Python).  

Verificación rápida de Tkinter:  
```bash
python -c "import tkinter; print('Tkinter disponible')"
```  

## Instalación  
1. Guardar el archivo como `simulador_so.py`.  
2. No requiere instalación de dependencias adicionales.  

## Ejecución  
En consola:  
```bash
python simulador_so.py
```  

## Uso de la interfaz  
### Panel izquierdo: Memoria  
- Muestra cada partición de memoria como un bloque.  
- Los bloques ocupados muestran el PID del proceso y la memoria usada.  
- Los bloques libres aparecen en gris con la etiqueta `(LIBRE)`.  

### Panel derecho  
- **Controles**: Auto, Tick, Agregar proceso, Ajustes.  
- **Resumen**: información sobre memoria usada, procesos en cada estado, quantum y velocidad.  
- **Tabla de procesos**: con columnas PID, Estado, Memoria requerida, Partición asignada, CPU restante, I/O restante.  

### Ajustes  
- **Velocidad (ms/tick)**: determina la frecuencia de actualización.  
- **Quantum**: número de ticks que un proceso puede usar antes de ser desalojado.  
- **CPU inicial mín–máx**: rango aleatorio de CPU asignada a los procesos nuevos.  
- **Probabilidad de bloqueo**: porcentaje de chance de que un proceso en CPU pase a Bloqueado en cada tick.  
- **Duración de I/O (mín–máx)**: rango de ticks que un proceso permanecerá en Bloqueado.  
- **Aplicar a existentes**: reasigna CPU restante a procesos activos.  
- **Reiniciar particiones**: permite definir un nuevo esquema de particiones (ejemplo: `4,4,8,16`).  

## Lógica de simulación  
- **Estados de procesos**:  
  - *Listo*: esperando CPU.  
  - *Ejecutando*: en uso de CPU.  
  - *Bloqueado*: esperando I/O.  
  - *Terminado*: finalizado y liberando memoria.  

- **Planificación Round Robin**:  
  - Los procesos listos se ejecutan según el quantum.  
  - Si el quantum se agota y hay otros procesos listos, el proceso es desalojado y vuelve a la cola.  
  - Si un proceso se bloquea, pasa al estado *Bloqueado* hasta que termine su I/O.  

- **Asignación de memoria**:  
  - Se usa particionamiento fijo.  
  - Los procesos requieren un tamaño de memoria aleatorio.  
  - Se asigna usando *first-fit*.  
  - Si no hay espacio, el proceso queda en espera de memoria.  

## Ordenamiento de la tabla  
- Al hacer clic en cualquier encabezado, la tabla se ordena.  
- El primer clic ordena de forma descendente, el siguiente alterna a ascendente.  
- El orden seleccionado se mantiene entre actualizaciones de la simulación.  

## Ejemplo de ejecución  
1. Iniciar el programa (`python simulador_so.py`).  
2. Observar los procesos iniciales en memoria y en la tabla.  
3. Usar *Agregar proceso* para crear nuevos procesos.  
4. Abrir *Ajustes…* para modificar parámetros como quantum o velocidad.  
5. Ordenar la tabla por CPU restante o estado para analizar el comportamiento.  

## Licencia  
Este simulador se distribuye con fines educativos y prácticos, para el estudio de conceptos de sistemas operativos.  
Autor: Tomás Romero Baylac.
![fe74cd5b-33a3-4eae-907d-b87ab024718d](https://github.com/user-attachments/assets/d57ba523-fee1-4174-ac18-31a11da2a50d)

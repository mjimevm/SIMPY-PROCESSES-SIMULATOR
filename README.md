# SIMPY-PROCESSES-SIMULATOR

Simulación usando Simpy en Python para modelar la corrida de procesos en un sistema operativo de tiempo compartido.

El modelo implementa el ciclo de vida típico de un proceso:

- **new**: el proceso llega y solicita memoria RAM.
- **ready**: espera turno para usar el CPU.
- **running**: ejecuta un *quantum* (tiempo compartido).
- **waiting**: (con probabilidad) hace I/O y regresa a ready.
- **terminated**: termina y libera memoria.

---

## Requisitos

- Python 3.9+ (recomendado)
- Librerías:
  - `simpy`
  - `matplotlib`

Instalación:

```bash
pip install simpy
pip install matplotlib
```

---

## Cómo ejecutar

Ejecuta el simulador:

```bash
python SIMPY-PROCESSES-SIMULATOR.py
```

El programa:

1. Corre múltiples experimentos automáticamente.
2. Imprime en consola una tabla con:
   - **promedio** del tiempo total en el sistema por proceso
   - **desviación estándar**
3. Genera gráficas en PNG (en el mismo directorio):
   - `simpy_processes_interval_10.png`
   - `simpy_processes_interval_5.png`
   - `simpy_processes_interval_1.png`

---

## Modelo


- **Llegada de procesos**: distribución exponencial con intervalo `interval`:
  - `random.expovariate(1.0 / interval)`
- **RAM total**:
  - Base: 100
  - Experimento: 200
- **RAM por proceso**: entero aleatorio entre 1 y 10.
- **Instrucciones por proceso**: entero aleatorio entre 1 y 10.
- **CPU**:
  - Base: 1 CPU (Resource capacity = 1)
  - Experimento: 2 CPUs (capacity = 2)
- **Quantum de CPU**:
  - 1 unidad de tiempo ejecuta **K instrucciones**
  - Base: `K = 3`
  - CPU más rápido: `K = 6`
  - Si un proceso tiene menos de K instrucciones pendientes, libera el CPU antes (tiempo proporcional).
- **Decisión al salir del CPU**:
  - Se genera un entero `action` entre 1 y 21.
  - Si `action == 1` → pasa a **waiting** (I/O).
  - Si `action == 2` → regresa a **ready**.
  - En cualquier otro caso → regresa a **ready**.
- **I/O**:
  - Tiempo fijo: 1 unidad
  - Modelado con `simpy.Resource(capacity=1)` (cola de waiting).

---

## Experimentos que ejecuta el script

Se corren combinaciones de:

- Cantidad de procesos: **25, 50, 100, 150, 200**
- Intervalo de llegada: **10, 5, 1**

Para cada intervalo, se comparan estrategias:

1. **base**: RAM=100, CPU=1, K=3
2. **ram_incrementado_200**: RAM=200, CPU=1, K=3
3. **cpu_rapido_6_instr**: RAM=100, CPU=1, K=6
4. **dos_cpus**: RAM=100, CPU=2, K=3

---

## Salida esperada

En consola verás bloques como:

- Escenario + intervalo
- Tabla por N procesos con promedio y desviación estándar

Y al final un resumen indicando la mejor estrategia según el **promedio global** de los promedios (heurística simple).

---

## Notas

- Se usa `random.seed(RANDOM_SEED)` para reproducibilidad y comparación entre escenarios.
- La RAM se modela con `simpy.Container`, por lo que **si no hay suficiente memoria el proceso espera** (cola implícita) hasta que haya.
- El CPU e I/O se modelan con `simpy.Resource` para representar colas de espera.

---

## Archivos

- `SIMPY-PROCESSES-SIMULATOR.py`: simulación + experimentos + gráficas
- `README.md`: este documento

---

## Autor

Jimena Vásquez - 25092

--- 

## Asignatura

Algoritmos y Estructura de Datos

Sección 20

---

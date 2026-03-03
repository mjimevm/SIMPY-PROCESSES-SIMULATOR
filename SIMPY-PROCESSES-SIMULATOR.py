"""
SIMULADOR DE PROCESOS DE IO SYSTEM CON SIMPY
@author: Jimena Vásquez

"""

import random
import statistics
import simpy
import matplotlib.pyplot as plt


RANDOM_SEED = 271125

N_LIST = [25, 50, 100, 150, 200]
INTERVALS = [10, 5, 1]

RAM_MIN = 1
RAM_MAX = 10

INSTRUCCIONES_MIN = 1
INSTRUCCIONES_MAX = 10

IO_TIME = 1.0

CPU_QUANTUM_TIME = 1.0 
ACTION_MAX = 21
GO_TO_WAITING = 1
GO_TO_READY = 2


def source(env, number, interval, CPU, RAM, IO, instructions_per_quantum, finished_times, verbose=False):
    for i in range(number):
        RAM_needed = random.randint(RAM_MIN, RAM_MAX)
        p = process(env, 'Proceso %03d' % (i + 1), RAM_needed, CPU, RAM, IO,
                    instructions_per_quantum, finished_times, verbose)
        env.process(p)
        t = random.expovariate(1.0 / float(interval))
        yield env.timeout(t)


def process(env, name, RAM_needed, CPU, RAM, IO, instructions_per_quantum, finished_times, verbose=False):
    arrive = env.now
    if verbose:
        print('%7.4f %s: EMPEZANDO, RAM NECESARIA: %d' % (arrive, name, RAM_needed))

    # Solicita RAM (Container hace cola si no hay suficiente)
    yield RAM.get(RAM_needed)
    if verbose:
        print('%7.4f %s: CONSIGUIÓ RAM (%d). PASA A READY' % (env.now, name, RAM_needed))

    # Instrucciones totales del proceso
    instructions = random.randint(INSTRUCCIONES_MIN, INSTRUCCIONES_MAX)

    while instructions > 0:
        # READY
        with CPU.request() as cpu_req:
            yield cpu_req

            executed = instructions_per_quantum if instructions >= instructions_per_quantum else instructions

            run_time = CPU_QUANTUM_TIME * (float(executed) / float(instructions_per_quantum))
            yield env.timeout(run_time)

            instructions -= executed

            if verbose:
                print('%7.4f %s: INSTRUCCIONES RESTANTES: %d' %
                      (env.now, name, max(instructions, 0)))

        if instructions <= 0:
            break

        action = random.randint(1, ACTION_MAX)

        # WAITING O READY
        if action == GO_TO_WAITING:
            if verbose:
                print('%7.4f %s: waiting for I/O' % (env.now, name))
            with IO.request() as io_req:
                yield io_req
                yield env.timeout(IO_TIME)
            if verbose:
                print('%7.4f %s: Finished I/O, back to ready' % (env.now, name))
        elif action == GO_TO_READY:
            if verbose:
                print('%7.4f %s: ready' % (env.now, name))
        else:
            pass

    yield RAM.put(RAM_needed)
    finish = env.now
    if verbose:
        print('%7.4f %s: terminated (tiempo total=%.4f)' % (finish, name, finish - arrive))

    finished_times.append(finish - arrive)


def run_simulation(n_processes, interval, ram_capacity, cpu_count, instructions_per_quantum, seed, verbose=False):
    random.seed(seed)
    env = simpy.Environment()

    RAM = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)
    CPU = simpy.Resource(env, capacity=cpu_count)
    IO = simpy.Resource(env, capacity=1)

    finished_times = []
    env.process(source(env, n_processes, interval, CPU, RAM, IO, instructions_per_quantum, finished_times, verbose))
    env.run()

    avg = statistics.mean(finished_times) if finished_times else 0.0
    sd = statistics.stdev(finished_times) if len(finished_times) >= 2 else 0.0
    return avg, sd, finished_times



def scenarios():
    return {
        "base": {"RAM": 100, "CPUS": 1, "k": 3},
        "ram_incrementado_200": {"RAM": 200, "CPUS": 1, "k": 3},
        "cpu_rapido_6_instr": {"RAM": 100, "CPUS": 1, "k": 6},
        "dos_cpu": {"RAM": 100, "CPUS": 2, "k": 3},
    }


def run_all(verbose=False):
    all_results = {}

    for scen_name, params in scenarios().items():
        for interval in INTERVALS:
            key = (scen_name, interval)
            all_results[key] = {}
            for n in N_LIST:
                avg, sd, _ = run_simulation(
                    n_processes=n,
                    interval=interval,
                    ram_capacity=params["RAM"],
                    cpu_count=params["CPUS"],
                    instructions_per_quantum=params["k"],
                    seed=RANDOM_SEED,  # misma secuencia para comparar
                    verbose=verbose if n <= 25 else False,
                )
                all_results[key][n] = (avg, sd)

    return all_results

"""FUNCIONES DE MATPLOTLIB Y ANÁLISIS DE RESULTADOS"""
def print_results(all_results):
    for (scen, interval), per_n in all_results.items():
        print("\n" + "=" * 72)
        print("Escenario: %s | interval=%s" % (scen, interval))
        print("-" * 72)
        print("No_Procesos| Tiempo_Promedio | Desviacion_Estándar")
        for n in sorted(per_n.keys()):
            avg, sd = per_n[n]
            print("%9d  | %14.6f  | %18.6f" % (n, avg, sd))


def plot_results(all_results, prefix="simpy_processes"):
    intervals = sorted(set(interval for (_s, interval) in all_results.keys()))

    for interval in intervals:
        plt.figure(figsize=(10, 6))
        plt.title("Tiempo promedio vs Número de Procesos (Intervalo: %s)" % interval)
        plt.xlabel("Número de procesos")
        plt.ylabel("Tiempo promedio en el sistema")

        for (escenario, i), per_n in all_results.items():
            if i != interval:
                continue
            xs = sorted(per_n.keys())
            ys = [per_n[n][0] for n in xs]
            plt.plot(xs, ys, marker="o", linewidth=2, label=escenario)

        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig("%s_interval_%s.png" % (prefix, interval), dpi=160)
        plt.close()

# Función simple para elegir la mejor estrategia según el promedio global
def best_strategy_simple(all_results):
    escenarios = {}
    for (escenario), per_n in all_results.items():
        escenarios.setdefault(escenario, [])
        for n in per_n:
            escenarios[escenario].append(per_n[n][0])

    best = None
    best_score = None
    for escenario, vals in escenarios.items():
        score = statistics.mean(vals) if vals else float("inf")
        if best is None or score < best_score:
            best = escenario
            best_score = score

    return best, best_score

"""============================================================================="""
"""               EJECUCIÓN DE SIMULACIÓN Y ANÁLISIS DE RESULTADOS              """
"""-----------------------------------------------------------------------------"""
print('PROCESSES SIMULATION')
random.seed(RANDOM_SEED)

all_results = run_all(verbose=False)
print_results(all_results)
plot_results(all_results, prefix="simpy_processes")

best, score = best_strategy_simple(all_results)
print("\n" + "=" * 72)
print("Mejor estrategia (promedio global): %s (score=%.6f)" % (best, score))
print("Gráficas generadas: simpy_processes_interval_10.png, _5.png, _1.png\n")
"""============================================================================="""
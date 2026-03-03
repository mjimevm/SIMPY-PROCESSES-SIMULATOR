"""
SIMULADOR DE PROCESOS DE IO SYSTEM CON SIMPY
@author: Jimena Vásquez

"""
import random

import simpy

RANDOM_SEED = 20000
# NEW 
NEW_PROCESSES = 5
RAM_CAPACITY = 10
AVERAGE_TIME_BETWEEN_ARRIVALS = 5.0

CPU_TIME_PER_INSTRUCTION = 1.0
IO_TIME = 1.0

def source(env, number, numInstructions, RAM):
    for i in range(number):
        RAM_needed = random.randint(1, 10)
        p = process(env, 'Proceso %02d' % (i+1), RAM_needed, numInstructions, RAM)
        env.process(p)
        t = random.expovariate(1.0 / AVERAGE_TIME_BETWEEN_ARRIVALS)
        yield env.timeout(t)

def process(env, name, RAM_needed, numInstructions, RAM):
    arrive = env.now
    print('%7.4f %s: EMPEZANDO, RAM NECESARIA: %d' % (arrive, name, RAM_needed))
    if RAM.count + RAM_needed > RAM.capacity:
        print('%7.4f %s: NO HAY SUFICIENTE RAM. ESPERANDO.' % (arrive, name))
        return
    with RAM.request() as req:
        yield req
        print('%7.4f %s: CONSIGUIÓ ESPACIO EN RAM. EMPEZANDO EJECUCIÓN' % (arrive, name))
        instructions = random.randint(1, 10)
        while instructions > 0:
            yield env.timeout(CPU_TIME_PER_INSTRUCTION * min(numInstructions, instructions))
            instructions -= 3
            print('%7.4f %s: INSTRUCCIONES RESTANTES: %d' % (arrive, name, max(instructions, 0)))

        print('%7.4f %s: terminated' % (arrive, name))

        action = random.randint(1, 21)

        if action == 1:
            print('%7.4f %s: waiting for I/O' % (arrive, name))
            yield env.timeout(IO_TIME)
            print('%7.4f %s: Finished I/O, back to ready' % (arrive, name))

        elif action == 2:
            print('%7.4f %s: ready' % (arrive, name))


print('PROCESSES SIMULATION')
random.seed(RANDOM_SEED)
env = simpy.Environment()
RAM = simpy.Resource(env, capacity=RAM_CAPACITY)
env.process(source(env, NEW_PROCESSES, 3, RAM))
env.run()
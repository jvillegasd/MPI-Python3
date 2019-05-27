#Primos con paralelismo
from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

k = 10
iter_int = 2
primes_per_process = 0
seeded = 0
cnt = 0
ver_number = 0

def master(slaveW, isPrime):
    global iter_int, seeded, k
    if slaveW == 0:
        for i in range(1, size):
            if seeded == 0:
                comm.send(iter_int, dest = i)
            else:
                f = comm.recv()
                comm.send(iter_int, dest = f)
            iter_int+=1
        seeded = 1
    elif slaveW == 1 and isPrime == 1:
        global primes_per_process 
        primes_per_process+=1

def slave(last):
    number = comm.recv(source = 0)
    global k, ver_number
    flag = 1
    for i in range(2, number//2 + 1):
        if number % i == 0:
            flag = 0
            break
    if last == 0:
        comm.send(rank, dest = 0)
    if number <= k:
        ver_number+=1
        master(1, flag)

start = time.time()
while iter_int < k:
    if rank == 0:
        master(0, 0)
    else:
        slave(0)
    iter_int = comm.bcast(iter_int, root = 0)
    seeded = comm.bcast(seeded, root = 0)

if rank == 0:
    master(0, 0)
else:
    slave(1)

cnt = comm.reduce(primes_per_process, op = MPI.SUM, root = 0)
end = time.time()

if rank == 0:
    print('Numeros primos de [1 - {}]: {}'.format(k, cnt))
    print('Tiempo de ejecucion: {} secs'.format(end - start))
else:
    print('Proceso {} ha validado {} numeros'.format(rank, ver_number))
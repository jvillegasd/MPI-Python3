from mpi4py import MPI
from prettytable import PrettyTable
import numpy as np
import sys
import time
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

k = int(sys.argv[1])
friendly = 0

def checkRight():
    MPI.Win.Lock(shared_block, rank, MPI.LOCK_EXCLUSIVE)
    aux = rank
    can_pick = False
    rtime = random.randint(5, 15)
    if forks[aux] == 0:
        forks[aux] = rank
        can_pick = True
        MPI.Win.Unlock(shared_block, rank)
    elif friendly == 1:
        MPI.Win.Unlock(shared_block, rank)
        time.sleep(rtime)
        MPI.Win.Lock(shared_block, rank, MPI.LOCK_EXCLUSIVE)
        if forks[aux] == 0:
            forks[aux] = rank
            can_pick = True
        MPI.Win.Unlock(shared_block, rank)
    elif friendly == 0:
        MPI.Win.Unlock(shared_block, rank)
        while forks[aux] != rank:
            MPI.Win.Lock(shared_block, rank, MPI.LOCK_EXCLUSIVE)
            if forks[aux] == 0:
                forks[aux] = rank
                can_pick = True
            MPI.Win.Unlock(shared_block, rank)
    if not can_pick:
        give_forks(True)
    return can_pick

def checkLeft():
    MPI.Win.Lock(shared_block, rank, MPI.LOCK_EXCLUSIVE)
    aux = rank - 1
    can_pick = False
    if aux <= 0:
        aux = size - 1
    if forks[aux] == 0:
        forks[aux] = rank
        can_pick = True
    MPI.Win.Unlock(shared_block, rank)
    return can_pick

def think():
    rtime = random.randint(7, 10)
    time.sleep(rtime)

def eat():
    rtime = random.randint(2, 5)
    time.sleep(rtime)

def give_forks(time_out):
    MPI.Win.Lock(shared_block, rank, MPI.LOCK_EXCLUSIVE)
    if not time_out:
        aux = rank
        forks[aux] = 0 
    aux = rank - 1
    if aux <= 0:
        aux = size - 1
    forks[aux] = 0
    MPI.Win.Unlock(shared_block, rank)

def printTable():
    output.field_names = ["Filosofo {} ({})".format(i, "1" if table[i] == 1 else "2") for i in range(1, size)]
    row = ["" for i in range(size)]
    row1 = ["" for i in range(size)]
    for i in range(1, size):
        l = i - 1
        r = i
        if l <= 0:
            l = size - 1
        if forks[l] == i:
            row[i]+="x |"
        else:
            row[i]+="- |"
        if forks[r] == i:
            row[i]+=" x"
        else:
            row[i]+=" -"
        if forks[l] == 0:
            row1[i]+="x"
        else:
            row1[i] = "-"
    output.add_row(row[1:])
    output.add_row(row1[1:])
    print(output)
    output.clear_rows()
    
if rank == 0:
    fsize_bytes = (size + 1) * MPI.DOUBLE.Get_size() #Size in bytes of shared memory block
    a1 = random.randint(1, size - 1)
    a2 = random.choice([i for i in range(1, size) if not i in [a1]])
    table = [0]*size
    for i in range(1, size):
        if i != a1 and i != a2:
            table[i] = 1
    output = PrettyTable()
else:
    fsize_bytes = 0
    table = []

#Creating shared memory block
shared_block = MPI.Win.Allocate_shared(fsize_bytes, MPI.DOUBLE.Get_size(), comm = comm) #Return Win object for RMA Operations
buf, fsize_bytes = shared_block.Shared_query(0) #Querying for the buffer/pointer of the memory block and size of bytes
assert fsize_bytes == MPI.DOUBLE.Get_size() #Making sure the query has the same size of bytes
forks = np.ndarray(buffer = buf, dtype = 'i', shape = (size + 1, )) #Init numpy array and point it to memory block

friendly = comm.scatter(table, root = 0) #Assigning which process is friendly (1) or not (2)
if size <= 3 and rank == 0:
    print('Number of processes is not allowed. Minimum number of processes is 4')

while True and size >= 4:
    if rank == 0:
        printTable()
        sys.stdout.flush()
        time.sleep(1)
        if forks[size] == size - 1:
            break
    else:   
        think()
        if checkLeft() and checkRight():
            eat()
            give_forks(False)
            think()
            k-=1
            if k == 0:
                forks[size]+=1
                break
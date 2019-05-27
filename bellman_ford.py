from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def bellmanFord(vertex):
    global n, g, e
    dist = [100**100 for u in range(n + 1)]
    parent = [[] for u in range(n + 1)]
    dist[vertex] = 0
    parent[vertex] = vertex
    for i in range(e - 1):
        for u in range(1, n + 1):
            for pair in g[u]:
                v = pair[0]
                w = pair[1]
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u
    return parent

def master(slaveW, path, u):
    global nodes, paths, n
    if slaveW == 0:
        for i in range(1, size):
            comm.send(nodes, dest = i, tag = i)
            if nodes < n:
                nodes+=1 
    else:
        paths[u].append(path)

def slave():
    global n, nodes
    u = comm.recv(source = 0, tag = rank)
    if u <= n:
        path = bellmanFord(u)
        master(1, path, u)

nodes = 1
if rank == 0:
    graph_file = open('grafo.txt', 'r')
    n = int(graph_file.readline())
    e = 0
    g = [[] for u in range(n + 1)]
    paths = [[] for u in range(n + 1)]

    for line in graph_file:
        edge = [int(number) for number in line.split() if number.isdigit()]
        e+=1
        g[edge[0]].append([edge[1], edge[2]])
        g[edge[1]].append([edge[0], edge[2]])

    graph_file.close()
else:
    g = None
    n = None
    e = None
    paths = None
n = comm.bcast(n, root = 0)
e = comm.bcast(e, root = 0)
g = comm.bcast(g, root = 0)
paths = comm.bcast(paths, root = 0)

start = time.time()
while nodes < n:
    if rank == 0:
        master(0, [], 0)
    else:
        slave()
    nodes = comm.bcast(nodes, root = 0)

if rank == 0:
    master(0, [], 0)
else:
    slave()
end = time.time()

paths = comm.gather(paths, root = 0)
vist = [0 for u in range(n + 1)]
if rank == 0:
    for i in range(1, size):
        u = 0
        for li in paths[i]:
            if li != [] and vist[u] == 0:
                li = li[0]
                print('V{}: '.format(u))
                vist[u] = 1
                for v in range(1, n + 1):
                    print('{}: {}'.format(v, u), end = '')
                    path = []
                    i = li[v]
                    while i != u:
                        path.append(i)
                        i = li[i]
                    path.reverse()
                    for p in path:
                        print(', {}'.format(p), end = '')
                    print()
                print('\n')
            u+=1
    print('Tiempo de ejecucion: {} secs'.format(end - start))
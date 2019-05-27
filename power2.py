from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
	data = [i for i in range(size)]
else:
	data = None
data = comm.scatter(data, root = 0)
data = data**2

new_data = comm.gather(data, root = 0)
if rank == 0:
	print("root received ", new_data)
	
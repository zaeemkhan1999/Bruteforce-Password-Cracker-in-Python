from itertools import product
import subprocess
from mpi4py import MPI

# Define the output file name, password length, and character set
output_file = 'passwords.txt'
password_length = 5
character_set = 'agrz3'

# Function to check if a password is successful
def check_password(password):
    print('Checking password:', password)
    process = subprocess.Popen(['C:\\Unrar\\UnRAR.exe', 'x', '-p' + password, 'Newfolder.rar'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode == 0

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Generate all possible combinations of passwords
possible_passwords = list(product(character_set, repeat=password_length))

# Divide passwords into chunks for each MPI process
chunk_size = len(possible_passwords) // size
start = rank * chunk_size
end = start + chunk_size if rank != size - 1 else len(possible_passwords)

print('Rank:', rank, 'Start:', start, 'End:', end)

# Each process checks its chunk of passwords
successful_passwords = []
for password_tuple in possible_passwords[start:end]:
    password = ''.join(password_tuple)
    if check_password(password):
        successful_passwords.append(password)

# Gather successful passwords from all MPI processes
all_successful_passwords = comm.gather(successful_passwords, root=0)

# Save passwords to the output file if the current process is the root process (rank 0)
if rank == 0:
    with open(output_file, 'w') as file:
        for passwords in all_successful_passwords:
            file.writelines([password + '\n' for password in passwords])

    print('Passwords generated and saved to', output_file)
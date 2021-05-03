from cryptography.fernet import Fernet
from time import time

file = open('key.key', 'rb')  # Open the file as wb to read bytes
key = file.read()  # The key will be type bytes
file.close()

test_message = "This is the long enough"
f = Fernet(key)

start_time = time()
message = test_message.encode()
f.encrypt(message)
end_time = time()
print(end_time-start_time)

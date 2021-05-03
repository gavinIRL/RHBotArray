from cryptography.fernet import Fernet
from time import time

file = open('key.key', 'rb')  # Open the file as wb to read bytes
key = file.read()  # The key will be type bytes
file.close()

test_message = "This is long enough"
f = Fernet(key)


message = test_message.encode()
message = f.encrypt(message)


start_time = time()
decrypted = f.decrypt(message)
end_time = time()
print(end_time-start_time)
print(decrypted.decode())

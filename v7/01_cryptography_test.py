from cryptography.fernet import Fernet

key = Fernet.generate_key()
file = open('key.key', 'wb')  # Open the file as bytes
file.write(key)  # The key is type bytes
file.close()

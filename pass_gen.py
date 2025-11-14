import random

# Characters to use in the password
characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"

# Ask the user for password length
length = int(input("Enter password length: "))

password = ""

# Generate password character by character
if length < 8:
    print("Password length should be at least 8 characters.")
else:
    for i in range(length):
        password += random.choice(characters)
    print("Generated Password:", password)

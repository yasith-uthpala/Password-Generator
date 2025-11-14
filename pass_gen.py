import random

# Characters to use in the password
characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"

# Ask the user for password length
length = int(input("Enter password length: "))

password = ""

# Generate password character by character
for i in range(length):
    password += random.choice(characters)

print("Generated Password:", password)

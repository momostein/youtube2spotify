# Generate a secret key for the flask app

import os

FILENAME = 'secret.key'


def generate(length=16):
    key = os.urandom(length)
    with open(FILENAME, 'wb') as f:
        f.write(key)

    return key


def get(generate=False, length=16):
    try:
        with open(FILENAME, 'rb') as f:
            key = f.read()

    except FileNotFoundError as error:
        if generate:
            key = generate(length)
        else:
            raise (error)

    return key


if __name__ == "__main__":
    try:
        length = int(input('Key length: '))
    except ValueError as error:
        print("You must input a valid number!")

    generate(length)

    print(get())

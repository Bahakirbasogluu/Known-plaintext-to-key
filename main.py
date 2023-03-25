import math
import string
import sys
import numpy as np
from sympy import Matrix

def display_menu():
    print("1) Force a Ciphertext (Known Plaintext Attack).")
    print("2) Quit.\n")
    choice = int(input("Select a function to run: "))
    return choice

# Create two dictionaries, mapping English alphabet to numbers and vice versa, and return them
def create_alphabet_dict():
    alphabet_to_num = {}
    for character in string.ascii_uppercase:
        alphabet_to_num[character] = string.ascii_uppercase.index(character)

    num_to_alphabet = {}
    for key, value in alphabet_to_num.items():
        num_to_alphabet[value] = key

    return alphabet_to_num, num_to_alphabet


# Get input from the user and check if it respects the alphabet
def get_input_with_alphabet_check(message, alphabet_to_num):
    text = input(message)
    text = text.upper()
    for char in text:
        if char not in alphabet_to_num.keys():
            print(f"{char} is not a valid character. Please only use uppercase English letters.")
            return get_input_with_alphabet_check(message, alphabet_to_num)
    return text

# Create the matrix for the encryption key
def create_key_matrix(key, alphabet_to_num):
    key_as_list = list(key)
    matrix_size = int(math.sqrt(len(key_as_list)))
    for (i, character) in enumerate(key_as_list):
        key_as_list[i] = alphabet_to_num[character]

    return np.reshape(key_as_list, (matrix_size, matrix_size))


# Create the matrix of m-grams for a given text, and if needed, complete the last m-gram with the last letter of the alphabet
def create_text_matrix(text, m, alphabet_to_num):
    matrix = list(text)
    remainder = len(text) % m
    for (i, character) in enumerate(matrix):
        matrix[i] = alphabet_to_num[character]
    if remainder != 0:
        for i in range(m - remainder):
            matrix.append(25)

    return np.reshape(matrix, (int(len(matrix) / m), m)).transpose()


# Transform a matrix to a text, according to the alphabet
def matrix_to_text(matrix, order, num_to_alphabet):
    if order == 't':
        text_array = np.ravel(matrix, order='F')
    else:
        text_array = np.ravel(matrix)
    text = ""
    for i in range(len(text_array)):
        text = text + num_to_alphabet[text_array[i]]
    return text

# Check if the key matrix is invertible and if so, return the inverse of the matrix
def get_inverse_matrix(matrix, alphabet_to_num):
    alphabet_size = len(alphabet_to_num)
    if math.gcd(int(round(np.linalg.det(matrix))), alphabet_size) == 1:
        matrix = Matrix(matrix)
        return np.matrix(matrix.inv_mod(alphabet_size))
    else:
        return None

def get_gram_length():
    m = int(input("Insert the length of the m-grams (m): "))
    return m

# Force a Ciphertext (Known Plaintext Attack)
def known_plaintext_attack(ciphertext_matrix, plaintext_matrix_inverse, alphabet_to_num):
    m = ciphertext_matrix.shape[0]
    num_grams = plaintext_matrix_inverse.shape[1]

    # Encrypt the plaintext with the given encryption key k, calculating the matrix c of the ciphertext
    ciphertext = np.zeros((m, num_grams)).astype(int)
    for i in range(num_grams):
        ciphertext[:, i] = np.reshape(np.dot(ciphertext_matrix, plaintext_matrix_inverse[:, i]) % len(alphabet_to_num), m)
    return ciphertext


def main():
    # Ask the user what function wants to run
    choice = display_menu()

    # Get two dictionaries, english alphabet to numbers and numbers to english alphabet
    alphabet, reverse_alphabet = create_alphabet_dict()

    if choice == 1:
        # Asks the user the text and the ciphertext to use them for the plaintext attack
        plaintext = get_input_with_alphabet_check("\nInsert the plaintext for the attack: ", alphabet)
        ciphertext = get_input_with_alphabet_check("Insert the ciphertext of the plaintext for the attack: ", alphabet)

        # Asks the user the length of the grams
        m = get_gram_length()

        if len(plaintext) / m >= m:
            # Get the m-grams matrix p of the plaintext and takes the firsts m
            p = create_text_matrix(plaintext, m, alphabet)
            p = p[:, 0:m]

            # Check if the matrix of the plaintext is invertible and in that case returns the inverse of the matrix
            p_inverse = get_inverse_matrix(p, alphabet)

            if p_inverse is not None:
                # Get the m-grams matrix c of the ciphertext
                c = create_text_matrix(ciphertext, m, alphabet)
                c = c[:, 0:m]

                if c.shape[1] == p.shape[0]:
                    print("\nCiphertext Matrix:\n", c)
                    print("Plaintext Matrix:\n", p)

                    input("\nPress Enter to begin the attack.")

                    # Force the ciphertext provided
                    k = known_plaintext_attack(c, p_inverse, alphabet)

                    # Transform the key matrix to a text of the alphabet
                    key = matrix_to_text(k, "k", reverse_alphabet)

                    print("\nThe key has been found.\n")
                    print("Generated Key: ", np.transpose(key))
                    print("Generated Key Matrix:\n", k, "\n")
                else:
                    print("\nThe number of m-grams for plaintext and ciphertext are different.\n")
            else:
                print("\nThe matrix of the plaintext provided is not invertible.\n")
        else:
            print("\nThe length of the plaintext must be compatible with the length of the grams (m).\n")
    elif choice == 2:
        sys.exit(0)


if __name__ == '__main__':
    main()
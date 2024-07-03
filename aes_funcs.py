from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def encrypt_aes(key, plaintext):
    # Create a new AES cipher object in CBC mode with a random IV
    cipher = AES.new(key, AES.MODE_CBC)

    iv = cipher.iv

    # Pad the plaintext to be a multiple of the block size
    padded_plaintext = pad(plaintext, AES.block_size)
    # Encrypt the padded plaintext
    ciphertext = cipher.encrypt(padded_plaintext)

    # Prepend IV to ciphertext for use in decryption
    return iv + ciphertext


# Decryption
def decrypt_aes(key, ciphertext):
    # Get the vector from the start of the block
    iv = ciphertext[:AES.block_size]
    ciphertext = ciphertext[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext = unpad(padded_plaintext, AES.block_size)
    return plaintext

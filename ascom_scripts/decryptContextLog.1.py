from Crypto.Cipher import AES
import pkcs7
import base64
import hashlib
import binascii
from pkcs7 import PKCS7Encoder
import configparser


class AESCipher:
    class InvalidBlockSizeError(Exception):
        """Raised for invalid block sizes"""

        pass

    def __init__(self, key):
        self.key = bytes(key, "utf-8")
        self.iv = bytes(key[0:128], "utf-8")
        print(self.key)
        print(key[0:128])
        AES.block_size = 128

    def __pad(self, text):
        text_length = len(text)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def __unpad(self, text):
        pad = ord(text[-1])
        return text[:-pad]

    def encrypt(self, raw):
        raw = self.__pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return self.__unpad(cipher.decrypt(enc).decode("utf-8"))


# Open and parse config.ini
settings_file = "config.ini"
settings = configparser.ConfigParser()
settings.read(settings_file)

logpath = r"/app/csvs/log.txt.encrypted"
logout = r"/app/csvs/log.txt.dencrypted"

# Open input file and output file
f = open(logpath, "r")
f_out = open(logout, "w")

# Getting settings from config.ini
BlockSize = 256
SecurePassword = settings.get("Ascom", "ascompassword")

print(SecurePassword)
# print(BlockSize)
e = AESCipher(SecurePassword)
# decr_str = e.decrypt(msg)
for line in f:
    # print("Type: {}; Line: {}".format(type(line), line))

    decr_str = e.decrypt(line)
    # print(decr_str)
    # print("______")
    f_out.write(decr_str + "\n")

f.close()
f_out.close()
print("*****END*****")


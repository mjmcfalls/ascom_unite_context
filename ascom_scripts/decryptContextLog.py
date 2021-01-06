from Crypto.Cipher import AES 
import pkcs7, sys, getopt, re, os, time
import base64, hashlib, binascii
from pkcs7 import PKCS7Encoder
import logging, configparser

class AESCipher:
    class InvalidBlockSizeError(Exception):
        """Raised for invalid block sizes"""
        pass

    def __init__(self, key):
        self.key = bytes(key, 'utf-8')
        self.iv = bytes(key[0:128], 'utf-8')
        # logging.debug(self.key)
        # logging.debug(key[0:128])
        AES.block_size = 256

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

    def encrypt( self, raw ):
        raw = self.__pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw)) 

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return self.__unpad(cipher.decrypt(enc).decode("utf-8"))

def processDirectory(directory, decryptInfo):
    tFile = []
    for i in sorted(os.listdir(directory), key=lambda x: x[9:], reverse=True):
        # logging.debug('%s' % directory + os.sep + i)
        # for i in f:
        if re.search('encrypted', i):
            print('Processing ', i)
            logging.debug('%s' % i) 
            # logging.debug(d + os.sep + i)
            f = open(directory + os.sep + i, 'r')
            for line in f:
                # logging.info('%s' % line)
                tFile.append(decryptLog(line, decryptInfo))
            f.close()
    # for t in tFile:
    #     logging.debug("%s" % t)
    return sorted(tFile)

def processSingleFile(iFile, decryptInfo):
    tFile = []
    logging.debug('%s' % iFile) 
    f = open(iFile, 'r')
    print('Processing ', iFile)
    for line in f:
        # logging.info('%s' % line)
        tFile.append(decryptLog(line, decryptInfo))
    # for t in tFile:
    #     logging.debug("%s" % t)
    return tFile

def decryptLog(f, decryptInfo):
    decr_str = decryptInfo.decrypt(f)
    return decr_str

def writeDecryptedLog(decryptedList, outFile):
        print("Saving logs to ", outFile)
        # f_out = open(outFile, 'w')
        with open(outFile, 'w', encoding='utf-8') as f_out:
            for line in decryptedList:
                # logging.debug("Line: %s" % line)
                f_out.write(line + "\n")
        # f.close()
        f_out.close()

def main(argv):
    # Open logging
    logging.basicConfig(level=logging.ERROR)
    # Open and parse config.ini
    settings_file = 'config.ini'
    settings = configparser.ConfigParser()
    settings.read(settings_file)
    # Get settings from .ini
    BlockSize = settings.get('Ascom','BlockSize')
    SecurePassword = settings.get('Ascom','ascompassword')

    logging.debug(SecurePassword)
    logging.debug(BlockSize)
    # Set secure info into AESCipher Class
    decryptInfo = AESCipher(SecurePassword)

    # Check command line arguments
    try:
        opts, args = getopt.getopt(argv, "hd:")
        logging.debug("opts: %s" % opts)
        logging.debug("args: %s" % args)
    except getopt.GetoptError:
        print("Error: ", opts, args)
        sys.exit(2)
    
    if len(args) == 1 and not opts:
        logging.debug("Process individual files")
        writeDecryptedLog(processSingleFile(args[0], decryptInfo), re.sub('encrypted', 'decrypted.log', args[0]))
    else: 
        for opt, arg in opts:
            logging.debug("Len(arg):%s " % len(arg))
            if opt in ('-h', ''):
                # print("-h if: ", opt, arg)
                print("HELP!")
            elif opt in ('-d', ''):
                logging.debug("%s, %s" % (opt, arg))
                # tempFiles = processDirectory(arg, decryptInfo)
                # decryptedList = decryptLog(, decryptInfo, BlockSize)
                writeDecryptedLog(processDirectory(arg, decryptInfo), 
                    arg + "\DecryptedLogs_" +time.strftime("%Y%m%d_%H%M%S")  + ".log")
            else:
                assert False, "Unknown option"

if __name__ == '__main__':
    main(sys.argv[1:])
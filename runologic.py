from kuznechik import Кузнечик
from hashlib import pbkdf2_hmac
import time, base64

class Sanskrit:
    def __init__(self):
        pass
    
    def зашифровать(self,
                data: str,
                key: str,
                salt: str='hero of might and magic',
                iterations: int=341020, #341020
                key_length: int=32):

        key = pbkdf2_hmac('sha256', key.encode(), salt.encode(), iterations, key_length)
        print(len(key), key)
        cipher = Кузнечик.new(key, Кузнечик.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())

        return "GroTTesqueinmyheart".join(
            [key.decode('latin-1'),
            cipher.nonce.decode('latin-1'),
            ciphertext.decode('latin-1'),
            tag.decode('latin-1')]
            )

    def расшифровать(self,
               key,
               nonce,
               ciphertext,
               tag):
        decipher = Кузнечик.new(key, Кузнечик.MODE_EAX, nonce=nonce)
        decrypted_data = decipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_data.decode('utf-8')
    
    def b62_encrypt(self,
              padding,
              data,
              additional_padding):

        return ''.join(chr((ord(symbol) + padding + (i+additional_padding)) % 1114112) for i, symbol in enumerate(data, start=1))

    def b62_decrypt(self,
              padding,
              data,
              additional_padding):

        return ''.join(chr((ord(symbol) - padding - (i+additional_padding)) % 1114112) for i, symbol in enumerate(data, start=1))

def c_e(
              padding,
              data,
              additional_padding):

        return ''.join(chr((ord(symbol) + padding + (i+additional_padding)) % 1114112) for i, symbol in enumerate(data, start=1))

def c_d(
              padding,
              data,
              additional_padding):

    return ''.join(chr((ord(symbol) - padding - (i+additional_padding)) % 1114112) for i, symbol in enumerate(data, start=1))

def encrypt(message, key="Default", padding=2, additional_padding=16):
    chiper_aoe = Sanskrit()
    obj_chiper = chiper_aoe.зашифровать(key=key, data=message)
    chipred_cesar = chiper_aoe.b62_encrypt(padding=padding, data=obj_chiper, additional_padding=additional_padding)
    obj_chiper_cesar = chiper_aoe.зашифровать(key=key, data=chipred_cesar)
    chipred_cesar_mega = chiper_aoe.b62_encrypt(padding=padding, data=obj_chiper_cesar, additional_padding=additional_padding)
    return base64.b64encode(chipred_cesar_mega.encode()).decode('latin-1')

def decrypt(message, key="Default", padding=2, additional_padding=16):
    chiper_aoe = Sanskrit()
    obj_chiper = chiper_aoe.b62_decrypt(padding=padding, data=message, additional_padding=additional_padding)
    obj_grotted = obj_chiper.split("GroTTesqueinmyheart")
    chipred_cesar = chiper_aoe.расшифровать(obj_grotted[0].encode('latin-1'),obj_grotted[1].encode('latin-1'),
                                      obj_grotted[2].encode('latin-1'),obj_grotted[3].encode('latin-1'))
    obj_chiper = chiper_aoe.b62_decrypt(padding=padding, data=chipred_cesar, additional_padding=additional_padding)
    obj_grotted = obj_chiper.split("GroTTesqueinmyheart")
    chipred_cesar = chiper_aoe.расшифровать(obj_grotted[0].encode('latin-1'),obj_grotted[1].encode('latin-1'),
                                      obj_grotted[2].encode('latin-1'),obj_grotted[3].encode('latin-1'))
    return base64.b64encode(chipred_cesar.encode()).decode('latin-1')

def test(message, key, padding, additional_padding):
    chiper_aoe = Sanskrit()
    start = time.time()
    obj_chiper = chiper_aoe.зашифровать(key=key, data=message)
    #print(obj_chiper)

    chipred_cesar = chiper_aoe.b62_encrypt(padding=padding, data=obj_chiper, additional_padding=additional_padding)
    obj_chiper_cesar = chiper_aoe.зашифровать(key=key, data=chipred_cesar)
    chipred_cesar_mega = chiper_aoe.b62_encrypt(padding=padding, data=obj_chiper_cesar, additional_padding=additional_padding)


    #print('Chiper estimed: ', time.time()-start, len(message))

    start = time.time()
    obj_chiper = chiper_aoe.b62_decrypt(padding=padding, data=chipred_cesar_mega, additional_padding=additional_padding)
    obj_grotted = obj_chiper.split("GroTTesqueinmyheart")
    chipred_cesar = chiper_aoe.расшифровать(obj_grotted[0].encode('latin-1'),obj_grotted[1].encode('latin-1'),
                                      obj_grotted[2].encode('latin-1'),obj_grotted[3].encode('latin-1'))
    
    obj_chiper = chiper_aoe.b62_decrypt(padding=padding, data=chipred_cesar, additional_padding=additional_padding)
    obj_grotted = obj_chiper.split("GroTTesqueinmyheart")
    chipred_cesar = chiper_aoe.расшифровать(obj_grotted[0].encode('latin-1'),obj_grotted[1].encode('latin-1'),
                                      obj_grotted[2].encode('latin-1'),obj_grotted[3].encode('latin-1'))

    b64_ultra = base64.b64encode(chipred_cesar_mega.encode()).decode('latin-1')
    print(chipred_cesar) # - это итоговый результат шифрования

#test("", "123456", 69, 3) #



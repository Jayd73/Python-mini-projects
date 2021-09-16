import math

class Cipher:
    CHARACTER_SET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ENCRYPT = 1
    DECRYPT = -1
    def __init__ (self, key):
        self.key = key

    def encrypt(self, message):
        return 

    def decrypt(self, message):
        return


class ShiftCipher (Cipher):
    def __init__ (self, key):
        super().__init__(key)

    def _convert(self, message, shift_direc = 0):
        message = message.upper()

        converted_message = ''
        for character in message:
            if character in Cipher.CHARACTER_SET:
                char_ind = (Cipher.CHARACTER_SET.find(character) + self.key * shift_direc) % len(Cipher.CHARACTER_SET)
                converted_message += Cipher.CHARACTER_SET[char_ind]
            else:
                converted_message += character
        return converted_message

    def encrypt(self, message):
        return self._convert(message, shift_direc = Cipher.ENCRYPT)

    def decrypt(self, message):
        return self._convert(message, shift_direc = Cipher.DECRYPT)


class VigenereCipher (Cipher):
    def __init__ (self, key):
        super().__init__(key)
        self.key = self.key.upper()

    def _convert(self, message, operation_val = 0):
        message = message.upper()
        converted_message = ''
        i = 0
        for character in message:
            if character in Cipher.CHARACTER_SET:
                row = Cipher.CHARACTER_SET.find(self.key[i])
                colm = Cipher.CHARACTER_SET.find(character)
                converted_message += Cipher.CHARACTER_SET[(colm + row * operation_val) % 26]
                i %= len(self.key)
            else:
                converted_message += character
        return converted_message

    def encrypt(self, message):
        return self._convert(message, operation_val = Cipher.ENCRYPT)

    def decrypt(self, message):
        return self._convert(message, operation_val = Cipher.DECRYPT)


# chars other than alphabets are lost in encryption, in this implementation
class PlayfairCipher (Cipher):
    GRID_SIZE = 5
    FILLING_LETTER = 'X'
    OMITTED_LETTER = 'J'
    REPLACING_LETTER = 'I'

    def __init__(self, key):
        super().__init__(key)
        self.key = self.key.upper()
        self.key.replace(PlayfairCipher.OMITTED_LETTER, PlayfairCipher.REPLACING_LETTER)
        self.key = ''.join(dict.fromkeys(self.key))
        intermediate_str = self.key + Cipher.CHARACTER_SET.replace(PlayfairCipher.OMITTED_LETTER, '')
        self.grid_str = ''.join(dict.fromkeys(intermediate_str))

    def _get_pos_in_grid(self, character):
        row = self.grid_str.find(character) // PlayfairCipher.GRID_SIZE
        colm = self.grid_str.find(character) % PlayfairCipher.GRID_SIZE
        return (row, colm)

    def _get_char_in_grid_at(self, row, colm):
        return self.grid_str[row * PlayfairCipher.GRID_SIZE + colm]

    def _convert(self, message, operation_val):
        message = ''.join(filter(lambda x: x.isalpha(), message))
        message = message.upper()
        message = message.replace(PlayfairCipher.OMITTED_LETTER, PlayfairCipher.REPLACING_LETTER)

        if operation_val == Cipher.ENCRYPT:
            ind = 0
            while ind < len(message)-len(message)%2 :
                if message[ind] == message[ind+1]:
                    message = message[:ind+1] + PlayfairCipher.FILLING_LETTER + message[ind+1:]
                ind+=2
            if len(message) % 2 != 0:
                message += 'X'

        converted_message = ''
        for i in range(0,len(message),2):
            char1 = message[i]
            char2 = message[i+1]
            pos1 = self._get_pos_in_grid(char1)
            pos2 = self._get_pos_in_grid(char2)

            if pos1[0] == pos2[0]:
                r_char1 = self._get_char_in_grid_at(pos1[0], (pos1[1] + operation_val) % PlayfairCipher.GRID_SIZE)  
                r_char2 = self._get_char_in_grid_at(pos2[0], (pos2[1] + operation_val) % PlayfairCipher.GRID_SIZE)  
            elif pos1[1] == pos2[1]:
                r_char1 = self._get_char_in_grid_at((pos1[0] + operation_val) % PlayfairCipher.GRID_SIZE, pos1[1])  
                r_char2 = self._get_char_in_grid_at((pos2[0] + operation_val) % PlayfairCipher.GRID_SIZE, pos2[1]) 
            else:
                r_char1 = self._get_char_in_grid_at(pos1[0], pos2[1])
                r_char2 = self._get_char_in_grid_at(pos2[0], pos1[1])

            converted_message += r_char1 + r_char2
        return converted_message

    def encrypt(self, message):
        return self._convert(message, operation_val = Cipher.ENCRYPT)

    def decrypt(self, message):
        return self._convert(message, operation_val = Cipher.DECRYPT)


class ColumnarTranspositionCipher:
    FILLING_LETTER = 'X'

    def __init__(self, key):
        self.key = key.upper()
        self.key = ''.join(dict.fromkeys(self.key))
        self.colms = len(self.key)

    def encrypt(self, message):
        # message = message.replace(" ","")             #If u don't want spaces.
        # message = message.upper()      
        rows = int(math.ceil(len(message) / self.colms))
        message += ColumnarTranspositionCipher.FILLING_LETTER * (rows * self.colms - len(message))
        converted_message = ''

        for key_char in sorted(self.key):
            colm_num = self.key.index(key_char)
            converted_message += ''.join([message[r * self.colms + colm_num] for r in range(rows)])

        return converted_message

    def decrypt(self, message):
        decrypted_msg = list(message)
        rows = int(math.ceil(len(message) / self.colms))

        for i, key_char in enumerate(sorted(self.key)):
            colm_num = self.key.index(key_char)
            for r in range(rows):
                decrypted_msg[r * self.colms + colm_num] = message[i * rows + r]
            
        return ''.join(decrypted_msg)


class RailFenceCipher:
    def __init__(self, key):
        self.key = key

    def _convert(self, message):
        converted_message = [None]*len(message)
        cipher_ind = 0
        for rail_num in range(self.key):
            letter_ind = rail_num
            while letter_ind < len(message):
                converted_message[cipher_ind] = message[letter_ind]
                cipher_ind += 1
                rail_reflection = self.key - rail_num - 1
                # wraps back to max offset if rail reflection is 0
                rail_reflection = (rail_reflection - 1) % (self.key - 1) + 1
                letter_ind += 2 * rail_reflection   
                rail_num = rail_reflection
        return ''.join(converted_message)

    # def wrap_between(lower, upper, val):    #both inclusive
    #     return (val - lower)%(upper - lower + 1) + lower

    def encrypt(self, message):
        return self._convert(message)

    def decrypt(self, message):
        converted_message = [None]*len(message)
        cipher_ind = 0
        for rail_num in range(self.key):
            letter_ind = rail_num
            while letter_ind < len(message):
                converted_message[letter_ind] = message[cipher_ind]
                cipher_ind += 1
                rail_reflection = self.key - rail_num - 1
                # wraps back to max offset if rail reflection is 0
                rail_reflection = (rail_reflection - 1) % (self.key - 1) + 1
                letter_ind += 2 * rail_reflection   
                rail_num = rail_reflection
        return ''.join(converted_message)



if __name__ == "__main__":
    m = "Apple a day keeps doctor away"
    print("\n-----SHIFT CIPHER-----")
    shiftCipher = ShiftCipher(key = 3)
    e_m = shiftCipher.encrypt(m)
    print("\nEncrypted message:")
    print(e_m)
    print("\nDecrypted message: ")
    print(shiftCipher.decrypt(e_m))

    print("\n-----VIGENERE CIPHER-----")
    vigenereCipher = VigenereCipher(key = "POSSOM")
    e_m = vigenereCipher.encrypt(m)
    print("\nEncrypted message:")
    print(e_m)
    print("\nDecrypted message: ")
    print(vigenereCipher.decrypt(e_m))
    print()

    print("\n-----PLAYFAIR CIPHER-----")
    playfairCipher = PlayfairCipher(key = "MONARCHY")
    e_m = playfairCipher.encrypt(m)
    print("\nEncrypted message:")
    print(e_m)
    print("\nDecrypted message: ")
    print(playfairCipher.decrypt(e_m))
    print()

    print("\n-----COLUMNAR TRANSPOSITION CIPHER-----")
    colmCipher = ColumnarTranspositionCipher(key = "MONARCHY")
    e_m = colmCipher.encrypt(m)
    print("\nEncrypted message:")
    print(e_m)
    print("\nDecrypted message: ")
    print(colmCipher.decrypt(e_m))
    print()

    print("\n-----RAIL FENCE TRANSPOSITION CIPHER-----")
    railFenceCipher = RailFenceCipher(key = 3)
    e_m = railFenceCipher.encrypt(m)
    print("\nEncrypted message:")
    print(e_m)
    print("\nDecrypted message: ")
    print(railFenceCipher.decrypt(e_m))
    print()

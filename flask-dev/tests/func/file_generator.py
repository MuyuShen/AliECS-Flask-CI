import random
import string
import oss2

def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))

def random_file(n):
    filename = random_string(32) + '.txt'
    content = oss2.to_bytes(random_string(1024 * 1024))

    with open(filename, 'wb') as fileobj:
        fileobj.write(content)
    
    return filename
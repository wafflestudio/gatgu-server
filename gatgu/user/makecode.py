import random
import string


def generate_code():

    code_length = 6

    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(code_length))

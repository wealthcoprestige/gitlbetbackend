import random 

def get_random_nums(length: int) -> int:
    start = "0" * (length - 1)
    end = "9" * length
    return random.randint(int(f"1{start}"), int(end))
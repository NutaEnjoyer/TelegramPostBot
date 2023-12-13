import random
import time

def generate_hacker_text():
    hacker_text = ""
    for _ in range(150):
        hacker_text += chr(random.randint(32, 127))
    return hacker_text + '  ' + str(random.randint(100, 999))

while True:
    print(generate_hacker_text())
    time.sleep(1)
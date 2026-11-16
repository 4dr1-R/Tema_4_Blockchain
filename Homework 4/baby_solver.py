
import socket
import hashlib
import itertools
import string
import re

HOST = "202.61.227.83"
PORT = 31337

HASHES = {
    "sha256": hashlib.sha256,
    "md5": hashlib.md5,
    "keccak": hashlib.sha3_256
}

ALPHABET = string.ascii_letters + string.digits

def solve(challenge):
    match = re.search(
        r'(\w+)\(xxxx \+ (.*)\) == ([0-9a-f]+)',
        challenge
    )

    if not match:
        raise ValueError("invalid challenge: " + challenge)

    algorithm, suffix, target = match.groups()
    prefix_len = 20 - len(suffix)
    hash_function = HASHES[algorithm]

    # prefixul nu poate contine caractere din sufix deoarece sirul initial este generat cu random.sample.
    alphabet = [c for c in ALPHABET if c not in suffix]

    for candidate in itertools.permutations(alphabet, prefix_len):
        prefix = ''.join(candidate)
        value = hash_function(
            (prefix + suffix).encode()
        ).hexdigest()

        if value == target:
            return prefix

    raise ValueError("Can't find prefix.")



def read_challenge(f):
    while True:
        line = f.readline()

        if not line:
            raise ConnectionError("Server disconnected.")

        line = line.decode().strip()

        if " == " in line and "(" in line:
            return line

        print("[SERVER]", line)

def main():
    with socket.create_connection((HOST, PORT)) as sock:
        f = sock.makefile("rwb")

        for i in range(15):
            challenge = read_challenge(f)

            print(f"\n[{i+1}/15] {challenge}")

            answer = solve(challenge)

            print("Answer:", answer)

            f.write((answer + "\n").encode())
            f.flush()

        while True:
            line = f.readline()
            if not line:
                break
            print(line.decode(), end="")

if __name__ == "__main__":
    main()



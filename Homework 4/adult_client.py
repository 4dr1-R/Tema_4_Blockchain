

import socket
import subprocess
import os
import re

HOST = "202.61.227.83"
PORT = 31338

def main():
    solver_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Tema 4 blockchain/adult_solver.exe"
    )

    with socket.create_connection((HOST, PORT), timeout=180) as sock:
        sock.settimeout(180)
        f = sock.makefile("rwb", buffering=0)

        for round_num in range(1, 6):
            print(f"\n=== ROUND {round_num}/5 ===")

            # citeste pana gaseste provocarea SHA256
            while True:
                line = f.readline().decode().strip()

                if not line:
                    raise RuntimeError("Server disconnected")

                print("[SERVER]", line)

                if "sha256(xxxx)" in line:
                    break

            # citeste prompt
            prompt = f.readline().decode().strip()
            print("[SERVER]", prompt)

            match = re.search(r'== ([a-f0-9]{64})', line)

            if not match:
                raise RuntimeError("Invalid challenge: " + line)

            target = match.group(1)

            print("[*] Starting C++ solver...")

            result = subprocess.run(
                [solver_path, target],
                capture_output=True,
                text=True,
                timeout=150
            )

            if result.returncode != 0:
                print(result.stderr)
                raise RuntimeError("Solver failed")

            answer = result.stdout.strip().splitlines()[-1]

            print("[+] Found:", answer)

            f.write(answer.encode() + b"\n")

        print("\n[+] FINAL SERVER RESPONSE:")
        print(f.read().decode(errors="replace"))

if __name__ == "__main__":
    main()

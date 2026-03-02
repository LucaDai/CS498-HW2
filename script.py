import time
import requests
from statistics import mean

IP_A = "34.123.62.170"
IP_B = "34.76.94.107"
N_LAT = 10
N_CONS = 100
TIMEOUT = 10

def measure_get(base_url: str, path: str, n: int = N_LAT):
    latencies = []
    for _ in range(n):
        start = time.perf_counter()
        r = requests.get(f"{base_url}{path}", timeout=TIMEOUT)
        end = time.perf_counter()

        r.raise_for_status()
        latencies.append((end - start) * 1000)

    return latencies

def measure_register(base_url: str, n: int = N_LAT):
    latencies = []
    for i in range(n):
        username = f"user_{int(time.time()*1000)}_{i}"

        start = time.perf_counter()
        r = requests.post(f"{base_url}/register",json={"username": username},timeout=TIMEOUT)
        end = time.perf_counter()

        r.raise_for_status()
        latencies.append((end - start) * 1000)
    return latencies


def measure_consistency(write_url: str, read_url: str, iterations: int = N_CONS):
    miss_count = 0
    for i in range(iterations):
        username = f"user_{i}_{int(time.time()*1000)}"
        requests.post(f"{write_url}/register", json={"username": username}, timeout=TIMEOUT,).raise_for_status()

        users = requests.get(f"{read_url}/list", timeout=TIMEOUT,).json().get("users", [])
        if username not in users:
            miss_count += 1

    return miss_count

def clear_both(A: str, B: str):
    requests.post(f"{A}/clear", timeout=TIMEOUT)
    requests.post(f"{B}/clear", timeout=TIMEOUT)

def main():
    A = f"http://{IP_A}:8080"
    B = f"http://{IP_B}:8080"

    # Latency
    clear_both(A, B)
    print("===== Measure Latency =====")

    regA = measure_register(A)
    regB = measure_register(B)
    listA = measure_get(A, "/list")
    listB = measure_get(B, "/list")

    print(f"IP A register average latency: {mean(regA):.2f} ms")
    print(f"IP B register average latency: {mean(regB):.2f} ms")
    print(f"IP A list average latency: {mean(listA):.2f} ms")
    print(f"IP B list average latency: {mean(listB):.2f} ms")

    # Consistency
    print("===== Measure Consistency =====")

    clear_both(A, B)
    miss_count = measure_consistency(write_url=A, read_url=B)
    print(f"Misses: {miss_count} / {N_CONS}")

main()
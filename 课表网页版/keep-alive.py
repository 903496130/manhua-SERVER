import requests
import time


if __name__ == "__main__":
    while True:
        time.sleep(10000)
        req = requests.get("http://jwgl.bistu.edu.cn")
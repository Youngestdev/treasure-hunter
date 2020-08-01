import json
import requests
import time
import random
import websocket
import re
from multiprocessing.pool import ThreadPool as Pool
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# It won't be bad to gossip y'know.

ws = websocket.WebSocket()
ws.connect('wss://findtreasure.app/api/v1/games/test/ws')

websocket.enableTrace(True)
name = ["Abdulazeez Abdulazeez Adeshina"]


def OtherUserNodes():
    res = f"{ws.recv()}"
    if len(res) < 100:
        pass
    elif name[0] in res:
        pass
    else:
        x = re.findall("\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", res)
        connectedNodes = x[2:-1]
        visited = x[-1]
        seen.add(visited)
        return connectedNodes


headers = {'gomoney': '09058640120',
           'Authorization': 'Bearer <TOKEN>'}

seen = set()

"""
Retry strategy.
Kicks off after getting a response with status in `status_forcelist` instead of dieing down.
"""
retry_strategy = Retry(
    total=1000,  # Increase.
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["GET"],
    backoff_factor=1
)

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)


# Miscellaneous pool worker file. Actually, isn't this a repetition? Wellll.. Idk.
def worker(item):
    try:
        FindTreasure(item)
    except ConnectionError:
        print("Lobatan")


def FindTreasure(node):
    toVisit = OtherUserNodes()
    url = "https://findtreasure.app/api/v1/games/test/{}".format(node)
    seen.add(node)

    nodes = []

    response = http.get(url, headers=headers).json()
    paths = response['paths']

    for path in paths:
        if path not in nodes:
            nodes.append(path[43:])

    if 'start' in nodes:
        nodes.remove('start')

    random.shuffle(nodes)  # Shuffle the nodes.

    pool = Pool()
    nodes = [node for node in nodes if node not in seen]

    if toVisit is not None:
        toVisit = [node for node in toVisit if
                   node not in seen and node not in nodes]  # If we've seen it previously, don't add it.
        nodes.extend(toVisit)
    print("Visited nodes: ", toVisit, nodes, seen)

    pool.imap_unordered(worker, nodes)

    pool.close()
    pool.join()
    return print("One path down.", len(seen))


if __name__ == '__main__':
    try:
        begin = time.perf_counter()
        FindTreasure("start")
        end = time.perf_counter()
        print(f"Treasure found in {end - begin:0.4f} seconds", len(seen))

    except ConnectionError:
        last = seen.pop()
        FindTreasure(last)
        print("There was a connection error, we're starting back from node: ", last)

    except json.decoder.JSONDecodeError:
        print("Shutting down gracefully")

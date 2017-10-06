#!/usr/bin/env python3

import robomodules
import os

ADDRESS = os.environ.get("BIND_ADDRESS","localhost")
PORT = os.environ.get("BIND_PORT", 11297)

def main():
    server = robomodules.Server(ADDRESS, PORT)
    server.run()

if __name__ == "__main__":
    main()

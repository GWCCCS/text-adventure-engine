# dep

import os

from adventure import Adventure


# const

ADVENTURES_DIR = "adventures"


# util

def choose_file(path: str) -> str:
    try:
        filenames = os.listdir(path)
    except FileNotFoundError:
        path = f"../{path}" # fix for /src/ path issues
        filenames = os.listdir(path)
    filenames = [ f for f in filenames if f.endswith(".json") ]
    print("Choose a file:")
    for i, f in enumerate(filenames): print(f"{i+1}. {f}")
    while True:
        user_input = input("> ")
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(filenames):
                return f"{path}/{filenames[idx]}"
        except ValueError: pass


# main

def main():
    filename = choose_file(ADVENTURES_DIR)
    print("\n\n***\n\n")
    adventure = Adventure(filename)
    while True:
        adventure.begin()

if __name__ == '__main__':
    print("\n" * 2)
    main()

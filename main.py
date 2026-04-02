# dep

import json


# const

ADVENTURE_FILENAME = "adventure.json"


# util

def load_json(filename: str):
    file = open(filename)
    file_str = "".join(file.readlines())
    file.close()
    return json.loads(file_str)

def ask_user(choices: list[str]) -> int:
    print("What do you want to do?")
    for i, choice in enumerate(choices):
        print(f"{i+1}. {choice}")

    while True:
        choice_str = input("> ")
        if choice_str in choices:
            return choices.index(choice_str)
        try:
            choice_idx = int(choice_str)
            if 1 <= choice_idx <= len(choices):
                return choice_idx-1
        except ValueError:
            pass

# game

def game(adventure):
    context = "\n".join(adventure["context"])
    choices = adventure["choices"]

    print(f"\n{context}\n")
    choice_idx = ask_user(choices)

    print(f"\nYou chose: {choices[choice_idx]}")


# main

if __name__ == '__main__':
    adventure = load_json(ADVENTURE_FILENAME)
    game(adventure)
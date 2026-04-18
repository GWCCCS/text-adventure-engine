# dep

from __future__ import annotations # fix class/staticmethod return type hints

from typing import Any

import json


# const

F_RESET     = "\033[0m"
F_BOLD      = "\033[1m"
F_ITALIC    = "\033[3m"
F_UNDERLINE = "\033[4m"

BOX_CHARS_DEFAULT = "─│╭╮╰╯"


# util

def load_json(filename: str) -> Any:
    file = open(filename)
    file_str = "".join(file.readlines())
    file.close()
    return json.loads(file_str)

def str_list(arg: str|list[str]) -> list[str]:
    if isinstance(arg, str): return [arg]
    return arg

def box_text(
        text:  str,
        chars: str = BOX_CHARS_DEFAULT
) -> str|None:
    if len(chars) != 6: return None # err
    c_hori, c_vert, c_tl, c_tr, c_bl, c_br = chars

    lines = (
        text.strip()
        .replace("\t", " ")
        .replace("\r", "")
        .split("\n")
    )
    max_len = max([len(line) for line in lines])

    top_line = c_tl + (c_hori * (max_len + 2)) + c_tr
    bot_line = c_bl + (c_hori * (max_len + 2)) + c_br

    return "\n".join([
        top_line,
        *[f"{c_vert} {line.ljust(max_len)} {c_vert}" for line in lines],
        bot_line,
    ])

def print_spacer() -> None:
    print("\n\n***\n\n")

def print_title(
        title: str,
        title_chars: str,
        subtitle: str|None,
        prompt: str
) -> None:
    title = f"{box_text(title, title_chars)}\n\n"
    subtitle = f"{subtitle}\n\n" if subtitle not in (None, "") else ""

    input(
        f"{F_BOLD}{title}{F_RESET}"
        f"{F_ITALIC}{subtitle}{F_RESET}"
        f"{F_BOLD}{prompt}{F_RESET}"
    )

def print_context(context: str|list[str]) -> None:
    context = str_list(context)
    print(f"{F_ITALIC}{"\n".join(context)}{F_RESET}")

def print_directive(directive: str|list[str]) -> None:
    directive = str_list(directive)
    print(f"{F_BOLD}{"\n".join(directive)}{F_RESET}")

def print_list(items: list[str]) -> None:
    i_just = len(f"{len(items)}")
    for i, item in enumerate(items):
        i_str = f"{i+1}.".ljust(i_just+1)
        print(f"{i_str} {item}")

def prompt_list(items: list[str], prompt: str) -> int:
    print_directive(f"{prompt}\n")
    print_list(items)
    while True:
        user_input = input("> ")
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(items):
                return idx
        except ValueError:
            pass


# main

class Adventure:
    # const

    KEY_MAIN_DEFAULT  = "__main__"
    KEY_META_DEFAULT  = "__meta__"

    META_DEFAULT = {
        "title":        "My Text Adventure",
        "title_chars":  BOX_CHARS_DEFAULT,
        "subtitle":     "So Textual, So Adventurous",

        "prompt_start": "Press enter to begin...",
        "prompt_end":   "Press enter to end...",

        "the_end": "The End"
    }

    SCENARIO_DEFAULT = {
        "context": "...",
        "prompt":  "What do you do?",
        # "choices": []
    }

    SCENARIO_KEY_DEFAULT = "_"

    # constr

    def __init__(
            self,
            adventure_json: str,
            key_meta: str = "__meta__",
            key_main: str = "__main__"
    ):
        json_data       = load_json(adventure_json)
        self._METADATA  = Adventure._parse_metadata (json_data.get(key_meta, {}))
        self._SCENARIOS = Adventure._parse_scenarios(json_data[key_main])
        self._flags     = set()

    # main

    def begin(
            self,
            scenario_key: str = SCENARIO_KEY_DEFAULT
    ):
        self.title_screen()
        print_spacer()
        while scenario_key is not None:
            scenario_key = self.do_scenario(scenario_key)
            print()
        self.end_screen()

    def title_screen(self):
        meta = self._METADATA
        print_title(
            meta["title"],
            meta["title_chars"],
            meta["subtitle"],
            meta["prompt_start"]
        )

    def end_screen(self):
        meta = self._METADATA
        print_title(
            meta["the_end"],
            meta["title_chars"],
            None,
            meta["prompt_end"]
        )

    def do_scenario(
            self,
            scenario_key: str
    ) -> str|None:
        scenario = self._SCENARIOS[scenario_key]
        choice = scenario.prompt_choices(self._flags)
        if choice is None:
            return None
        return choice.choose(self._flags)

    # scenario (list of choices)

    class Scenario:
        # constr

        def __init__(
                self,
                raw: dict[str, dict[str, Any]]
        ):
            self._context = str_list(
                raw.get("context", Adventure.SCENARIO_DEFAULT["context"])
            )
            self._prompt = (
                raw.get("prompt", Adventure.SCENARIO_DEFAULT["prompt"])
            )
            self._all_choices = self._parse_scenario(
                raw.get("choices", [])
            )

        # method

        def prompt_choices(
                self,
                flags: set[str]
        ) -> Choice|None:
            valid_choices = self._get_valid_choices(self._all_choices, flags)
            print_context(self._context)
            print()
            if len(valid_choices) == 0:
                return None # no options
            idx = prompt_list(
                [ choice.text for choice in valid_choices ],
                self._prompt
            )
            return valid_choices[idx]

        # util

        @classmethod
        def _parse_scenario(
                cls,
                choices_raw: list[dict[str, Any]]
        ) -> list[Choice]:
            return [
                cls.Choice(choice_raw) for choice_raw in choices_raw
            ]

        @classmethod
        def _get_valid_choices(
                cls,
                all_choices: list[Choice],
                flags: set[str]
        ) -> list[Choice]:
            return [
                choice for choice in all_choices if choice.is_valid(flags)
            ]

        # choice (one option w/ flag params)

        class Choice:
            # constr

            def __init__(
                    self,
                    raw: dict[str, Any]
            ) -> None:
                self._text        =          raw.get("text"           ) # err if no text
                self._follow_up   = str_list(raw.get("follow_up", None))
                self._show_condit =          raw.get("show_if",   None)
                self._hide_condit =          raw.get("hide_if",   None)

                self._on_select: dict[str, list[str]] = {
                    "set":   str_list(raw.get("on_select", {}).get("set",   [])), # wrap into list
                    "clear": str_list(raw.get("on_select", {}).get("clear", []))  # ...
                }
                self._next_scenario_key = raw["next"]

            # prop

            @property
            def text(self):
                return self._text

            @property
            def next_scenario_key(self):
                return self._next_scenario_key

            # method

            def is_valid(self, flags: set[str]):
                show_ignore = self._show_condit is None
                hide_ignore = self._hide_condit is None

                should_show = show_ignore       or  (self._show_condit in flags) # or
                should_hide = (not hide_ignore) and (self._hide_condit in flags) # or (overrides show)

                return should_show and not should_hide

            def choose(self, flags: set[str]) -> str:
                for f in self._on_select["set"]:
                    flags.add(f) # mut
                for f in self._on_select["clear"]:
                    flags.remove(f) # mut

                if self._follow_up not in ("", None):
                    print_context(f"\n{"\n".join(self._follow_up)}")

                return self._next_scenario_key

    # prot util

    @classmethod
    def _parse_metadata(
            cls,
            raw: dict[str, str]
    ) -> dict[str, str]:
        return {
            k: raw.get(k, cls.META_DEFAULT[k])
            for k in cls.META_DEFAULT.keys()
        }

    @classmethod
    def _parse_scenarios(
            cls,
            raw: dict[str, Any]
    ) -> dict[str, Scenario]:
        return {
            k: cls.Scenario(v)
            for k, v in raw.items()
        }
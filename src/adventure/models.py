# dep

from __future__ import annotations # fix class/staticmethod return type hints

from typing import Any

from .util import Cli, Util


# main

class Adventure:
    # const

    KEY_MAIN_DEFAULT  = "__main__"
    KEY_META_DEFAULT  = "__meta__"

    META_DEFAULT = {
        "title":        "My Text Adventure",
        "title_chars":  None,
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
        json_data       = Util.load_json(adventure_json)
        self._METADATA  = Adventure._parse_metadata (json_data.get(key_meta, {}))
        self._SCENARIOS = Adventure._parse_scenarios(json_data[key_main])
        self._flags     = set()

    # main

    def begin(
            self,
            scenario_key: str = SCENARIO_KEY_DEFAULT
    ):
        self.title_screen()
        Cli.print_spacer()
        while scenario_key is not None:
            print()
            scenario_key = self.do_scenario(scenario_key)
        self.end_screen()

    def title_screen(self):
        meta = self._METADATA
        Cli.print_title(
            meta["title"],
            meta["title_chars"],
            meta["subtitle"],
            meta["prompt_start"]
        )

    def end_screen(self):
        meta = self._METADATA
        Cli.print_title(
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
            self._context = Util.str_list(
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
            Cli.print_context(self._context)
            print()
            if len(valid_choices) == 0:
                return None # no options
            idx = Cli.prompt_list(
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
                self._text        = raw.get("text"         ) # err if no text
                self._show_condit = raw.get("show_if", None)
                self._hide_condit = raw.get("hide_if", None)

                self._follow_up = Util.str_list(raw.get("follow_up", None))

                self._on_select: dict[str, list[str]] = {
                    "set":   Util.str_list(raw.get("on_select", {}).get("set",   [])), # wrap into list
                    "clear": Util.str_list(raw.get("on_select", {}).get("clear", []))  # ...
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
                    Cli.print_context(f"\n{"\n".join(self._follow_up)}")

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
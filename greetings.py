"""Generate playful greeting styles for the hello-world project."""
from __future__ import annotations

import random
from textwrap import dedent


def emoji_blast(name: str) -> str:
    return dedent(
        f"""
        🎉🎉🎉  嘿，{name}！  🎉🎉🎉
        送你一整串的笑脸和好心情，願你今天像這些彩帶一樣繽紛！
        """
    ).strip()


def neon_marquee(name: str) -> str:
    lines = [
        "┏━━━━━━━━━━━━━━━━━━━━━━┓",
        f"┃   WELCOME, {name.upper():^10}   ┃",
        "┃  ✨ 線上霓虹燈為你閃耀 ✨  ┃",
        "┗━━━━━━━━━━━━━━━━━━━━━━┛",
    ]
    return "\n".join(lines)


def multilingual_wave(name: str) -> str:
    greetings = [
        "Hola",
        "Bonjour",
        "こんにちは",
        "안녕하세요",
        "مرحبا",
        "Hallo",
        "Γεια σου",
    ]
    joined = "、".join(greetings)
    return f"{joined}，{name}！世界都在向你招手～"


def ascii_postcard(name: str) -> str:
    art = dedent(
        r"""
         ~~~~~~~~~~~~~~~~~~~~~~~~~
         |        \ | /          |
         |         .-.           |
         |      '-(   )-'        |
         |         `-'           |
         |  來自雲端的明信片 ✈️ |
         ~~~~~~~~~~~~~~~~~~~~~~~~~
        """
    ).strip("\n")
    return f"{art}\n親愛的 {name}，這是送給你的數位問候明信片！"


def chiptune_intro(name: str) -> str:
    notes = "♪ ♫ ♬"
    return (
        f"{notes} 嘟嘟嘟！8-bit 開場響起，{name} 正在登入快樂模式！ {notes}"
    )


def random_greeting(name: str = "朋友") -> str:
    styles = [
        emoji_blast,
        neon_marquee,
        multilingual_wave,
        ascii_postcard,
        chiptune_intro,
    ]
    return random.choice(styles)(name)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Print a playful greeting")
    parser.add_argument("name", nargs="?", default="朋友", help="Name to greet")
    parser.add_argument(
        "--random",
        action="store_true",
        help="Always choose a random style (default is the same as without the flag)",
    )
    parser.add_argument(
        "--style",
        choices=["emoji", "neon", "polyglot", "postcard", "chiptune"],
        help="Select a specific greeting style",
    )

    args = parser.parse_args()

    style_map = {
        "emoji": emoji_blast,
        "neon": neon_marquee,
        "polyglot": multilingual_wave,
        "postcard": ascii_postcard,
        "chiptune": chiptune_intro,
    }

    if args.style:
        greeting = style_map[args.style](args.name)
    elif args.random:
        greeting = random_greeting(args.name)
    else:
        greeting = random_greeting(args.name)

    print(greeting)


if __name__ == "__main__":
    main()

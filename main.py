"""보드게임 (오목, 체스). 실행: python main.py"""
import pygame

import chess_game
import gomoku
from common import BG, H, W, button, settings, t, text


def menu_rows():
    """(제목, 설정 키, [(값, 글자), ...]) 목록. 지금 선택에 따라 줄이 바뀐다."""
    is_gomoku = settings["game"] == "gomoku"
    rows = [
        ("game", "game", [("gomoku", t("gomoku")), ("chess", t("chess"))]),
        ("opponent", "vs_ai", [(False, t("friend")), (True, t("computer"))]),
    ]
    if settings["vs_ai"]:
        levels = ["easy", "normal", "hard"] if is_gomoku else ["beginner", "normal", "hard", "expert"]
        rows.append(("level", "level", [(i, t(k)) for i, k in enumerate(levels)]))
        first, second = ("black_first", "white_second") if is_gomoku else ("white_first", "black_second")
        rows.append(("my_side", "human_first", [(True, t(first)), (False, t(second))]))
    if is_gomoku:
        rows.append(("rule33", "forbid33", [(False, t("off")), (True, t("on"))]))
        rows.append(("overline", "exact5", [(False, t("win")), (True, t("nowin"))]))
    rows.append(("language", "lang", [("ko", "한국어"), ("en", "English")]))
    return rows


def menu(screen, clock):
    warning = ""
    while True:
        rows = menu_rows()
        level_row = next((r for r in rows if r[1] == "level"), None)
        if level_row and settings["level"] >= len(level_row[2]):
            settings["level"] = len(level_row[2]) - 1

        screen.fill(BG)
        text(screen, t("title"), (W // 2, 50), 40, center=True)
        clickable = []
        y = 105
        for label, key, options in rows:
            text(screen, t(label), (60, y + 10), 24)
            for i, (value, name) in enumerate(options):
                r = button(screen, (250 + i * 152, y, 140, 46), name, settings[key] == value, 20)
                clickable.append((r, key, value))
            y += 64
        start = button(screen, (W // 2 - 110, H - 72, 220, 58), t("start"), True, 26)
        if warning:
            text(screen, warning, (W // 2, H - 92), 20, (200, 30, 30), center=True)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                warning = ""
                for r, key, value in clickable:
                    if r.collidepoint(e.pos):
                        settings[key] = value
                if start.collidepoint(e.pos):
                    if settings["game"] == "chess" and settings["vs_ai"] and not chess_game.engine_ready():
                        warning = t("no_engine")
                    else:
                        return "start"
        clock.tick(30)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Board Games")
    clock = pygame.time.Clock()
    while menu(screen, clock) == "start":
        game = gomoku if settings["game"] == "gomoku" else chess_game
        if game.run(screen, clock) == "quit":
            break
    pygame.quit()


if __name__ == "__main__":
    main()

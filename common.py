"""화면, 글자, 버튼처럼 두 게임이 같이 쓰는 것들."""
import sys
from pathlib import Path

import pygame

W, H = 900, 660
BG = (238, 228, 210)
INK = (40, 40, 40)
ACCENT = (70, 120, 200)
PANEL_X = 660

# 실행 파일(exe)로 묶였을 때는 exe 옆 폴더, 아니면 소스 폴더
BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent

settings = dict(
    lang="ko",
    game="gomoku",
    vs_ai=True,
    level=1,
    human_first=True,
    forbid33=False,   # 쌍삼 금지 (기본: 끔)
    exact5=False,     # True면 6목 이상은 승리 아님
)

TEXT = {
    "title": ("보드게임", "Board Games"),
    "game": ("게임", "Game"),
    "gomoku": ("오목", "Gomoku"),
    "chess": ("체스", "Chess"),
    "opponent": ("상대", "Opponent"),
    "friend": ("친구 (2인)", "Friend (2P)"),
    "computer": ("컴퓨터", "Computer"),
    "level": ("난이도", "Level"),
    "easy": ("쉬움", "Easy"),
    "normal": ("보통", "Normal"),
    "hard": ("어려움", "Hard"),
    "beginner": ("입문", "Beginner"),
    "expert": ("도전", "Expert"),
    "my_side": ("내 차례", "I play"),
    "black_first": ("흑 (먼저)", "Black (first)"),
    "white_second": ("백 (나중)", "White (second)"),
    "white_first": ("백 (먼저)", "White (first)"),
    "black_second": ("흑 (나중)", "Black (second)"),
    "rule33": ("쌍삼 금지", "No double-3"),
    "overline": ("6목 이상", "6 or more"),
    "on": ("켬", "On"),
    "off": ("끔", "Off"),
    "win": ("승리", "Wins"),
    "nowin": ("무효", "No win"),
    "language": ("언어", "Language"),
    "start": ("시작", "Start"),
    "undo": ("무르기", "Undo"),
    "new": ("새 게임", "New game"),
    "menu": ("메뉴", "Menu"),
    "black_turn": ("흑 차례", "Black to move"),
    "white_turn": ("백 차례", "White to move"),
    "thinking": ("컴퓨터가 생각 중...", "Computer is thinking..."),
    "black_wins": ("흑 승리!", "Black wins!"),
    "white_wins": ("백 승리!", "White wins!"),
    "draw": ("무승부", "Draw"),
    "forbidden": ("쌍삼 금지 자리예요", "Double-three is not allowed"),
    "check": ("체크!", "Check!"),
    "checkmate": ("체크메이트", "Checkmate"),
    "stalemate": ("스테일메이트", "Stalemate"),
    "no_engine": ("Stockfish가 없어요. get_stockfish.py를 실행하세요",
                  "Stockfish missing. Run get_stockfish.py"),
    "promote": ("무엇으로 바꿀까요?", "Promote to?"),
}


def t(key):
    return TEXT[key][0 if settings["lang"] == "ko" else 1]


_fonts = {}


def font(size, name="malgungothic"):
    if (name, size) not in _fonts:
        _fonts[name, size] = pygame.font.SysFont(name, size)
    return _fonts[name, size]


def text(screen, s, pos, size=22, color=INK, center=False, name="malgungothic"):
    img = font(size, name).render(s, True, color)
    r = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    screen.blit(img, r)
    return r


def button(screen, rect, label, selected=False, size=22):
    rect = pygame.Rect(rect)
    hover = rect.collidepoint(pygame.mouse.get_pos())
    fill = ACCENT if selected else (255, 255, 255) if hover else (248, 244, 236)
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, INK, rect, 2, border_radius=8)
    text(screen, label, rect.center, size, (255, 255, 255) if selected else INK, center=True)
    return rect


def panel(screen, lines):
    """오른쪽 상태 글자 + 무르기/새 게임/메뉴 버튼. 버튼 사각형 dict 반환."""
    y = 40
    for s in lines:
        text(screen, s, (PANEL_X, y), 24)
        y += 40
    return {
        "undo": button(screen, (PANEL_X, 420, 210, 52), t("undo")),
        "new": button(screen, (PANEL_X, 487, 210, 52), t("new")),
        "menu": button(screen, (PANEL_X, 554, 210, 52), t("menu")),
    }

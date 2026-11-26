"""오목: 규칙, AI, 화면.

좌표는 board[y][x]. 0 빈칸, 1 흑, 2 백.
"""
import random
import threading
from functools import lru_cache

import pygame

from common import BG, INK, panel, settings, t, text

N = 15
EMPTY, BLACK, WHITE = 0, 1, 2
DIRS = [(1, 0), (0, 1), (1, 1), (1, -1)]


def inside(x, y):
    return 0 <= x < N and 0 <= y < N


# ---------------------------------------------------------------- 규칙

def run_length(board, x, y, dx, dy, p):
    """(x,y)를 지나는 한 방향으로 p 돌이 몇 개 이어지는지 (자기 포함)."""
    n = 1
    for s in (1, -1):
        cx, cy = x + dx * s, y + dy * s
        while inside(cx, cy) and board[cy][cx] == p:
            n += 1
            cx, cy = cx + dx * s, cy + dy * s
    return n


def is_win(board, x, y, p, exact5=False):
    """(x,y)에 p가 이미 놓였다고 보고 승리인지."""
    for dx, dy in DIRS:
        n = run_length(board, x, y, dx, dy, p)
        if n == 5 or (n > 5 and not exact5):
            return True
    return False


def win_cells(board, x, y, p):
    """승리한 줄의 칸 목록 (화면 강조용)."""
    for dx, dy in DIRS:
        if run_length(board, x, y, dx, dy, p) >= 5:
            cells = [(x, y)]
            for s in (1, -1):
                cx, cy = x + dx * s, y + dy * s
                while inside(cx, cy) and board[cy][cx] == p:
                    cells.append((cx, cy))
                    cx, cy = cx + dx * s, cy + dy * s
            return cells
    return []


def line_str(board, x, y, dx, dy, p, r=5):
    """(x,y) 중심으로 앞뒤 r칸. 내 돌 X, 상대 돌과 판 밖은 O, 빈칸 '.'."""
    out = []
    for i in range(-r, r + 1):
        cx, cy = x + dx * i, y + dy * i
        v = board[cy][cx] if inside(cx, cy) else -1
        out.append("." if v == EMPTY else "X" if v == p else "O")
    return "".join(out)


def open_three(line, c=5):
    """빈칸 하나를 더 채워서 중심을 포함한 열린 4(.XXXX.)를 만들 수 있으면 열린 3."""
    for i, ch in enumerate(line):
        if ch != ".":
            continue
        s = line[:i] + "X" + line[i + 1:]
        for j in range(len(s) - 5):
            if s[j:j + 6] == ".XXXX." and j < c < j + 5 and j < i < j + 5:
                return True
    return False


def is_double_three(board, x, y, p):
    """(x,y)에 p를 두면 열린 3이 두 방향 이상 생기는지. 5목이 되는 수는 예외."""
    # ponytail: 렌주 공식 규칙의 세부 예외(거짓 3 등)는 무시. 아이들 대국에는 충분
    board[y][x] = p
    try:
        if is_win(board, x, y, p):
            return False
        return sum(open_three(line_str(board, x, y, dx, dy, p)) for dx, dy in DIRS) >= 2
    finally:
        board[y][x] = EMPTY


# ---------------------------------------------------------------- AI

PATTERNS = [
    ("XXXXX", 10_000_000),
    (".XXXX.", 100_000),
    ("XXXX.", 10_000), (".XXXX", 10_000), ("XXX.X", 10_000), ("X.XXX", 10_000), ("XX.XX", 10_000),
    ("..XXX.", 2_000), (".XXX..", 2_000), (".XX.X.", 2_000), (".X.XX.", 2_000),
    ("XXX..", 200), ("..XXX", 200), ("XX.X.", 200), (".X.XX", 200), ("X.XX.", 200),
    (".XX.X", 200), ("XX..X", 200), ("X..XX", 200), ("X.X.X", 200),
    ("..XX..", 100), (".X.X.", 50), (".XX..", 20), ("..XX.", 20),
]
FIVE = 10_000_000
WIN = 10**9


def _all_lines():
    lines = [[(x, y) for x in range(N)] for y in range(N)]
    lines += [[(x, y) for y in range(N)] for x in range(N)]
    for k in range(-(N - 5), N - 4):
        lines.append([(x, x - k) for x in range(N) if inside(x, x - k)])
        lines.append([(x, k + N - 1 - x) for x in range(N) if inside(x, k + N - 1 - x)])
    return lines


LINES = _all_lines()
CELL_LINES = [[[] for _ in range(N)] for _ in range(N)]  # 칸 -> [(줄 번호, 줄 안 위치)]
for _i, _ln in enumerate(LINES):
    for _pos, (_x, _y) in enumerate(_ln):
        CELL_LINES[_y][_x].append((_i, _pos))
AS_BLACK = str.maketrans("12|", "XOO")
AS_WHITE = str.maketrans("12|", "OXO")


@lru_cache(maxsize=500_000)  # ponytail: 같은 줄 모양이 탐색 중 계속 반복돼서 캐시가 핵심 속도
def line_value(s):
    """'|..1122.|' 같은 줄 문자열의 (흑 점수, 백 점수)."""
    b, w = s.translate(AS_BLACK), s.translate(AS_WHITE)
    return (sum(b.count(pt) * v for pt, v in PATTERNS),
            sum(w.count(pt) * v for pt, v in PATTERNS))


class Board:
    """탐색용 판. 돌 하나 놓을 때 그 돌이 지나는 줄 4개만 점수를 다시 계산한다."""

    def __init__(self, grid, exact5=False):
        self.g = [row[:] for row in grid]
        self.exact5 = exact5
        self.stones = [(x, y) for y in range(N) for x in range(N) if grid[y][x]]
        self.chars = [[".12"[grid[y][x]] for x, y in ln] for ln in LINES]
        self.line_score = [self._line(i) for i in range(len(LINES))]
        self.total = [sum(s[0] for s in self.line_score), sum(s[1] for s in self.line_score)]
        self.stack = []

    def _line(self, i):
        return line_value("|" + "".join(self.chars[i]) + "|")

    def place(self, x, y, p):
        self.g[y][x] = p
        self.stones.append((x, y))
        saved = []
        for i, pos in CELL_LINES[y][x]:
            self.chars[i][pos] = "12"[p - 1]
            old, new = self.line_score[i], self._line(i)
            saved.append((i, old))
            self.line_score[i] = new
            self.total[0] += new[0] - old[0]
            self.total[1] += new[1] - old[1]
        self.stack.append((x, y, saved))

    def undo(self):
        x, y, saved = self.stack.pop()
        self.g[y][x] = EMPTY
        self.stones.pop()
        for (i, old), (_, pos) in zip(saved, CELL_LINES[y][x]):
            self.chars[i][pos] = "."
            cur = self.line_score[i]
            self.total[0] += old[0] - cur[0]
            self.total[1] += old[1] - cur[1]
            self.line_score[i] = old

    def delta(self, x, y, p):
        """(x,y)에 p를 두면 흑/백 점수가 얼마나 바뀌는지. 판은 그대로 둔다."""
        db = dw = 0
        for i, pos in CELL_LINES[y][x]:
            self.chars[i][pos] = "12"[p - 1]
            new, old = self._line(i), self.line_score[i]
            self.chars[i][pos] = "."
            db += new[0] - old[0]
            dw += new[1] - old[1]
        return db, dw

    def candidates(self, r=2):
        seen = set()
        for sx, sy in self.stones:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    x, y = sx + dx, sy + dy
                    if inside(x, y) and self.g[y][x] == EMPTY:
                        seen.add((x, y))
        return seen

    def ordered_moves(self, p):
        """공격 가치 + 막기 가치가 큰 순서. [(점수, x, y), ...]"""
        q = 3 - p
        out = []
        for x, y in self.candidates():
            attack = self.delta(x, y, p)[p - 1]
            defend = self.delta(x, y, q)[q - 1]
            out.append((attack + defend * 0.9, x, y))
        out.sort(reverse=True)
        return out

    def best_leaf(self, p):
        """p가 한 수 두고 끝났을 때 가장 좋은 점수. 다음은 상대 차례라 상대 위협을 더 무겁게 본다."""
        best = -WIN * 2
        for x, y in self.candidates():
            d = self.delta(x, y, p)
            mine = self.total[p - 1] + d[p - 1]
            if d[p - 1] >= FIVE // 2:
                return WIN
            best = max(best, mine - (self.total[2 - p] + d[2 - p]) * 1.2)
        return best


def negamax(b, p, depth, alpha, beta, width):
    if depth == 1:
        return b.best_leaf(p)
    moves = b.ordered_moves(p)[:width]
    if not moves:
        return 0
    best = -WIN * 2
    for _, x, y in moves:
        b.place(x, y, p)
        if is_win(b.g, x, y, p, b.exact5):
            v = WIN + depth  # 빨리 이기는 쪽을 더 좋게
        else:
            v = -negamax(b, 3 - p, depth - 1, -beta, -alpha, width)
        b.undo()
        if v > best:
            best = v
        alpha = max(alpha, v)
        if alpha >= beta:
            break
    return best


# 난이도: (탐색 깊이, 후보 수)
LEVELS = [(1, 10), (2, 12), (4, 9)]


def choose_move(grid, p, level=1, forbid33=False, exact5=False):
    b = Board(grid, exact5)
    if not b.stones:
        return N // 2, N // 2
    moves = b.ordered_moves(p)
    if forbid33:
        moves = [m for m in moves if not is_double_three(b.g, m[1], m[2], p)]
    if not moves:
        return None

    # 바로 이기는 수, 그다음 상대가 바로 이기는 자리 막기
    for who in (p, 3 - p):
        for _, x, y in moves:
            b.g[y][x] = who
            win = is_win(b.g, x, y, who, exact5)
            b.g[y][x] = EMPTY
            if win:
                return x, y

    if level == 0:
        # 쉬움: 상위 몇 수 중 무작위. 일부러 실수할 여지를 둔다
        return random.choice(moves[:4])[1:]

    depth, width = LEVELS[level]
    best, best_v = moves[0][1:], -WIN * 3
    alpha = -WIN * 3
    for _, x, y in moves[:width + 3]:
        b.place(x, y, p)
        v = -negamax(b, 3 - p, depth - 1, -WIN * 3, -alpha, width)
        b.undo()
        if v > best_v:
            best, best_v = (x, y), v
        alpha = max(alpha, v)
    return best


# ---------------------------------------------------------------- 화면

CELL = 40
ORIGIN = 40  # (0,0) 교차점의 화면 좌표
WOOD = (222, 184, 120)
STARS = [(3, 3), (11, 3), (7, 7), (3, 11), (11, 11)]


def to_screen(x, y):
    return ORIGIN + x * CELL, ORIGIN + y * CELL


def from_screen(px, py):
    x, y = round((px - ORIGIN) / CELL), round((py - ORIGIN) / CELL)
    return (x, y) if inside(x, y) else None


def draw_stone(screen, x, y, p, alpha=255):
    cx, cy = to_screen(x, y)
    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    color = (20, 20, 20, alpha) if p == BLACK else (250, 250, 250, alpha)
    pygame.draw.circle(surf, color, (CELL // 2, CELL // 2), CELL // 2 - 2)
    pygame.draw.circle(surf, (0, 0, 0, alpha), (CELL // 2, CELL // 2), CELL // 2 - 2, 1)
    screen.blit(surf, (cx - CELL // 2, cy - CELL // 2))


def run(screen, clock):
    vs_ai = settings["vs_ai"]
    human = BLACK if settings["human_first"] else WHITE

    def reset():
        return [[EMPTY] * N for _ in range(N)], [], BLACK, None, ""

    board, history, turn, winner, msg = reset()
    win_line = []
    ai = {"thread": None, "result": None, "gen": 0}

    def ai_job(grid, p, gen):
        mv = choose_move(grid, p, settings["level"], settings["forbid33"], settings["exact5"])
        if gen == ai["gen"]:
            ai["result"] = mv

    def play(x, y):
        nonlocal turn, winner, win_line
        board[y][x] = turn
        history.append((x, y))
        if is_win(board, x, y, turn, settings["exact5"]):
            winner, win_line = turn, win_cells(board, x, y, turn)
        elif len(history) == N * N:
            winner = 0
        turn = 3 - turn

    while True:
        ai_turn = vs_ai and turn != human and winner is None
        if ai_turn and ai["thread"] is None:
            ai["result"] = None
            ai["thread"] = threading.Thread(
                target=ai_job, args=([r[:] for r in board], turn, ai["gen"]), daemon=True)
            ai["thread"].start()
        if ai["thread"] and not ai["thread"].is_alive():
            ai["thread"] = None
            if ai["result"] and winner is None:
                play(*ai["result"])

        screen.fill(BG)
        pygame.draw.rect(screen, WOOD, (10, 10, 620, 620), border_radius=6)
        for i in range(N):
            pygame.draw.line(screen, INK, to_screen(i, 0), to_screen(i, N - 1))
            pygame.draw.line(screen, INK, to_screen(0, i), to_screen(N - 1, i))
        for sx, sy in STARS:
            pygame.draw.circle(screen, INK, to_screen(sx, sy), 4)
        for y in range(N):
            for x in range(N):
                if board[y][x]:
                    draw_stone(screen, x, y, board[y][x])
        if history:
            pygame.draw.circle(screen, (220, 40, 40), to_screen(*history[-1]), 5)
        for cx, cy in win_line:
            pygame.draw.circle(screen, (220, 40, 40), to_screen(cx, cy), CELL // 2 - 1, 3)
        hover = from_screen(*pygame.mouse.get_pos())
        if hover and winner is None and not ai_turn and board[hover[1]][hover[0]] == EMPTY:
            draw_stone(screen, *hover, turn, alpha=110)

        if winner is not None:
            status = [t({BLACK: "black_wins", WHITE: "white_wins", 0: "draw"}[winner])]
        else:
            status = [t("black_turn" if turn == BLACK else "white_turn")]
            if ai_turn:
                status.append(t("thinking"))
        if msg:
            status.append(msg)
        buttons = panel(screen, status)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                ai["gen"] += 1
                return "quit"
            if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
                continue
            msg = ""
            if buttons["menu"].collidepoint(e.pos):
                ai["gen"] += 1
                return "menu"
            if buttons["new"].collidepoint(e.pos):
                ai["gen"] += 1
                ai["thread"] = None
                board, history, turn, winner, msg = reset()
                win_line = []
            elif buttons["undo"].collidepoint(e.pos):
                if ai_turn:
                    continue
                # 컴퓨터 대전에서는 내 차례가 될 때까지 되돌린다
                ai["gen"] += 1
                ai["thread"] = None
                while history:
                    x, y = history.pop()
                    board[y][x] = EMPTY
                    turn = 3 - turn
                    if not vs_ai or turn == human:
                        break
                winner, win_line = None, []
            elif winner is None and not ai_turn:
                cell = from_screen(*e.pos)
                if cell and board[cell[1]][cell[0]] == EMPTY:
                    if settings["forbid33"] and is_double_three(board, *cell, turn):
                        msg = t("forbidden")
                    else:
                        play(*cell)
        clock.tick(30)

"""오목 규칙/AI 확인. 실행: python test_gomoku.py"""
import time

from gomoku import BLACK, EMPTY, N, WHITE, choose_move, is_double_three, is_win


def empty():
    return [[EMPTY] * N for _ in range(N)]


def put(board, p, cells):
    for x, y in cells:
        board[y][x] = p


def test_win():
    b = empty()
    put(b, BLACK, [(3, 7), (4, 7), (5, 7), (6, 7), (7, 7)])
    assert is_win(b, 5, 7, BLACK)
    b = empty()
    put(b, WHITE, [(2, 2), (3, 3), (4, 4), (5, 5)])
    assert not is_win(b, 5, 5, WHITE)
    put(b, WHITE, [(6, 6)])
    assert is_win(b, 6, 6, WHITE)


def test_overline():
    b = empty()
    put(b, BLACK, [(x, 7) for x in range(2, 8)])  # 6목
    assert is_win(b, 4, 7, BLACK, exact5=False)
    assert not is_win(b, 4, 7, BLACK, exact5=True)


def test_double_three():
    b = empty()
    put(b, BLACK, [(5, 7), (6, 7), (7, 5), (7, 6)])  # (7,7)에 두면 가로 3 + 세로 3
    assert is_double_three(b, 7, 7, BLACK)
    put(b, WHITE, [(4, 7)])  # 가로 한쪽이 막히면 열린 3이 아님
    assert not is_double_three(b, 7, 7, BLACK)


def test_ai_wins_and_blocks():
    b = empty()
    put(b, WHITE, [(3, 3), (4, 3), (5, 3), (6, 3)])
    put(b, BLACK, [(3, 10), (4, 10), (5, 10), (6, 10)])
    for lvl in range(3):
        assert choose_move(b, WHITE, lvl) in [(2, 3), (7, 3)], "자기 5목을 완성해야 함"
    b = empty()
    put(b, BLACK, [(5, 5), (6, 5), (7, 5), (8, 5)])
    put(b, WHITE, [(5, 6), (6, 6), (12, 12)])
    for lvl in range(3):
        assert choose_move(b, WHITE, lvl) in [(4, 5), (9, 5)], "상대 4를 막아야 함"


def test_ai_blocks_open_three():
    b = empty()
    put(b, BLACK, [(6, 7), (7, 7), (8, 7)])
    put(b, WHITE, [(7, 8), (6, 8)])
    for lvl in (1, 2):
        assert choose_move(b, WHITE, lvl) in [(5, 7), (9, 7), (4, 7), (10, 7)], "열린 3을 막아야 함"


def test_speed():
    b = empty()
    put(b, BLACK, [(7, 7), (8, 8), (6, 8), (9, 6), (7, 9), (5, 6)])
    put(b, WHITE, [(8, 7), (7, 8), (6, 6), (9, 9), (8, 6), (10, 8)])
    for lvl in range(3):
        start = time.time()
        choose_move(b, BLACK, lvl)
        sec = time.time() - start
        print(f"  level {lvl}: {sec:.2f}s")
        assert sec < 6, "너무 느림"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)

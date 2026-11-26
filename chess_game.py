"""체스 화면. 규칙은 python-chess, 컴퓨터 상대는 Stockfish."""
import subprocess
import threading

import chess
import chess.engine
import pygame

from common import BASE, BG, INK, panel, settings, t, text

ENGINE_PATH = BASE / "engine" / "stockfish.exe"
S = 76        # 칸 크기
OX = OY = 16  # 판 왼쪽 위
LIGHT, DARK = (240, 217, 181), (181, 136, 99)
PIECE_FONT = "segoeuisymbol"

# 난이도: (Stockfish 옵션, 생각 제한)
LEVELS = [
    ({"Skill Level": 0}, chess.engine.Limit(depth=1)),
    ({"UCI_LimitStrength": True, "UCI_Elo": 1320}, chess.engine.Limit(time=0.3)),
    ({"UCI_LimitStrength": True, "UCI_Elo": 1600}, chess.engine.Limit(time=0.5)),
    ({"UCI_LimitStrength": True, "UCI_Elo": 2000}, chess.engine.Limit(time=1.0)),
]


def engine_ready():
    return ENGINE_PATH.exists()


def sq_rect(sq, flipped):
    f, r = chess.square_file(sq), chess.square_rank(sq)
    if flipped:
        f, r = 7 - f, 7 - r
    return pygame.Rect(OX + f * S, OY + (7 - r) * S, S, S)


def sq_at(pos, flipped):
    x, y = (pos[0] - OX) // S, (pos[1] - OY) // S
    if not (0 <= x < 8 and 0 <= y < 8):
        return None
    f, r = (7 - x, y) if flipped else (x, 7 - y)
    return chess.square(f, r)


def draw_piece(screen, piece, center, size=62):
    filled = chess.UNICODE_PIECE_SYMBOLS[piece.symbol().lower()]
    if piece.color == chess.WHITE:
        # 흰 말: 속이 찬 모양을 흰색으로 칠하고 테두리 모양을 검게 덧그림
        text(screen, filled, center, size, (255, 255, 255), True, PIECE_FONT)
        text(screen, chess.UNICODE_PIECE_SYMBOLS[piece.symbol().upper()], center, size, INK, True, PIECE_FONT)
    else:
        text(screen, filled, center, size, (10, 10, 10), True, PIECE_FONT)


def tint(screen, rect, rgba):
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    surf.fill(rgba)
    screen.blit(surf, rect)


def run(screen, clock):
    vs_ai = settings["vs_ai"]
    human = chess.WHITE if settings["human_first"] else chess.BLACK
    flipped = vs_ai and human == chess.BLACK
    board = chess.Board()
    sel = None      # 선택한 칸
    promo = None    # 프로모션 대기 중인 (출발, 도착)
    ai = {"thread": None, "result": None, "gen": 0}

    engine = None
    if vs_ai:
        engine = chess.engine.SimpleEngine.popen_uci(
            str(ENGINE_PATH), creationflags=subprocess.CREATE_NO_WINDOW)
        options, limit = LEVELS[settings["level"]]
        engine.configure(options)

    def ai_job(b, gen):
        mv = engine.play(b, limit).move
        if gen == ai["gen"]:
            ai["result"] = mv

    try:
        while True:
            over = board.outcome(claim_draw=True)
            ai_turn = vs_ai and board.turn != human and over is None
            th = ai["thread"]
            if th and not th.is_alive():
                ai["thread"] = None
                mv, ai["result"] = ai["result"], None
                if mv and ai_turn and mv in board.legal_moves:
                    board.push(mv)
                    continue
            # 엔진은 한 번에 하나만 생각하게 한다 (이전 생각이 끝날 때까지 기다림)
            if ai_turn and ai["thread"] is None:
                ai["thread"] = threading.Thread(
                    target=ai_job, args=(board.copy(), ai["gen"]), daemon=True)
                ai["thread"].start()

            # ---- 그리기
            screen.fill(BG)
            last = board.peek() if board.move_stack else None
            targets = {m.to_square for m in board.legal_moves if m.from_square == sel} if sel is not None else set()
            for sq in chess.SQUARES:
                r = sq_rect(sq, flipped)
                light = (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1
                pygame.draw.rect(screen, LIGHT if light else DARK, r)
                if last and sq in (last.from_square, last.to_square):
                    tint(screen, r, (255, 230, 60, 110))
                if sq == sel:
                    tint(screen, r, (60, 140, 255, 120))
                piece = board.piece_at(sq)
                if piece and piece.piece_type == chess.KING and piece.color == board.turn and board.is_check():
                    tint(screen, r, (230, 30, 30, 140))
                if piece:
                    draw_piece(screen, piece, r.center)
                if sq in targets:
                    if piece:
                        pygame.draw.circle(screen, (40, 40, 40), r.center, S // 2 - 3, 4)
                    else:
                        pygame.draw.circle(screen, (40, 40, 40), r.center, 10)
            # 칸 이름 (a~h, 1~8)
            for i in range(8):
                f = 7 - i if flipped else i
                text(screen, "abcdefgh"[f], (OX + i * S + S - 12, OY + 8 * S - 20), 14)
                text(screen, str(8 - i if not flipped else i + 1), (OX + 3, OY + i * S + 2), 14)

            if over:
                if over.winner is None:
                    status = [t("stalemate") if over.termination == chess.Termination.STALEMATE else t("draw")]
                else:
                    status = [t("checkmate"), t("white_wins" if over.winner else "black_wins")]
            else:
                status = [t("white_turn" if board.turn else "black_turn")]
                if board.is_check():
                    status.append(t("check"))
                if ai_turn:
                    status.append(t("thinking"))
            buttons = panel(screen, status)

            promo_rects = []
            if promo:
                box = pygame.Rect(OX + 2 * S - 20, OY + 3 * S - 30, 4 * S + 40, S + 80)
                pygame.draw.rect(screen, (255, 255, 255), box, border_radius=10)
                pygame.draw.rect(screen, INK, box, 2, border_radius=10)
                text(screen, t("promote"), (box.centerx, box.y + 22), 22, center=True)
                for i, pt in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
                    r = pygame.Rect(box.x + 20 + i * S, box.y + 50, S, S)
                    pygame.draw.rect(screen, LIGHT, r, border_radius=6)
                    draw_piece(screen, chess.Piece(pt, board.turn), r.center)
                    promo_rects.append((pt, r))
            pygame.display.flip()

            # ---- 입력
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "quit"
                if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
                    continue
                if buttons["menu"].collidepoint(e.pos):
                    return "menu"
                if buttons["new"].collidepoint(e.pos):
                    ai["gen"] += 1
                    board.reset()
                    sel = promo = None
                    continue
                if buttons["undo"].collidepoint(e.pos):
                    if not ai_turn and board.move_stack:
                        ai["gen"] += 1
                        board.pop()
                        # 컴퓨터 대전에서는 내 차례가 될 때까지 되돌린다
                        if vs_ai and board.turn != human and board.move_stack:
                            board.pop()
                    sel = promo = None
                    continue
                if promo:
                    for pt, r in promo_rects:
                        if r.collidepoint(e.pos):
                            board.push(chess.Move(*promo, promotion=pt))
                    promo = None
                    continue
                sq = sq_at(e.pos, flipped)
                if sq is None or over or ai_turn:
                    continue
                if sel is not None:
                    moves = [m for m in board.legal_moves if m.from_square == sel and m.to_square == sq]
                    if moves:
                        if len(moves) > 1:  # 프로모션은 같은 칸으로 가는 수가 4개
                            promo = (sel, sq)
                        else:
                            board.push(moves[0])
                        sel = None
                        continue
                piece = board.piece_at(sq)
                sel = sq if piece and piece.color == board.turn and sq != sel else None
            clock.tick(30)
    finally:
        if engine:
            ai["gen"] += 1
            if ai["thread"]:
                ai["thread"].join(timeout=3)
            engine.quit()

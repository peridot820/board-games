# 보드게임 (오목, 체스)

아이들이 집 컴퓨터에서 오목과 체스를 두는 프로그램입니다. 둘이서 둘 수도 있고 컴퓨터와 둘 수도 있습니다.

## 기능

- 오목 (15x15)
  - 친구와 2인 대전, 컴퓨터 대전 (쉬움 / 보통 / 어려움)
  - 규칙 선택: 쌍삼 금지 (기본 끔), 6목 이상 승리 인정 여부 (기본 승리)
- 체스
  - 친구와 2인 대전, 컴퓨터 대전 (입문 / 보통 / 어려움 / 도전)
  - 캐슬링, 앙파상, 프로모션, 무승부 규칙 모두 지원
  - 컴퓨터 상대는 [Stockfish](https://stockfishchess.org/) (보통 Elo 1320, 어려움 1600, 도전 2000)
- 공통: 무르기, 새 게임, 마지막 수 표시, 한국어 / English 선택

## 처음 설치

Windows, Python 3.12 기준입니다.

```powershell
pip install -r requirements.txt
python get_stockfish.py      # 체스 컴퓨터 상대 (engine/stockfish.exe, 약 100MB)
```

Stockfish 파일은 GitHub 용량 제한(100MB)을 넘어서 저장소에 넣지 않았습니다. 처음 한 번 `get_stockfish.py`로 받으면 됩니다.

## 실행

```powershell
python main.py
```

## exe 만들기와 바탕화면 바로가기

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

`dist/BoardGames/BoardGames.exe`가 만들어지고, 바탕화면에 "보드게임" 바로가기가 생깁니다. 코드를 고친 뒤에는 다시 실행하면 됩니다.

## 테스트

```powershell
python test_gomoku.py
```

오목 승리 판정, 6목, 쌍삼, 컴퓨터가 5목을 완성하는지와 4를 막는지, 생각 시간을 확인합니다.

## 파일 구성

| 파일 | 내용 |
|---|---|
| `main.py` | 메뉴, 프로그램 시작 |
| `common.py` | 설정, 한국어/영어 글자, 버튼 |
| `gomoku.py` | 오목 규칙, 컴퓨터(알파베타 탐색), 화면 |
| `chess_game.py` | 체스 화면, Stockfish 연결 |
| `get_stockfish.py` | Stockfish 내려받기 |
| `build.ps1` | exe 빌드, 바로가기 생성 |

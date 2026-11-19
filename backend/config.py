"""設定値をここに集める。あとで数字を変えるときは、このファイルだけ直す。"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("GAKUMON_DB", os.path.join(BASE_DIR, "gakumon.db"))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

# ニックネーム・名前
NICKNAME_MAX = 10              # 決定:10文字まで
DEFAULT_NICKNAME = "ななしさん"   # 決定:未入力のとき
MONSTER_NAME_MAX = 8           # 決定:8文字まで
EGG_NAME = "タマゴ"              # 卵のあいだの表示名
DEFAULT_HATCH_NAME = "モンスター"  # 仮:孵化のとき名前が空だった場合(仮の名前は未決定)

# テスト
QUESTION_COUNT = 5             # 決定:1回のテストは5問
MIN_SENDS_FOR_TEST = 3         # 決定:説明を3回以上送るとテストを受けさせられる
REASONS = ["計算ミス", "考え方が違う", "教えていない内容"]  # ×のときの理由

# 経験値(決定)
EXP_PER_MATCH = 10             # 自分の採点が合っていた1問につき
ALL_MATCH_BONUS = 10           # 全問合っていたらボーナス
STAGE_EXP = [0, 30, 100, 180]  # 卵→赤ちゃん30、赤ちゃん→成長100、成長→大人180
STAGE_NAMES = ["卵", "赤ちゃん", "成長", "大人"]

# 単元(最初は中1の3単元)
UNITS = {1: "正負の数", 2: "文字と式", 3: "方程式"}

# 開発中のLive Server(5500番)からもAPIを使えるようにする
DEV_ORIGINS = ["http://127.0.0.1:5500", "http://localhost:5500"]

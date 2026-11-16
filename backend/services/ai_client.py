"""AIの呼び出し口。いまは「仮の返事」を返す(APIキーが用意できたら、ここを置き換える)。

画面側・API側は、この2つの関数だけを呼ぶ。本物のAIにするときも、
同じ形(引数と戻り値)を守れば、ほかのファイルは直さなくていい。
"""

import random

from services import questions


def reply(unit_name, message, notes):
    """教える画面で、モンスターが返す言葉"""
    if "負の数" in message:
        return "負の数って0より小さい数なんだね！"
    if "正の数" in message:
        return "正の数は0より大きい数かな？"
    return random.choice(["なるほど！", "もっと詳しく教えて！",
                          "それってどういう意味？", "少し分かってきたよ！", "例も教えて！"])


def answer(question_text, correct_answer, notes):
    """テストの問題に、モンスターが答える。ノートの内容だけで解く(仮:ノートの量で正解率が変わる)
    戻り値: (答え, 考え方)
    """
    if not notes:
        return "わからない", "ノートに書いてないよ"
    rng = random.Random(question_text + str(len(notes)))   # 同じ条件なら同じ答え
    # ノートが多いほど正解しやすい(最大90%)。仮の動き。
    p_correct = min(0.9, 0.4 + 0.1 * len(notes))
    if rng.random() < p_correct:
        return correct_answer, "ノートの内容を使って計算したよ"
    wrong = int(correct_answer) + rng.choice([-2, -1, 1, 2])
    return str(wrong), "たぶんこうかな…"

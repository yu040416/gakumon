"""経験値と進化の計算(画面にも、DBにも依存しない)"""

import config


def stage_for_exp(exp):
    """累計経験値から段階(0=卵,1=赤ちゃん,2=成長,3=大人)を求める"""
    stage = 0
    for i, need in enumerate(config.STAGE_EXP):
        if exp >= need:
            stage = i
    return stage


def exp_gain(match_count, total):
    """獲得経験値。自分の採点が合った1問につき10、全問合ったら+10"""
    gain = match_count * config.EXP_PER_MATCH
    if total > 0 and match_count == total:
        gain += config.ALL_MATCH_BONUS
    return gain


def progress(exp):
    """経験値バーに出す値"""
    stage = stage_for_exp(exp)
    if stage < len(config.STAGE_EXP) - 1:
        lo = config.STAGE_EXP[stage]
        hi = config.STAGE_EXP[stage + 1]
        percent = int((exp - lo) / (hi - lo) * 100)
        rest = hi - exp
    else:  # 大人は最大
        hi, percent, rest = config.STAGE_EXP[-1], 100, 0
    return {
        "stage": stage,
        "stage_name": config.STAGE_NAMES[stage],
        "exp": exp,
        "next_exp": hi,
        "percent": percent,
        "rest": rest,
    }

"""ガクモンのAPI(画面のJavaScriptから fetch で呼ぶ)

ユーザーの見分けかた: ブラウザに保存したIDを、ヘッダー X-User-Id で送る(ログインなし)。
"""

import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

import config
from db import get_db
from services import ai_client, exp, questions

bp = Blueprint("api", __name__, url_prefix="/api")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def fail(message, status=400):
    return jsonify({"error": message}), status


def current_user():
    uid = request.headers.get("X-User-Id", "")
    return get_db().execute("SELECT * FROM users WHERE user_id = ?", (uid,)).fetchone()


def get_json():
    return request.get_json(silent=True) or {}


# ---------- ひとまとめにして返す形 ----------

def teach_count_since_last_test(db, monster_id):
    """前のテストが終わってから、説明を送った回数"""
    last = db.execute(
        "SELECT MAX(finished_at) AS t FROM tests WHERE monster_id = ? AND finished_at IS NOT NULL",
        (monster_id,)).fetchone()["t"] or ""
    return db.execute(
        "SELECT COUNT(*) AS n FROM teach_logs WHERE monster_id = ? AND started_at > ?",
        (monster_id, last)).fetchone()["n"]


def monster_dict(db, m):
    p = exp.progress(m["exp"])
    sends = teach_count_since_last_test(db, m["monster_id"])
    return {
        "unit_id": m["unit_id"],
        "unit_name": config.UNITS[m["unit_id"]],
        "name": m["name"],
        **p,
        "send_count": sends,
        "can_test": sends >= config.MIN_SENDS_FOR_TEST,
    }


def get_monster(db, user, unit_id):
    return db.execute("SELECT * FROM monsters WHERE user_id = ? AND unit_id = ?",
                      (user["user_id"], unit_id)).fetchone()


def create_monster(db, user_id, unit_id):
    db.execute(
        "INSERT INTO monsters (user_id, unit_id, name, stage, exp, created_at) VALUES (?, ?, ?, 0, 0, ?)",
        (user_id, unit_id, config.EGG_NAME, now()))
    db.commit()


# ---------- ユーザー ----------

@bp.post("/users")
def create_user():
    """はじめる:ユーザーIDを作り、最初の単元の卵をわたす"""
    nickname = str(get_json().get("nickname", "")).strip()
    if len(nickname) > config.NICKNAME_MAX:
        return fail("もう少し短くしてね")
    if nickname == "":
        nickname = config.DEFAULT_NICKNAME
    db = get_db()
    uid = str(uuid.uuid4())
    db.execute("INSERT INTO users (user_id, nickname, created_at) VALUES (?, ?, ?)",
               (uid, nickname, now()))
    create_monster(db, uid, 1)
    return jsonify({"user_id": uid, "nickname": nickname}), 201


@bp.get("/me")
def me():
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    rows = db.execute("SELECT * FROM monsters WHERE user_id = ? ORDER BY unit_id",
                      (user["user_id"],)).fetchall()
    return jsonify({"nickname": user["nickname"],
                    "monsters": [monster_dict(db, m) for m in rows]})


# ---------- 単元・モンスター ----------

def unit_or_404(unit_id):
    return unit_id in config.UNITS


@bp.post("/units/<int:unit_id>/open")
def open_unit(unit_id):
    """単元を開く:その単元のモンスター(卵)がなければ、はじめてもらう"""
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    if not unit_or_404(unit_id):
        return fail("単元が見つかりません", 404)
    db = get_db()
    if not get_monster(db, user, unit_id):
        create_monster(db, user["user_id"], unit_id)
    return jsonify(monster_dict(db, get_monster(db, user, unit_id)))


@bp.patch("/units/<int:unit_id>/monster")
def rename_monster(unit_id):
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    m = get_monster(db, user, unit_id)
    if not m:
        return fail("モンスターが見つかりません", 404)
    name = str(get_json().get("name", "")).strip()
    if name == "" or len(name) > config.MONSTER_NAME_MAX:
        return fail("名前は1〜8文字で入れてね")
    db.execute("UPDATE monsters SET name = ? WHERE monster_id = ?", (name, m["monster_id"]))
    db.commit()
    return jsonify(monster_dict(db, get_monster(db, user, unit_id)))


# ---------- 教える ----------

@bp.post("/units/<int:unit_id>/teach")
def teach(unit_id):
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    m = get_monster(db, user, unit_id)
    if not m:
        return fail("モンスターが見つかりません", 404)
    message = str(get_json().get("message", "")).strip()
    if message == "":
        return fail("説明を入れてね")
    notes = [r["content"] for r in db.execute(
        "SELECT content FROM notes WHERE monster_id = ?", (m["monster_id"],))]
    reply = ai_client.reply(config.UNITS[unit_id], message, notes)
    t = now()
    db.execute("INSERT INTO teach_logs (monster_id, started_at) VALUES (?, ?)",
               (m["monster_id"], t))
    # 仮:ノートの作り方は未決定なので、教えた言葉をそのままノートに入れる
    db.execute("INSERT INTO notes (monster_id, content, updated_at) VALUES (?, ?, ?)",
               (m["monster_id"], message, t))
    db.commit()
    d = monster_dict(db, m)
    return jsonify({"reply": reply, "send_count": d["send_count"], "can_test": d["can_test"]})


@bp.get("/units/<int:unit_id>/notes")
def notes(unit_id):
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    m = get_monster(db, user, unit_id)
    if not m:
        return fail("モンスターが見つかりません", 404)
    rows = db.execute("SELECT content FROM notes WHERE monster_id = ? ORDER BY note_id",
                      (m["monster_id"],)).fetchall()
    return jsonify({"notes": [r["content"] for r in rows]})


# ---------- テスト ----------

def own_test(db, user, test_id):
    return db.execute(
        """SELECT t.* FROM tests t JOIN monsters m ON m.monster_id = t.monster_id
           WHERE t.test_id = ? AND m.user_id = ?""", (test_id, user["user_id"])).fetchone()


@bp.post("/units/<int:unit_id>/tests")
def start_test(unit_id):
    """テストを始める:問題を作り、モンスターの答案をつける(正解はまだ返さない)"""
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    m = get_monster(db, user, unit_id)
    if not m:
        return fail("モンスターが見つかりません", 404)
    d = monster_dict(db, m)
    if not d["can_test"]:
        return fail(f"あと{config.MIN_SENDS_FOR_TEST - d['send_count']}回教えると、テストを受けさせられるよ", 409)

    kind = get_json().get("kind", "unit")
    if kind not in ("unit", "review"):
        return fail("テストの種類が正しくありません")

    # 途中のテストが残っていたら捨てる(途中でやめた結果は保存しない)
    for old in db.execute("SELECT test_id FROM tests WHERE monster_id = ? AND finished_at IS NULL",
                          (m["monster_id"],)).fetchall():
        discard_test(db, old["test_id"])

    cur = db.execute(
        "INSERT INTO tests (monster_id, kind, question_count, started_at) VALUES (?, ?, ?, ?)",
        (m["monster_id"], kind, config.QUESTION_COUNT, now()))
    test_id = cur.lastrowid
    note_list = [r["content"] for r in db.execute(
        "SELECT content FROM notes WHERE monster_id = ?", (m["monster_id"],))]
    out = []
    for no, q in enumerate(questions.generate_test(unit_id, config.QUESTION_COUNT), 1):
        ans, reason = ai_client.answer(q["text"], q["answer"], note_list)
        db.execute(
            """INSERT INTO test_items (test_id, no, template_key, question_text, correct_answer,
                                       monster_answer, monster_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (test_id, no, q["template_key"], q["text"], q["answer"], ans, reason))
        out.append({"no": no, "question_text": q["text"],
                    "monster_answer": ans, "monster_reason": reason})
    db.commit()
    return jsonify({"test_id": test_id, "kind": kind, "question_count": config.QUESTION_COUNT,
                    "questions": out}), 201


@bp.post("/tests/<int:test_id>/items/<int:no>/grade")
def grade(test_id, no):
    """「答え合わせ」:自分の採点(○/×)を受け取り、正解と、採点が合っていたかを返す"""
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    test = own_test(db, user, test_id)
    if not test or test["finished_at"]:
        return fail("テストが見つかりません", 404)
    item = db.execute("SELECT * FROM test_items WHERE test_id = ? AND no = ?",
                      (test_id, no)).fetchone()
    if not item:
        return fail("問題が見つかりません", 404)
    if item["user_mark"]:
        return fail("答え合わせのあとは、採点を変えられないよ", 409)
    data = get_json()
    mark = data.get("mark")
    if mark not in ("maru", "batsu"):
        return fail("○か×を選んでね")
    reason = data.get("reason") if mark == "batsu" else None
    if reason is not None and reason not in config.REASONS:
        return fail("理由が正しくありません")
    monster_ok = questions.is_same_answer(item["monster_answer"], item["correct_answer"])
    match = (mark == "maru") == monster_ok
    db.execute(
        """UPDATE test_items SET user_mark = ?, user_reason = ?, is_monster_correct = ?, is_match = ?
           WHERE item_id = ?""", (mark, reason, int(monster_ok), int(match), item["item_id"]))
    db.commit()
    return jsonify({"correct_answer": item["correct_answer"],
                    "is_monster_correct": monster_ok, "is_match": match})


@bp.post("/tests/<int:test_id>/finish")
def finish_test(test_id):
    """結果を出す:経験値を足し、進化を判定し、不正解を「あやふやポイント」に残す"""
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    test = own_test(db, user, test_id)
    if not test or test["finished_at"]:
        return fail("テストが見つかりません", 404)
    items = db.execute("SELECT * FROM test_items WHERE test_id = ? ORDER BY no", (test_id,)).fetchall()
    if any(i["user_mark"] is None for i in items):
        return fail("まだ採点していない問題があるよ", 400)

    correct = sum(i["is_monster_correct"] for i in items)
    matched = sum(i["is_match"] for i in items)
    gain = exp.exp_gain(matched, len(items))

    m = db.execute("SELECT * FROM monsters WHERE monster_id = ?", (test["monster_id"],)).fetchone()
    old_stage = exp.stage_for_exp(m["exp"])
    new_exp = m["exp"] + gain
    new_stage = exp.stage_for_exp(new_exp)

    name = m["name"]
    hatched = old_stage == 0 and new_stage >= 1
    if hatched:   # 卵がかえった:名前を決める(空なら仮の名前)
        hatch_name = str(get_json().get("hatch_name", "")).strip()
        if len(hatch_name) > config.MONSTER_NAME_MAX:
            return fail("名前は8文字までだよ")
        name = hatch_name or config.DEFAULT_HATCH_NAME

    db.execute("UPDATE monsters SET exp = ?, stage = ?, name = ? WHERE monster_id = ?",
               (new_exp, new_stage, name, m["monster_id"]))
    db.execute("UPDATE tests SET correct_count = ?, match_count = ?, exp_gained = ?, finished_at = ? WHERE test_id = ?",
               (correct, matched, gain, now(), test_id))
    wrong = []
    for i in items:
        if not i["is_monster_correct"]:
            db.execute("INSERT INTO weak_points (monster_id, item_id, summary) VALUES (?, ?, ?)",
                       (m["monster_id"], i["item_id"], i["question_text"]))
            wrong.append({"no": i["no"], "question_text": i["question_text"],
                          "monster_answer": i["monster_answer"],
                          "correct_answer": i["correct_answer"],
                          "reason": i["user_reason"]})
    db.commit()
    return jsonify({
        "question_count": len(items), "correct_count": correct, "match_count": matched,
        "exp_gained": gain, "all_correct": correct == len(items),
        "evolved": new_stage > old_stage, "hatched": hatched,
        "monster": monster_dict(db, db.execute("SELECT * FROM monsters WHERE monster_id = ?",
                                               (m["monster_id"],)).fetchone()),
        "wrong_items": wrong})


def discard_test(db, test_id):
    db.execute("DELETE FROM test_items WHERE test_id = ?", (test_id,))
    db.execute("DELETE FROM tests WHERE test_id = ?", (test_id,))
    db.commit()


@bp.delete("/tests/<int:test_id>")
def quit_test(test_id):
    """やめる:途中のテストを捨てる(教えたノートは残る)"""
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    test = own_test(db, user, test_id)
    if not test or test["finished_at"]:
        return fail("テストが見つかりません", 404)
    discard_test(db, test_id)
    return jsonify({"discarded": True})


# ---------- 学習履歴 ----------

@bp.get("/history")
def history():
    user = current_user()
    if not user:
        return fail("ユーザーが見つかりません", 401)
    db = get_db()
    uid = user["user_id"]
    teach_n = db.execute(
        """SELECT COUNT(*) AS n FROM teach_logs l JOIN monsters m ON m.monster_id = l.monster_id
           WHERE m.user_id = ?""", (uid,)).fetchone()["n"]
    tests = db.execute(
        """SELECT t.*, m.unit_id FROM tests t JOIN monsters m ON m.monster_id = t.monster_id
           WHERE m.user_id = ? AND t.finished_at IS NOT NULL ORDER BY t.finished_at DESC""",
        (uid,)).fetchall()
    total_q = sum(t["question_count"] for t in tests)
    total_match = sum(t["match_count"] for t in tests)
    weak = db.execute(
        """SELECT w.wp_id, w.summary, m.unit_id FROM weak_points w
           JOIN monsters m ON m.monster_id = w.monster_id
           WHERE m.user_id = ? AND w.resolved = 0 ORDER BY w.wp_id DESC""", (uid,)).fetchall()
    return jsonify({
        "teach_count": teach_n,
        "test_count": len(tests),
        "accuracy_percent": int(total_match / total_q * 100) if total_q else None,
        "recent": [{"date": t["finished_at"][:10], "unit_name": config.UNITS[t["unit_id"]],
                    "kind": t["kind"], "correct_count": t["correct_count"],
                    "match_count": t["match_count"], "question_count": t["question_count"],
                    "exp_gained": t["exp_gained"]} for t in tests[:20]],
        "weak_points": [{"wp_id": w["wp_id"], "unit_id": w["unit_id"],
                         "unit_name": config.UNITS[w["unit_id"]], "summary": w["summary"]}
                        for w in weak],
    })

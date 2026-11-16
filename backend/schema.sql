-- ガクモン DB(SQLite)。DB設計書をもとに、最初に必要な分だけ作る。

CREATE TABLE IF NOT EXISTS users (
    user_id     TEXT PRIMARY KEY,
    nickname    TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS units (
    unit_id   INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    order_no  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS monsters (
    monster_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        TEXT NOT NULL REFERENCES users(user_id),
    unit_id        INTEGER NOT NULL REFERENCES units(unit_id),
    name           TEXT NOT NULL,
    stage          INTEGER NOT NULL DEFAULT 0,
    exp            INTEGER NOT NULL DEFAULT 0,
    review_due_at  TEXT,
    created_at     TEXT NOT NULL,
    UNIQUE (user_id, unit_id)
);

CREATE TABLE IF NOT EXISTS notes (
    note_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id  INTEGER NOT NULL REFERENCES monsters(monster_id),
    content     TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- 教えるメッセージを1回送るごとに1行(「3回以上送ったらテスト」の判定に使う)
CREATE TABLE IF NOT EXISTS teach_logs (
    log_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id    INTEGER NOT NULL REFERENCES monsters(monster_id),
    started_at    TEXT NOT NULL,
    duration_sec  INTEGER,
    send_count    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tests (
    test_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id      INTEGER NOT NULL REFERENCES monsters(monster_id),
    kind            TEXT NOT NULL,        -- unit=単元テスト, review=復習テスト
    question_count  INTEGER NOT NULL,
    correct_count   INTEGER,
    match_count     INTEGER,
    exp_gained      INTEGER,
    started_at      TEXT NOT NULL,
    finished_at     TEXT                  -- NULLのあいだは途中(やめたら消す)
);

-- 問題テンプレートはコード(services/questions.py)にあるので、キーだけ保存する
CREATE TABLE IF NOT EXISTS test_items (
    item_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id             INTEGER NOT NULL REFERENCES tests(test_id),
    no                  INTEGER NOT NULL,
    template_key        TEXT NOT NULL,
    question_text       TEXT NOT NULL,
    correct_answer      TEXT NOT NULL,
    monster_answer      TEXT,
    monster_reason      TEXT,
    user_mark           TEXT,             -- maru / batsu
    user_reason         TEXT,
    is_monster_correct  INTEGER,
    is_match            INTEGER,
    UNIQUE (test_id, no)
);

CREATE TABLE IF NOT EXISTS weak_points (
    wp_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id  INTEGER NOT NULL REFERENCES monsters(monster_id),
    item_id     INTEGER NOT NULL REFERENCES test_items(item_id),
    summary     TEXT NOT NULL,
    resolved    INTEGER NOT NULL DEFAULT 0
);

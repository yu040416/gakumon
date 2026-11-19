# ガクモン backend(Flask + SQLite)

## 起動
```
cd backend
pip install -r requirements.txt
python app.py
```
ブラウザで http://127.0.0.1:5000 を開く(`../frontend` の画面もここから配られる)。
DBファイル `gakumon.db` は、はじめて起動したときに自動で作られる(Gitには入れない)。

## 動作確認
```
python -m unittest discover -s tests
```

## ファイル
| ファイル | 役割 |
|---|---|
| `app.py` | サーバーの起動、frontendの配信 |
| `api.py` | API(下の表) |
| `config.py` | 設定値(経験値10、進化30/100/180、5問、3回送信…) |
| `schema.sql`, `db.py` | DBのテーブルと接続 |
| `services/exp.py` | 経験値・進化の計算 |
| `services/questions.py` | 問題テンプレートと正解の計算 |
| `services/ai_client.py` | AIの呼び出し口(いまは仮の返事。ここだけ本物に置き換える) |
| `main.py`, `templates/`, `static/` | 前につくったFlaskのデモ画面(使わなくなったら消してよい) |

## API(ヘッダー `X-User-Id` でユーザーを見分ける。`POST /api/users` だけ不要)
| メソッド | URL | 内容 |
|---|---|---|
| POST | `/api/users` | はじめる(ニックネーム、最初の卵をわたす)→ `user_id` |
| GET | `/api/me` | ニックネームとモンスター一覧 |
| POST | `/api/units/<単元>/open` | 単元を開く(その単元の卵がなければもらう) |
| PATCH | `/api/units/<単元>/monster` | モンスターの名前を変える(8文字まで) |
| POST | `/api/units/<単元>/teach` | 説明を送る → モンスターの返事 |
| GET | `/api/units/<単元>/notes` | ノート |
| POST | `/api/units/<単元>/tests` | テスト開始(3回以上教えたあと)→ 問題5問+モンスターの答案 |
| POST | `/api/tests/<id>/items/<番号>/grade` | 「答え合わせ」(○×を送る → 正解と、採点が合ったか) |
| POST | `/api/tests/<id>/finish` | 結果(経験値・進化・不正解の一覧) |
| DELETE | `/api/tests/<id>` | やめる(途中のテストを捨てる) |
| GET | `/api/history` | 学習履歴 |

単元の番号: 1=正負の数、2=文字と式、3=方程式

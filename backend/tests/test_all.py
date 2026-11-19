"""動作確認。実行:  python -m unittest discover -s tests   (backendフォルダで)"""

import os
import random
import sys
import tempfile
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app          # noqa: E402
from services import exp, questions  # noqa: E402


class ExpTest(unittest.TestCase):
    def test_stage(self):
        self.assertEqual([exp.stage_for_exp(x) for x in (0, 29, 30, 99, 100, 179, 180, 999)],
                         [0, 0, 1, 1, 2, 2, 3, 3])

    def test_gain(self):
        self.assertEqual(exp.exp_gain(4, 5), 40)
        self.assertEqual(exp.exp_gain(5, 5), 60)   # 全問で最大60
        self.assertEqual(exp.exp_gain(0, 5), 0)

    def test_progress(self):
        self.assertEqual(exp.progress(40)["percent"], 14)
        self.assertEqual(exp.progress(40)["rest"], 60)
        self.assertEqual(exp.progress(200)["percent"], 100)


class QuestionTest(unittest.TestCase):
    def test_answers_are_integers_and_unique(self):
        rng = random.Random(1)
        for unit in (1, 2, 3):
            for _ in range(200):
                items = questions.generate_test(unit, 5, rng)
                self.assertEqual(len({i["text"] for i in items}), 5)
                for i in items:
                    int(i["answer"])

    def test_equation_answers_satisfy_equation(self):
        """方程式は、答えを代入して両辺が等しいか、別の方法で確かめる"""
        import re
        rng = random.Random(2)
        for _ in range(300):
            for it in questions.generate_test(3, 5, rng):
                eq = it["text"].split("方程式 ")[1].split(" を解きなさい")[0]
                eq = eq.replace("−", "-")
                left, right = eq.split(" = ")
                x = Fraction(it["answer"])

                def val(expr):
                    expr = expr.replace(" ", "")
                    total = Fraction(0)
                    for sign, num, var in re.findall(r"([+-]?)(\d+)(x?)", expr):
                        n = Fraction(num) * (x if var else 1)
                        total += -n if sign == "-" else n
                    return total

                self.assertEqual(val(left), val(right), it["text"])

    def test_normalize(self):
        self.assertTrue(questions.is_same_answer("−3", "-3"))
        self.assertTrue(questions.is_same_answer(" ３ ", "3"))
        self.assertTrue(questions.is_same_answer("x = -4", "-4"))
        self.assertFalse(questions.is_same_answer("3", "-3"))


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(os.path.join(self.tmp.name, "t.db"))
        self.c = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def start(self, nickname="たろう"):
        r = self.c.post("/api/users", json={"nickname": nickname})
        self.assertEqual(r.status_code, 201)
        self.h = {"X-User-Id": r.get_json()["user_id"]}
        return r.get_json()

    def call(self, method, url, **kw):
        return getattr(self.c, method)(url, headers=self.h, **kw)

    def teach(self, n=3, unit=1):
        for i in range(n):
            r = self.call("post", f"/api/units/{unit}/teach", json={"message": f"説明{i}"})
            self.assertEqual(r.status_code, 200)
        return r.get_json()

    def test_register(self):
        self.assertEqual(self.start("")["nickname"], "ななしさん")
        me = self.call("get", "/api/me").get_json()
        self.assertEqual(len(me["monsters"]), 1)
        self.assertEqual(me["monsters"][0]["name"], "タマゴ")
        r = self.c.post("/api/users", json={"nickname": "あ" * 11})
        self.assertEqual(r.status_code, 400)

    def test_no_user(self):
        self.assertEqual(self.c.get("/api/me").status_code, 401)

    def test_open_unit_and_rename(self):
        self.start()
        r = self.call("post", "/api/units/2/open")
        self.assertEqual(r.get_json()["unit_name"], "文字と式")
        self.assertEqual(len(self.call("get", "/api/me").get_json()["monsters"]), 2)
        self.assertEqual(self.call("patch", "/api/units/1/monster", json={"name": ""}).status_code, 400)
        self.assertEqual(self.call("patch", "/api/units/1/monster", json={"name": "あ" * 9}).status_code, 400)
        r = self.call("patch", "/api/units/1/monster", json={"name": "ガクタロウ"})
        self.assertEqual(r.get_json()["name"], "ガクタロウ")

    def test_test_needs_three_sends(self):
        self.start()
        self.teach(2)
        self.assertEqual(self.call("post", "/api/units/1/tests", json={}).status_code, 409)
        d = self.teach(1)
        self.assertTrue(d["can_test"])
        self.assertEqual(self.call("post", "/api/units/1/tests", json={}).status_code, 201)

    def play(self, marks_all_match=True):
        """テストを1回通して遊ぶ。採点はいつも正しい(合っている)ようにする"""
        t = self.call("post", "/api/units/1/tests", json={}).get_json()
        self.assertEqual(len(t["questions"]), 5)
        self.assertNotIn("correct_answer", t["questions"][0])
        for q in t["questions"]:
            # 本当の正誤はサーバーしか知らないので、まず○で答え合わせ→合っていなければ検証だけ
            r = self.call("post", f"/api/tests/{t['test_id']}/items/{q['no']}/grade", json={"mark": "maru"})
            self.assertEqual(r.status_code, 200)
            g = r.get_json()
            self.assertEqual(g["is_match"], g["is_monster_correct"])   # ○なら、正解のときだけ合っている
            again = self.call("post", f"/api/tests/{t['test_id']}/items/{q['no']}/grade", json={"mark": "batsu"})
            self.assertEqual(again.status_code, 409)   # 答え合わせのあとは変えられない
        return t["test_id"]

    def test_full_flow_and_exp(self):
        self.start()
        self.teach(3)
        tid = self.play()
        r = self.call("post", f"/api/tests/{tid}/finish", json={"hatch_name": "ガクタロウ"})
        self.assertEqual(r.status_code, 200)
        d = r.get_json()
        self.assertEqual(d["exp_gained"], exp.exp_gain(d["match_count"], 5))
        self.assertEqual(d["monster"]["exp"], d["exp_gained"])
        if d["exp_gained"] >= 30:
            self.assertTrue(d["hatched"])
            self.assertEqual(d["monster"]["name"], "ガクタロウ")
        self.assertEqual(len(d["wrong_items"]), 5 - d["correct_count"])
        # 終わったテストは、もう一度終えられない
        self.assertEqual(self.call("post", f"/api/tests/{tid}/finish", json={}).status_code, 404)
        # テストのあとは、また3回教えるまで受けられない
        self.assertEqual(self.call("post", "/api/units/1/tests", json={}).status_code, 409)
        h = self.call("get", "/api/history").get_json()
        self.assertEqual(h["test_count"], 1)
        self.assertEqual(h["teach_count"], 3)
        self.assertEqual(len(h["weak_points"]), 5 - d["correct_count"])

    def test_cannot_finish_before_grading(self):
        self.start()
        self.teach(3)
        t = self.call("post", "/api/units/1/tests", json={}).get_json()
        self.assertEqual(self.call("post", f"/api/tests/{t['test_id']}/finish", json={}).status_code, 400)

    def test_quit_discards(self):
        self.start()
        self.teach(3)
        t = self.call("post", "/api/units/1/tests", json={}).get_json()
        self.call("post", f"/api/tests/{t['test_id']}/items/1/grade", json={"mark": "maru"})
        self.assertEqual(self.call("delete", f"/api/tests/{t['test_id']}").status_code, 200)
        self.assertEqual(self.call("get", "/api/history").get_json()["test_count"], 0)
        # ノートは残っていて、すぐ受け直せる
        self.assertEqual(len(self.call("get", "/api/units/1/notes").get_json()["notes"]), 3)
        self.assertEqual(self.call("post", "/api/units/1/tests", json={}).status_code, 201)

    def test_other_users_test_is_hidden(self):
        self.start()
        self.teach(3)
        t = self.call("post", "/api/units/1/tests", json={}).get_json()
        self.start("べつの人")
        r = self.call("post", f"/api/tests/{t['test_id']}/items/1/grade", json={"mark": "maru"})
        self.assertEqual(r.status_code, 404)

    def test_frontend_is_served(self):
        self.assertEqual(self.c.get("/").status_code, 302)


if __name__ == "__main__":
    unittest.main()

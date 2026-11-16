from flask import Flask, render_template, abort, request

app = Flask(__name__)

# 学年ごとの単元。active=True の単元だけ「教える」を押せる(最初は中1の3単元)
GRADES = {
    1: {"title": "中学1年", "units": [
        ("正負の数", True), ("文字と式", True), ("方程式", True),
        ("比例と反比例", False), ("平面図形", False), ("空間図形", False),
        ("資料の分析と活用", False)]},
    2: {"title": "中学2年", "units": [
        ("式の計算", False), ("連立方程式", False), ("1次関数", False),
        ("平行と合同", False), ("三角形と四角形", False), ("確率", False)]},
    3: {"title": "中学3年", "units": [
        ("多項式", False), ("平方根", False), ("2次方程式", False), ("関数", False),
        ("相似な図形", False), ("円", False), ("三平方の定理", False),
        ("標本調査", False)]},
}

# 仮のデータ(あとでDBから取る)
DUMMY_MONSTER = {"name": "タマゴ", "exp": 12, "next_exp": 30}


@app.route("/")
def index():
    return home()


@app.route("/home")
def home():
    m = DUMMY_MONSTER
    percent = int(m["exp"] / m["next_exp"] * 100)
    return render_template("home.html", active="ホーム", monster=m,
                           percent=percent, grades=GRADES)


@app.route("/grade/<int:grade>")
def grade(grade):
    if grade not in GRADES:
        abort(404)
    return render_template("grade.html", active="ホーム", grade=grade,
                           info=GRADES[grade])


@app.route("/chat")
def chat():
    unit = request.args.get("unit", "正負の数")
    back = request.args.get("grade", 1, type=int)
    return render_template("chat.html", active="ホーム", unit=unit, back=back)


def coming_soon(title, active):
    return render_template("coming_soon.html", active=active, title=title)


@app.route("/monster")
def monster():
    return coming_soon("モンスター育成(W06)", "モンスター")


@app.route("/history")
def history():
    return coming_soon("学習履歴(W07)", "学習履歴")


@app.route("/library")
def library():
    return coming_soon("図鑑(W08)", "図鑑")


@app.route("/test")
def test():
    return coming_soon("テストと採点(W04)", "ホーム")


if __name__ == "__main__":
    app.run(debug=True)

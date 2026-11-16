/* =====================
   モンスター得点取得
===================== */

const score =
    Number(
        localStorage.getItem(
            "monsterScore"
        ) || 0
    );

document
    .getElementById("monsterScore")
    .textContent = score;


/* =====================
   獲得経験値計算
===================== */

/*
1問10EXP
*/
const exp = score * 10;

document
    .getElementById("expPoint")
    .textContent = exp;


/* =====================
   間違えた問題取得
===================== */

const mistakes =
    JSON.parse(
        localStorage.getItem(
            "mistakes"
        )
    ) || [];


/* =====================
   間違い問題表示
===================== */

const mistakeList =
    document.getElementById(
        "mistakeList"
    );


/*
全部正解の場合
*/
if(mistakes.length === 0){

    const div =
        document.createElement("div");

    div.classList.add(
        "mistake-item"
    );

    div.innerHTML = `
        <p>
            おめでとう！
            間違えた問題はありません。
        </p>
    `;

    mistakeList.appendChild(div);

}


/*
間違えた問題表示
*/
mistakes.forEach((m, index) => {

    const div =
        document.createElement("div");

    div.classList.add(
        "mistake-item"
    );

    div.innerHTML = `

        <h3>
            間違えた問題 ${index + 1}
        </h3>

        <p>
            <strong>問題</strong>
            ：${m.question}
        </p>

        <p>
            <strong>モンスター回答</strong>
            ：${m.monsterAnswer}
        </p>

        <p>
            <strong>正解</strong>
            ：${m.correctAnswer}
        </p>

        <p>
            <strong>理由</strong>
            ：${m.reason}
        </p>

    `;

    mistakeList.appendChild(div);

});


/* =====================
   ホームへ戻る
===================== */

document
    .getElementById("homeButton")
    .addEventListener("click", () => {

        location.href =
            "home.html";

    });


/* =====================
   デバッグ用
===================== */

console.log(
    "モンスター得点",
    score
);

console.log(
    "間違い問題",
    mistakes
);

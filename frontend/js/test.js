
const questions = [
    {
        question: "-3 + 5 = ?",
        answer: "2"
    },
    {
        question: "-3 - 5 = ?",
        answer: "-8"
    },
    {
        question: "4 + (-7) = ?",
        answer: "-3"
    },
    {
        question: "-2 × 3 = ?",
        answer: "-6"
    },
    {
        question: "-10 + 8 = ?",
        answer: "-2"
    }
];

/* =====================
   状態管理
===================== */

let currentIndex = 0;
let score = 0;
let mistakes = [];
let judged = false;

const understanding = 80;

/* =====================
   要素取得
===================== */

const correctBtn =
    document.getElementById("correctBtn");

const wrongBtn =
    document.getElementById("wrongBtn");

const nextButton =
    document.getElementById("nextButton");

/* =====================
   初期表示
===================== */

loadQuestion();

/* =====================
   問題表示
===================== */

function loadQuestion() {

    judged = false;

    correctBtn.disabled = false;
    wrongBtn.disabled = false;

    correctBtn.classList.remove(
        "selected-correct"
    );

    wrongBtn.classList.remove(
        "selected-wrong"
    );

    document
    .querySelectorAll(".reason-btn")
    .forEach(btn => {

        btn.classList.remove(
            "selected-reason"
        );

        btn.disabled = false;

    });

    document.getElementById(
        "reasonArea"
    ).style.display = "none";

    const q = questions[currentIndex];

    document.getElementById(
        "questionText"
    ).textContent = q.question;

    document.getElementById(
        "questionCount"
    ).textContent =
        `${currentIndex + 1} / ${questions.length}問`;

    const progress =
        ((currentIndex + 1) /
            questions.length) * 100;

    document.getElementById(
        "progressFill"
    ).style.width =
        `${progress}%`;

    createMonsterAnswer(q);
}

/* =====================
   モンスター回答生成
===================== */

function createMonsterAnswer(q) {

    const rand =
        Math.random() * 100;

    let answer;

    if (rand <= understanding) {

        answer = q.answer;

    } else {

        const wrongAnswers = [
            "-2",
            "8",
            "-8",
            "3",
            "5",
            "-5",
            "6"
        ];

        answer =
            wrongAnswers[
                Math.floor(
                    Math.random() *
                    wrongAnswers.length
                )
            ];
    }

    document.getElementById(
        "monsterAnswer"
    ).textContent =
        `答え：${answer}`;

    document.getElementById(
        "monsterReason"
    ).textContent =
        "考え方：ノートを参考にしました";
}

/* =====================
   ○採点
===================== */

correctBtn.addEventListener(
    "click",
    () => {

        if (judged) {
            return;
        }

        judged = true;

        score++;

        correctBtn.classList.add(
            "selected-correct"
        );

        correctBtn.disabled = true;
        wrongBtn.disabled = true;
    }
);

/* =====================
   ×採点
===================== */

wrongBtn.addEventListener(
    "click",
    () => {

        if (judged) {
            return;
        }

        wrongBtn.classList.add(
            "selected-wrong"
        );

        document.getElementById(
            "reasonArea"
        ).style.display = "flex";
    }
);

/* =====================
   理由選択
===================== */

document
.querySelectorAll(".reason-btn")
.forEach(button => {

    button.addEventListener(
        "click",
        () => {

            if (judged) {
                return;
            }

            const q =
                questions[currentIndex];

            const monsterAnswer =
                document
                .getElementById(
                    "monsterAnswer"
                )
                .textContent
                .replace(
                    "答え：",
                    ""
                );

            mistakes.push({

                question:
                    q.question,

                monsterAnswer:
                    monsterAnswer,

                correctAnswer:
                    q.answer,

                reason:
                    button.textContent

            });

            document
            .querySelectorAll(".reason-btn")
            .forEach(btn => {

                btn.classList.remove(
                    "selected-reason"
                );

            });

            button.classList.add(
                "selected-reason"
            );

            judged = true;

            wrongBtn.classList.add(
                "selected-wrong"
            );

            correctBtn.disabled = true;
            wrongBtn.disabled = true;

            document
            .querySelectorAll(".reason-btn")
            .forEach(btn => {

                btn.disabled = true;

            });

        }
    );
});

/* =====================
   次へ
===================== */

nextButton.addEventListener(
    "click",
    () => {

        if (!judged) {

            alert(
                "○または×で採点してください。"
            );

            return;
        }

        currentIndex++;

        if (
            currentIndex >=
            questions.length
        ) {

            localStorage.setItem(
                "monsterScore",
                score
            );

            localStorage.setItem(
                "mistakes",
                JSON.stringify(
                    mistakes
                )
            );

            // =====================
            // テスト回数をカウント
            // =====================

            let testCount =
                Number(
                    localStorage.getItem("testCount")
                ) || 0;

            testCount++;

            localStorage.setItem(
                "testCount",
                testCount
            );

            // =====================
            // 結果画面へ移動
            // =====================

            location.href =
                "result.html";

            return;
        }

        loadQuestion();
    }
);

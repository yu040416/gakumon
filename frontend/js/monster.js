/* ===== モンスター育成画面(W06) ===== */

/* 段階の名前・絵の種類・必要な累計経験値(卵→赤ちゃん30、赤ちゃん→成長100、成長→大人180) */
const STAGES = [
    { name: "卵",     key: "egg",   need: 0 },
    { name: "赤ちゃん", key: "baby",  need: 30 },
    { name: "成長",   key: "grow",  need: 100 },
    { name: "大人",   key: "adult", need: 180 }
];

/* 仮のデータ(あとでサーバーから取る) */
const monsters = {
    "正負の数": { name: "チビモン", exp: 40 },
    "文字と式": { name: "タマゴ",   exp: 0 },
    "方程式":   { name: "タマゴ",   exp: 0 }
};

let currentUnit = "正負の数";

/* ===== モンスターの絵(SVG) ===== */

function monsterSvg(key, size){

    const parts = {
        egg:
            '<ellipse cx="60" cy="68" rx="38" ry="48" fill="#FFF6E0" stroke="#0B4F5C" stroke-width="3"/>' +
            '<circle cx="46" cy="58" r="6" fill="#F2A33A"/>' +
            '<circle cx="72" cy="82" r="7" fill="#F2A33A"/>' +
            '<circle cx="68" cy="50" r="4" fill="#F2A33A"/>',
        baby:
            '<ellipse cx="60" cy="72" rx="40" ry="38" fill="#BFE6DF" stroke="#0B4F5C" stroke-width="3"/>' +
            '<circle cx="46" cy="66" r="5" fill="#1B2A2F"/>' +
            '<circle cx="74" cy="66" r="5" fill="#1B2A2F"/>' +
            '<path d="M50 82 Q60 90 70 82" stroke="#1B2A2F" stroke-width="3" fill="none"/>',
        grow:
            '<path d="M30 40 L38 14 L50 36 Z" fill="#8FD0C4" stroke="#0B4F5C" stroke-width="3"/>' +
            '<path d="M90 40 L82 14 L70 36 Z" fill="#8FD0C4" stroke="#0B4F5C" stroke-width="3"/>' +
            '<ellipse cx="60" cy="70" rx="42" ry="42" fill="#8FD0C4" stroke="#0B4F5C" stroke-width="3"/>' +
            '<circle cx="45" cy="64" r="5" fill="#1B2A2F"/>' +
            '<circle cx="75" cy="64" r="5" fill="#1B2A2F"/>' +
            '<path d="M48 82 Q60 92 72 82" stroke="#1B2A2F" stroke-width="3" fill="none"/>',
        adult:
            '<path d="M28 44 L30 6 L52 34 Z" fill="#F2A33A" stroke="#0B4F5C" stroke-width="3"/>' +
            '<path d="M92 44 L90 6 L68 34 Z" fill="#F2A33A" stroke="#0B4F5C" stroke-width="3"/>' +
            '<ellipse cx="60" cy="72" rx="46" ry="42" fill="#5FB8A8" stroke="#0B4F5C" stroke-width="3"/>' +
            '<circle cx="44" cy="64" r="6" fill="#1B2A2F"/>' +
            '<circle cx="76" cy="64" r="6" fill="#1B2A2F"/>' +
            '<path d="M44 84 Q60 98 76 84" stroke="#1B2A2F" stroke-width="3" fill="none"/>'
    };

    return `<svg width="${size}" height="${size}" viewBox="0 0 120 120" role="img" aria-label="モンスター">${parts[key]}</svg>`;
}

/* ===== 経験値から段階を求める ===== */

function getStageIndex(exp){

    let index = 0;

    STAGES.forEach((stage, i) => {
        if(exp >= stage.need){
            index = i;
        }
    });

    return index;
}

/* ===== 保存した名前を読む・書く ===== */

function loadName(unit){

    try{
        const saved = localStorage.getItem("monsterName_" + unit);
        if(saved){
            return saved;
        }
    }
    catch(e){
        // 保存できないブラウザでは、仮の名前のまま使う
    }

    return monsters[unit].name;
}

function saveName(unit, name){

    try{
        localStorage.setItem("monsterName_" + unit, name);
    }
    catch(e){
        // 保存できなくても、画面は動かす
    }

    monsters[unit].name = name;
}

/* ===== ⑦ 単元の切り替えボタン ===== */

function renderTabs(){

    const tabs = document.getElementById("unitTabs");
    tabs.innerHTML = "";

    Object.keys(monsters).forEach(unit => {

        const button = document.createElement("button");

        button.type = "button";
        button.className = "unit-tab";
        button.textContent = unit;

        if(unit === currentUnit){
            button.classList.add("selected");
        }

        button.addEventListener("click", () => {
            currentUnit = unit;
            render();
        });

        tabs.appendChild(button);
    });
}

/* ===== 画面全体を描く ===== */

function render(){

    const m = monsters[currentUnit];
    const stageIndex = getStageIndex(m.exp);

    renderTabs();

    // ③ 絵
    document.getElementById("monsterPicture").innerHTML =
        monsterSvg(STAGES[stageIndex].key, 200);

    // ④ 名前
    document.getElementById("monsterName").value = loadName(currentUnit);
    document.getElementById("nameMessage").textContent = "";

    // ⑤ 段階の表示
    const list = document.getElementById("stageList");
    list.innerHTML = "";

    STAGES.forEach((stage, i) => {

        const item = document.createElement("li");

        item.className = "stage-item";

        if(i === stageIndex){
            item.classList.add("current");
        }

        item.innerHTML =
            monsterSvg(stage.key, 48) +
            `<span class="stage-name">${stage.name}</span>` +
            `<span class="stage-exp">${stage.need}〜</span>`;

        list.appendChild(item);
    });

    // ⑥ 経験値バー
    const expText = document.getElementById("expText");
    const expFill = document.getElementById("expFill");

    if(stageIndex < STAGES.length - 1){

        const lo = STAGES[stageIndex].need;
        const hi = STAGES[stageIndex + 1].need;
        const percent = Math.floor((m.exp - lo) / (hi - lo) * 100);

        expText.textContent =
            `次の段階まで あと ${hi - m.exp} EXP(${m.exp} / ${hi})`;

        expFill.style.width = percent + "%";
    }
    else{

        expText.textContent = `大人になったよ!(${m.exp} EXP)`;

        expFill.style.width = "100%";
    }

        /* 教えるボタン */

    const gradeMap = {

    "正負の数": 1,
    "文字と式": 1,
    "方程式": 1,
    "比例と反比例": 1,
    "平面図形": 1,
    "空間図形": 1,
    "資料の分析と活用": 1,

    "式の計算": 2,
    "連立方程式": 2,
    "1次関数": 2,
    "平行と合同": 2,
    "三角形と四角形": 2,
    "確率": 2,

    "多項式": 3,
    "平方根": 3,
    "2次方程式": 3,
    "関数": 3,
    "相似な図形": 3,
    "円": 3,
    "三平方の定理": 3,
    "標本調査": 3
};

    document.getElementById(
        "teachButton"
    ).href =
        `chat.html?grade=${gradeMap[currentUnit]}&unit=${encodeURIComponent(currentUnit)}`;
}

/* ===== ④ 名前を変える ===== */

document.getElementById("nameButton").addEventListener("click", () => {

    const input = document.getElementById("monsterName");
    const message = document.getElementById("nameMessage");
    const name = input.value.trim();

    if(name === "" || name.length > 8){
        message.textContent = "名前は1〜8文字で入れてね";
        return;
    }

    saveName(currentUnit, name);

    message.textContent = "名前を変えたよ";
});

render();

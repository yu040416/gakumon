const sendButton = document.getElementById("sendButton");
const chatInput = document.getElementById("chatInput");
const chatBox = document.getElementById("chatBox");

let isDirty = false;

/* =====================
   URLパラメータ取得
===================== */

const params = new URLSearchParams(window.location.search);

const grade = params.get("grade");
const unit = params.get("unit");

/* =====================
   理解度管理
===================== */

function getUnderstandingKey(){

    return `understanding_${unit}`;

}

function getUnderstanding(){

    return Number(
        localStorage.getItem(
            getUnderstandingKey()
        )
    ) || 0;

}

function saveUnderstanding(value){

    localStorage.setItem(
        getUnderstandingKey(),
        Math.min(value, 100)
    );

}

/* =====================
   単元名表示
===================== */

if (unit) {

    document.querySelector(".subject-title").textContent = unit;

    const firstMessage =
        document.querySelector(".monster .bubble");

    firstMessage.textContent =
        `${unit}について教えて！`;

    localStorage.setItem("currentGrade", grade);
    localStorage.setItem("currentUnit", unit);
}


/* =====================
   メッセージ送信
===================== */

sendButton.addEventListener("click", sendMessage);

chatInput.addEventListener("keypress", function(event){

    if(event.key === "Enter"){
        sendMessage();
    }

});

function sendMessage(){

    const message = chatInput.value.trim();

    if(message === ""){
        return;
    }

    let understanding =
    getUnderstanding();

    /* 理解度上昇 */
    
    if(message.length >= 10){
    
        understanding += 3;
    
    }
    else{
    
        understanding += 1;
    
    }
    
    saveUnderstanding(
        understanding
    );
    
    updateUnderstandingText();
    updateTestButton();

    addMessage(message, "user");

    chatInput.value = "";

    isDirty = true;

    document.getElementById("saveStatus")
        .textContent = "● 学習中";

    setTimeout(() => {

        let reply;

        if(message.includes("負の数")){

            reply = "負の数って0より小さい数なんだね！";

        }
        else if(message.includes("正の数")){

            reply = "正の数は0より大きい数かな？";

        }
        else if(message.includes("文字式")){

            reply = "文字式って数字の代わりに文字を使うんだね！";

        }
        else{

            const responses = [
                "なるほど！",
                "もっと詳しく教えて！",
                "それってどういう意味？",
                "少し分かってきたよ！",
                "例も教えて！"
            ];

            reply =
                responses[
                    Math.floor(
                        Math.random() * responses.length
                    )
                ];

        }

        addMessage(reply, "monster");

    }, 500);

}


/* =====================
   吹き出し追加
===================== */

function addMessage(text, type){

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add("message");
    messageDiv.classList.add(type);

    const bubble =
        document.createElement("div");

    bubble.classList.add("bubble");
    bubble.textContent = text;

    messageDiv.appendChild(bubble);

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop =
        chatBox.scrollHeight;

}


/* =====================
   記号ボタン
===================== */

document
.querySelectorAll(".symbol-btn")
.forEach(button => {

    button.addEventListener("click", () => {

        chatInput.value += button.textContent;

        chatInput.focus();

    });

});


/* =====================
   保存処理
===================== */

function saveChat(){

    if(!isDirty){

        document.getElementById("saveStatus")
            .textContent = "✓ 保存済み";

        return;
    }

    document.getElementById("saveStatus")
        .textContent = "⟳ 保存中...";

    setTimeout(() => {

        document.getElementById("saveStatus")
            .textContent = "✓ 保存済み";

        isDirty = false;

    }, 1000);

}


/* =====================
   戻るボタン
===================== */

document
.getElementById("backButton")
.addEventListener("click", () => {

    saveChat();

    const currentGrade =
        localStorage.getItem("currentGrade");

    setTimeout(() => {

        location.href =
            `grade${currentGrade}.html`;

    }, 1000);

});


/* =====================
   学習終了ボタン
===================== */

document
.getElementById("finishButton")
.addEventListener("click", () => {

    saveChat();

    setTimeout(() => {

        alert(
            "会話履歴を保存しました。\nノートを更新します。"
        );

        location.href = "home.html";

    }, 1000);

});


/* =====================
   サイドバー移動時
===================== */

document
.querySelectorAll(".menu a")
.forEach(link => {

    link.addEventListener("click", (e) => {

        e.preventDefault();

        saveChat();

        setTimeout(() => {

            location.href =
                link.getAttribute("href");

        }, 1000);

    });

});

/* =====================
   テストボタン
===================== */

const testButton =
    document.getElementById("testButton");


function updateUnderstandingText(){

    document
        .getElementById(
            "understandingText"
        )
        .textContent =
        `理解度：${getUnderstanding()}%`;

}

/*
 テストボタン制御
*/
updateTestButton();
updateUnderstandingText();

function updateTestButton(){

    const understanding =
        getUnderstanding();

    if(understanding >= 2){

        testButton.disabled = false;

        testButton.title =
            "";

    }
    else{

        testButton.disabled = true;

        testButton.title =
            "理解度5%以上で受験できます";

    }

}

testButton.addEventListener("click", () => {

    if(testButton.disabled){
        return;
    }

    location.href = "test.html";

});


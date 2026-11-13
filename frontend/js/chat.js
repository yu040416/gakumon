const sendButton = document.getElementById("sendButton");
const chatInput = document.getElementById("chatInput");
const chatBox = document.getElementById("chatBox");

let isDirty = false;

/* 単元名取得 */

const params = new URLSearchParams(window.location.search);

const unit = params.get("unit");

if(unit){

    document.querySelector(".subject-title").textContent = unit;

    const firstMessage =
        document.querySelector(".monster .bubble");

    firstMessage.textContent =
        `${unit}について教えて！`;
}

/* メッセージ送信 */

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

    addMessage(message,"user");

    chatInput.value = "";

    isDirty = true;

    setTimeout(() => {

        let reply;

        if(message.includes("負の数")){
            reply =
                "負の数って0より小さい数なんだね！";
        }
        else if(message.includes("正の数")){
            reply =
                "正の数は0より大きい数かな？";
        }
        else if(message.includes("文字式")){
            reply =
                "文字式って数字の代わりに文字を使うんだね！";
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
                        Math.random() *
                        responses.length
                    )
                ];
        }

        addMessage(reply,"monster");

    },500);

}

/* 吹き出し追加 */

function addMessage(text,type){

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

/* 記号ボタン */

document
.querySelectorAll(".symbol-btn")
.forEach(button => {

    button.addEventListener("click", () => {

        chatInput.value +=
            button.textContent;

        chatInput.focus();

    });

});

/* 学習終了 */

document
.querySelector(".test-btn")
.addEventListener("click", () => {

    alert(
        "会話履歴を保存しました。\nノートを更新します。"
    );

    location.href = "home.html";

});

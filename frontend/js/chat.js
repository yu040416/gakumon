const sendButton = document.getElementById("sendButton");
const chatInput = document.getElementById("chatInput");
const chatBox = document.getElementById("chatBox");

sendButton.addEventListener("click", sendMessage);

//OpenAI APIが有料のため開発初期は固定メッセージを使用
function sendMessage() {

    const message = chatInput.value.trim();

    if(message === ""){
        return;
    }

    // ユーザー吹き出し
    addMessage(message, "user");

    // 入力欄クリア
    chatInput.value = "";

   // モンスター返答候補
const responses = [
    "なるほど！",
    "もっと詳しく教えて！",
    "それってどういう意味？",
    "少し分かってきた！"
];

// ランダム選択
setTimeout(() => {

    let reply = "";

    if(message.includes("負の数")){
        reply = "負の数って0より小さい数だよね？";
    }
    else if(message.includes("正の数")){
        reply = "正の数は0より大きい数かな？";
    }
    else if(message.includes("文字式")){
        reply = "文字式って数字の代わりに文字を使うんだよね？";
    }
    else{

        const responses = [
            "なるほど！",
            "もっと詳しく教えて！",
            "それってどういう意味？",
            "少し分かってきた！"
        ];

        reply =
            responses[Math.floor(Math.random() * responses.length)];
    }

    addMessage(reply, "monster");

}, 500);


}

function addMessage(text, type){

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageDiv.classList.add(type);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.textContent = text;

    messageDiv.appendChild(bubble);
    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}
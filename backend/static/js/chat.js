const sendButton = document.getElementById("sendButton");
const chatInput = document.getElementById("chatInput");
const chatBox = document.getElementById("chatBox");
const testButton = document.getElementById("testButton");
const testHint = document.getElementById("testHint");

/* テストを受けさせるまでに必要な送信回数 */
const REQUIRED_SENDS = 3;
let sendCount = 0;

/* メッセージ送信 */

sendButton.addEventListener("click", sendMessage);

chatInput.addEventListener("keydown", function(event){

    // 日本語変換の確定のEnterでは送信しない
    if(event.key === "Enter" && !event.isComposing){
        sendMessage();
    }

});

function sendMessage(){

    const message = chatInput.value.trim();

    if(message === ""){
        return;
    }

    addMessage(message, "user");

    chatInput.value = "";

    sendCount++;
    updateTestButton();

    // 仮の返事(あとでAIの返事に置き換える)
    setTimeout(() => {

        let reply;

        if(message.includes("負の数")){
            reply = "負の数って0より小さい数なんだね！";
        }
        else if(message.includes("正の数")){
            reply = "正の数は0より大きい数かな？";
        }
        else if(message.includes("文字式") || message.includes("文字と式")){
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

            reply = responses[Math.floor(Math.random() * responses.length)];
        }

        addMessage(reply, "monster");

    }, 500);

}

/* 3回以上送ったらテストボタンを押せるようにする */

function updateTestButton(){

    const rest = REQUIRED_SENDS - sendCount;

    if(rest <= 0){
        testButton.disabled = false;
        testHint.textContent = "テストを受けさせられるよ！";
    }
    else{
        testHint.textContent =
            `あと${rest}回教えると、テストを受けさせられるよ`;
    }
}

testButton.addEventListener("click", () => {

    if(testButton.disabled){
        return;
    }

    // テスト画面(W04)ができたら、ここで移動する
    location.href = testButton.dataset.url;

});

/* 吹き出し追加 */

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

/* 記号ボタン */

document.querySelectorAll(".symbol-btn").forEach(button => {

    button.addEventListener("click", () => {

        chatInput.value += button.dataset.insert;

        chatInput.focus();

    });

});

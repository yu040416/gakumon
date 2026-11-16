document.addEventListener("DOMContentLoaded", () => {

    // ユーザー名(あとでサーバー側のニックネームに置き換える)
    const userName = localStorage.getItem("userName");

    if(userName){
        document.querySelector("h1").textContent =
            `こんにちは、${userName}さん！`;
    }

});

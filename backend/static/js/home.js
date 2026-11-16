document.addEventListener("DOMContentLoaded", () => {

    // 経験値バーの長さ(HTMLの data-percent から決める)
    const fill = document.querySelector(".exp-fill");

    if(fill){
        fill.style.width = `${fill.dataset.percent}%`;
    }

    // ユーザー名(あとでサーバー側のニックネームに置き換える)
    const userName = localStorage.getItem("userName");

    if(userName){
        document.querySelector("h1").textContent =
            `こんにちは、${userName}さん！`;
    }

});


// ===================================
// 開発モード設定
// ===================================

// true  : 開発中（毎回ニックネーム入力画面を表示）
// false : 通常時（保存データがあればホーム画面へ移動）
const isDevelopment = true;


// ===================================
// 起動時の画面判定
// ===================================

// 保存されているユーザーデータを確認
const savedData = localStorage.getItem("userData");

// 通常モードの場合のみ画面判定を行う
if (!isDevelopment && savedData !== null) {
    window.location.replace("home.html");
}


// ===================================
// スタートボタンの処理
// ===================================

function startApp() {

    // 入力されたニックネームを取得
    let nickname = document.getElementById("nickname").value.trim();

    // 未入力の場合
    if (nickname === "") {
        nickname = "ななしさん";
    }

    // 10文字以内にする
    nickname = nickname.slice(0, 10);

    // 仮のユーザーデータ
    // ※将来的にはデータベースに保存する
    const userData = {
        user_id: 1,
        nickname: nickname
    };

    // データを保存
    localStorage.setItem("userData", JSON.stringify(userData));

    // ホーム画面へ移動
    window.location.href = "home.html";
}

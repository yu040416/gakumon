document.addEventListener("DOMContentLoaded", () => {

    // ユーザー名
    const userName = localStorage.getItem("userName");

    if(userName){

        const title =
            document.querySelector("h1");

        title.textContent =
            `こんにちは、${userName}さん！`;

    }

});

/* 学年選択 */

function moveGrade(grade){

    switch(grade){

        case 1:
            location.href = "grade1.html";
            break;

        case 2:
            location.href = "grade2.html";
            break;

        case 3:
            location.href = "grade3.html";
            break;

    }

}
/* 経験値バーの長さ(HTMLの data-percent から決める) */

const fill = document.querySelector(".exp-fill");

if(fill){
    fill.style.width = `${fill.dataset.percent}%`;
}

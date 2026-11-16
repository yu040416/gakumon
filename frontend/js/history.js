
// ===================================
// 学習履歴画面の初期処理
// ===================================

let accuracyChart = null;

document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
});


// ===================================
// 学習履歴の読み込み
// ===================================

async function loadHistory() {

    // -------------------------------
    // 1. テスト回数を取得
    // -------------------------------

    const testCount =
        Number(localStorage.getItem("testCount")) || 0;

    document.getElementById("test-count").textContent =
        testCount + "回";


    // -------------------------------
    // 2. DBから学習結果を取得
    // -------------------------------

    try {

        const response = await fetch("/api/test-results");

        if (!response.ok) {
            throw new Error("学習結果の取得に失敗しました");
        }

        const results = await response.json();

        if (!Array.isArray(results)) {
            throw new Error("取得したデータの形式が正しくありません");
        }


        // -------------------------------
        // 3. データが存在しない場合
        // -------------------------------

        if (results.length === 0) {

            document.getElementById("accuracy").textContent = "--";

            document.getElementById("recent-history").innerHTML =
                '<p class="no-data">学習履歴はありません。</p>';

            document.getElementById("accuracy-graph").style.display =
                "none";

            const graphContainer =
                document.querySelector(".graph-container");

            graphContainer.innerHTML =
                '<p class="no-data">グラフを表示できるデータがありません。</p>';

            return;
        }


        // -------------------------------
        // 4. 最新の正答率を表示
        // -------------------------------

        // APIから新しい順に取得する想定
        const latestAccuracy = results[0].accuracy;

        document.getElementById("accuracy").textContent =
            latestAccuracy + "%";


        // -------------------------------
        // 5. 最近の学習を表示
        // -------------------------------

        displayRecentHistory(results);


        // -------------------------------
        // 6. 正答率の折れ線グラフを表示
        // -------------------------------

        displayAccuracyGraph(results);

    } catch (error) {

        console.error("学習履歴の読み込みエラー:", error);

        document.getElementById("accuracy").textContent = "--";

        document.getElementById("recent-history").innerHTML =
            '<p class="no-data">学習履歴を取得できませんでした。</p>';

        const graphContainer =
            document.querySelector(".graph-container");

        graphContainer.innerHTML =
            '<p class="no-data">グラフを表示できませんでした。</p>';
    }
}


// ===================================
// 最近の学習を表示
// ===================================

function displayRecentHistory(results) {

    const historyArea =
        document.getElementById("recent-history");

    historyArea.innerHTML = "";

    // 新しい順に最大5件表示
    results.slice(0, 5).forEach(result => {

        const item = document.createElement("div");

        item.className = "history-item";

        const info = document.createElement("div");
        info.className = "history-info";

        const unitName = document.createElement("strong");
        unitName.textContent = result.unit_name ?? "単元名なし";

        const testDate = document.createElement("span");
        testDate.textContent = result.test_date ?? "日時不明";

        info.appendChild(unitName);
        info.appendChild(testDate);

        const score = document.createElement("div");
        score.className = "history-score";

        score.textContent =
            result.accuracy != null
                ? result.accuracy + "%"
                : "--";

        item.appendChild(info);
        item.appendChild(score);

        historyArea.appendChild(item);
    });
}


// ===================================
// 正答率の折れ線グラフを表示
// ===================================

function displayAccuracyGraph(results) {

    const graphContainer =
        document.querySelector(".graph-container");

    graphContainer.innerHTML =
        '<canvas id="accuracy-graph"></canvas>';

    const canvas =
        document.getElementById("accuracy-graph");

    // 新しい順で取得したデータを古い順に並べ替える
    const graphResults = results.slice().reverse();

    // 横軸：単元名
    const labels = graphResults.map(result => {
        return result.unit_name ?? "単元名なし";
    });

    // 縦軸：DBに保存されている正答率
    const accuracyData = graphResults.map(result => {
        return Number(result.accuracy);
    });

    // Chart.jsで折れ線グラフを作成
    if (accuracyChart) {
        accuracyChart.destroy();
    }

    accuracyChart = new Chart(canvas, {

        type: "line",

        data: {

            labels: labels,

            datasets: [{

                label: "正答率",

                data: accuracyData,

                borderColor: "#62c5e8",

                backgroundColor: "rgba(98, 197, 232, 0.15)",

                borderWidth: 3,

                pointRadius: 5,

                pointHoverRadius: 7,

                pointBackgroundColor: "#62c5e8",

                pointBorderColor: "#ffffff",

                pointBorderWidth: 2,

                tension: 0.3,

                fill: true

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            interaction: {
                intersect: false,
                mode: "index"
            },

            scales: {

                y: {

                    min: 0,

                    max: 100,

                    ticks: {

                        stepSize: 20,

                        callback: function(value) {
                            return value + "%";
                        }

                    },

                    title: {

                        display: true,

                        text: "正答率"

                    }

                },

                x: {

                    title: {

                        display: true,

                        text: "単元"

                    }

                }

            },

            plugins: {

                legend: {

                    display: true

                },

                tooltip: {

                    callbacks: {

                        label: function(context) {
                            return "正答率：" + context.parsed.y + "%";
                        },

                        afterLabel: function(context) {

                            const result =
                                graphResults[context.dataIndex];

                            return "実施日時：" +
                                (result.test_date ?? "不明");
                        }

                    }

                }

            }

        }

    });

}

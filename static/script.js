function fetchStockData() {
    const stock1 = document.getElementById("stock1").value || "Stock1";
    const max_lag = document.getElementById("max_lag").value || 10;

    fetch('/stock_sh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ stock1, max_lag })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("错误: " + data.error);
                return;
            }

            if (document.getElementById("mean_return") && data["股票平均收益率Mean Return"]) {
                document.getElementById("mean_return").innerText = data["股票平均收益率Mean Return"];
            }

            document.getElementById("text1").innerText = data.text1;
            document.getElementById("img_lag_effect").src = "data:image/png;base64," + data.img_lag_effect;

            document.getElementById("text2").innerText = data.text2;
            document.getElementById("img_rolling_correlation").src = "data:image/png;base64," + data.img_rolling_correlation;

            document.getElementById("correlation").innerText = data.correlation;
            document.getElementById("img_cor").src = "data:image/png;base64," + data.img_cor;

            document.getElementById("beta").innerText = data.beta;
            document.getElementById("mean_return").innerText = data["股票平均收益率Mean Return"];
            document.getElementById("volatility").innerText = data["股票标准差Volatility (Std Dev)"];
            document.getElementById("skewness").innerText = data["股票偏度Skewness"];
            document.getElementById("kurtosis").innerText = data["股票峰度Kurtosis"];

            document.getElementById("mean_return_sh").innerText = data["上证平均收益率Mean Return"];
            document.getElementById("volatility_sh").innerText = data["上证标准差Volatility (Std Dev)"];
            document.getElementById("skewness_sh").innerText = data["上证偏度Skewness"];
            document.getElementById("kurtosis_sh").innerText = data["上证峰度Kurtosis"];

            addHistory(stock1, max_lag);
        })
        .catch(error => console.error("请求失败:", error));
}

function addHistory(stock, lag) {
    const historyList = document.getElementById("history-list");
    const historyItem = document.createElement("div");
    historyItem.classList.add("history-item");
    historyItem.innerText = `股票: ${stock} | 滞后: ${lag}`;
    historyList.appendChild(historyItem);
}
document.addEventListener("DOMContentLoaded", function() {
    // 监听所有侧边栏链接
    document.querySelectorAll(".sidebar a").forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault(); // 阻止默认跳转
            const page = this.getAttribute("onclick").match(/'([^']+)'/)[1]; // 提取页面名称
            loadPage(page);
        });
    });

    // 监听浏览器前进/后退按钮
    window.onpopstate = function() {
        const path = window.location.pathname.replace("/", "") || "index";
        loadPage(path, false);
    };
});

function loadPage(page, pushState = true) {
    let url = page === "index" ? "/" : "/" + page; // 确保 index 加载 "/"

    fetch(url)
        .then(response => response.text())
        .then(html => {
            // 解析返回的 HTML，提取 <main> 内的内容
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newContent = doc.querySelector("main").innerHTML;

            // 更新页面内容
            const mainContent = document.getElementById("main-content");
            if (mainContent) {
                mainContent.innerHTML = newContent;
            } else {
                console.error("未找到 #main-content");
            }

            // 更新 URL，但不刷新页面
            if (pushState) {
                window.history.pushState({}, "", url);
            }
        })
        .catch(error => console.error("页面加载失败:", error));
}

// 监听浏览器前进/后退按钮
window.onpopstate = function() {
    const path = window.location.pathname.replace("/", "") || "index";
    loadPage(path, false);
};
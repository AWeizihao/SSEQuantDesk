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

            document.getElementById("text1").innerText = data.text1;
            document.getElementById("img_lag_effect").src = "data:image/png;base64," + data.img_lag_effect;

            document.getElementById("text2").innerText = data.text2;
            document.getElementById("img_rolling_correlation").src = "data:image/png;base64," + data.img_rolling_correlation;

            document.getElementById("correlation").innerText = data.correlation;
            document.getElementById("img_cor").src = "data:image/png;base64," + data.img_cor;

            document.getElementById("beta").innerText = data.bata;
            document.getElementById("mean_return").innerText = data["Mean Return"];
            document.getElementById("volatility").innerText = data["Volatility (Std Dev)"];
            document.getElementById("skewness").innerText = data["Skewness"];
            document.getElementById("kurtosis").innerText = data["Kurtosis"];
        })
        .catch(error => console.error("请求失败:", error));
}
from app import app

if __name__ == "__main__":
    try:
        from waitress import serve  # 适用于 Windows
        serve(app, host="0.0.0.0", port=5000, threads=8)
    except ImportError:
        # 如果 Windows 没安装 waitress，就用 Flask 运行（开发模式）
        app.run(debug=True)
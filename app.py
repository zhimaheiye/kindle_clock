import time
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# 全局变量维护计时器状态
# 注意：在生产环境中，如果多进程部署（如 gunicorn -w 4），全局变量不能共享。
# 但对于这个轻量级单容器应用，默认单进程运行是没问题的。
timer_state = {
    "running": False,
    "start_timestamp": 0.0,  # 记录最近一次点击“开始”时的服务器时间戳
    "elapsed": 0.0           # 记录之前已经累积的时间（秒）
}

def get_response_data():
    data = timer_state.copy()
    data["server_time"] = time.time()
    return jsonify(data)

@app.route('/')
def index():
    """Kindle 显示端页面"""
    return render_template('index.html')

@app.route('/control')
def control():
    """PC/手机 控制端页面"""
    return render_template('control.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前计时器状态"""
    return get_response_data()

@app.route('/api/start', methods=['POST'])
def start_timer():
    """开始计时"""
    global timer_state
    if not timer_state["running"]:
        timer_state["running"] = True
        # 记录当前时间戳，作为本次运行的起点
        timer_state["start_timestamp"] = time.time()
    return get_response_data()

@app.route('/api/stop', methods=['POST'])
def stop_timer():
    """暂停计时"""
    global timer_state
    if timer_state["running"]:
        timer_state["running"] = False
        # 累加本次运行的时间段到 elapsed
        current_time = time.time()
        timer_state["elapsed"] += (current_time - timer_state["start_timestamp"])
        timer_state["start_timestamp"] = 0.0
    return get_response_data()

@app.route('/api/reset', methods=['POST'])
def reset_timer():
    """重置计时"""
    global timer_state
    timer_state["running"] = False
    timer_state["start_timestamp"] = 0.0
    timer_state["elapsed"] = 0.0
    return get_response_data()

if __name__ == '__main__':
    # 监听所有 IP，端口 5000
    app.run(host='0.0.0.0', port=5000)

# Kindle Clock Project (v2.0)

本项目是一个运行在 Docker 容器内的 Kindle 桌面时钟应用。它利用 Kindle 的实验性浏览器显示实时时间、日期和自定义图片，并在此基础上增加了跨设备同步的正向计时器（秒表）功能。

## 版本对比与改进

### 第一版 (v1.0) - 纯静态页面
*   **架构**：纯前端静态 HTML/JS。
*   **功能**：
    *   显示实时时间（时:分）。
    *   显示日期。
    *   显示静态图片。
    *   每 60 秒强制刷新页面以防止 Kindle 休眠。
*   **局限性**：
    *   无法实现跨设备的状态同步（例如在手机上控制，Kindle 上显示）。
    *   功能单一，仅作为时钟使用。

### 第二版 (v2.0) - 前后端分离 (当前版本)
*   **架构**：轻量级前后端分离 (Python Flask + HTML/JS)。
*   **改进点**：
    1.  **引入后端服务**：使用 Flask 搭建后端，在内存中维护计时器的状态（运行中/暂停、开始时间、累计时长），实现了多端状态同步。
    2.  **新增计时器功能**：
        *   **显示端 (Kindle)**：新增计时器显示区域，通过轮询 (Polling) 后端接口获取状态，并基于服务器时间戳计算时长，避免了设备性能差异导致的计时误差。
        *   **控制端 (PC/手机)**：新增 `/control` 页面，提供“开始”、“暂停”、“重置”按钮，可远程控制 Kindle 上的计时器。
    3.  **资源管理优化**：将 HTML 模板 (`templates`) 和静态资源 (`static`) 分离，符合 Web 开发规范。
    4.  **容器化部署**：提供了 `Dockerfile`，基于 `python:3.9-slim` 构建，保持了轻量级的特性。

## 快速开始

### 1. 构建镜像
在项目根目录下运行：
```bash
docker build -t kindle-clock .
```

### 2. 运行容器
```bash
docker run -d -p 5000:5000 --name kindle-clock kindle-clock
```

### 3. 访问地址
*   **Kindle 显示端**：`http://<你的电脑IP>:5000/`
*   **控制面板**：`http://<你的电脑IP>:5000/control`

---

## 开发过程中的问题与解决方案

### 1. 跨设备状态同步
*   **问题**：如果仅在前端用 JS 计时，刷新页面后计时会重置，且无法在手机和 Kindle 之间同步状态。
*   **解决方案**：
    *   后端维护全局变量 `timer_state`。
    *   前端通过 `setInterval` 每秒向 `/api/status` 发起请求（轮询）。
    *   计时逻辑采用“时间戳差值法”（`当前时间 - 开始时间`），而非简单的累加，确保了计时的准确性。

### 2. Kindle 旧版浏览器兼容性
*   **问题**：Kindle 的实验性浏览器内核较老，可能不支持 ES6+ 的新特性（如 `fetch`, `arrow functions` 等）。
*   **解决方案**：
    *   前端代码尽量使用 ES5 语法（如 `var`, `function`）。
    *   AJAX 请求使用原生的 `XMLHttpRequest` 而非 `fetch`（虽然部分新版 Kindle 支持 fetch，但 XHR 更保险）。
    *   添加 `<meta name="viewport" content="width=device-width, initial-scale=1.0">` 标签，优化页面在移动设备上的渲染。

### 3. 局域网访问被拒绝 (Connection Refused / Timeout)
*   **问题**：Docker 容器启动正常，本机（localhost）可以访问，但 Kindle 或手机无法通过局域网 IP 访问。
*   **原因**：Windows 防火墙默认拦截了入站连接。
*   **解决方案**：
    *   以管理员身份运行 PowerShell，添加防火墙规则允许 5000 端口入站：
        ```powershell
        New-NetFirewallRule -DisplayName "Kindle Clock" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
        ```

### 4. Kindle 硬件性能限制
*   **问题**：在 Kindle 上，计时器虽然能显示，但无法实时更新（停留在 00:00:00）
*   **原因**：Kindle 的电子墨水屏刷新率低，且内置浏览器性能极弱，无法支撑每秒更新 DOM 的高频操作（秒级刷新负荷过大）。
*   **结论**：虽然代码逻辑支持秒级计时，但在 Kindle 实机上体验不佳。建议 Kindle 端主要作为静态时钟（显示时:分）使用，计时器功能更适合在 PC 或手机端查看。

## 目录结构
```
.
├── app.py              # Flask 后端入口
├── Dockerfile          # Docker 构建文件
├── requirements.txt    # Python 依赖
├── static/             # 静态资源目录
│   └── sunce.png       # 图片文件
└── templates/          # HTML 模板目录
    ├── index.html      # Kindle 显示页面
    └── control.html    # 控制面板页面

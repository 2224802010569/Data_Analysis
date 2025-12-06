class ApiClient {
    constructor(base = "/api") {
        this.base = base;
    }

    async getData(tf = "1d") {
        const url = `${this.base}/data?tf=${encodeURIComponent(tf)}`;
        try {
            const res = await fetch(url, { cache: "no-cache" });
            const json = await res.json();

            if (!json || json.status !== "ok" || !Array.isArray(json.data)) {
                return [];
            }

            // --- QUAN TRỌNG: Lọc dữ liệu trùng lặp và sắp xếp ---
            // Lightweight Charts cực kỳ ghét dữ liệu trùng giờ, phải lọc kỹ
            const uniqueData = new Map();
            json.data.forEach(item => {
                const time = new Date(item.timestamp).getTime();
                // Nếu trùng giờ, chỉ lấy cái mới nhất (ghi đè)
                uniqueData.set(time, item);
            });

            // Chuyển lại thành mảng và sắp xếp tăng dần
            const sortedArr = Array.from(uniqueData.values())
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

            return sortedArr;
        } catch (e) {
            console.error("Lỗi tải API:", e);
            return [];
        }
    }
}

class ChartManager {
    constructor(containerId = "chart") {
        this.container = document.getElementById(containerId);
        if (!this.container) return; // Chống lỗi nếu không tìm thấy div
        
        this.chart = null;
        this.candleSeries = null;
        this.setupChart();
    }

    setupChart() {
        this.container.innerHTML = "";
        
        // Lấy kích thước thực tế của thẻ cha
        const width = this.container.clientWidth || 800; // Fallback nếu lỗi
        const height = this.container.clientHeight || 500;

        this.chart = LightweightCharts.createChart(this.container, {
            width: width,
            height: height,
            layout: { backgroundColor: "#ffffff", textColor: "#333" },
            grid: {
                vertLines: { color: "#f0f3fa" },
                horzLines: { color: "#f0f3fa" },
            },
            rightPriceScale: {
                borderColor: '#dfe1e5',
                scaleMargins: { top: 0.1, bottom: 0.1 },
            },
            timeScale: {
                borderColor: '#dfe1e5',
                timeVisible: true,
                secondsVisible: false,
                // Fix lỗi zoom quá đà bị trắng màn hình
                minBarSpacing: 0.01, 
            },
            // Tắt scroll quán tính để tránh trượt mất biểu đồ
            kineticScroll: { touch: false, mouse: false }
        });

        // Tự động resize thông minh (Chống sập khi resize về 0)
        new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== this.container) return;
            const newRect = entries[0].contentRect;
            
            // CHỐT CHẶN: Chỉ resize nếu kích thước hợp lệ (> 0)
            if (newRect.width > 0 && newRect.height > 0) {
                this.chart.applyOptions({ height: newRect.height, width: newRect.width });
            }
        }).observe(this.container);

        this.candleSeries = this.chart.addCandlestickSeries({
            upColor: "#26a69a",
            downColor: "#ef5350",
            borderVisible: false,
            wickUpColor: "#26a69a",
            wickDownColor: "#ef5350",
        });
    }

    recToPoint(rec) {
        const t = new Date(rec.timestamp).getTime() / 1000;
        return {
            time: t,
            open: Number(rec.open),
            high: Number(rec.high),
            low: Number(rec.low),
            close: Number(rec.close),
            ai_action: rec.ai_action,
            ai_confidence: rec.ai_confidence
        };
    }

    createMarkers(dataPoints) {
        const markers = [];
        dataPoints.forEach(point => {
            if (point.ai_action === 'BUY') {
                markers.push({
                    time: point.time,
                    position: 'belowBar',
                    color: '#2196F3',
                    shape: 'arrowUp',
                    text: 'BUY'
                });
            } else if (point.ai_action === 'SELL') {
                markers.push({
                    time: point.time,
                    position: 'aboveBar',
                    color: '#e91e63',
                    shape: 'arrowDown',
                    text: 'SELL'
                });
            }
        });
        // Sắp xếp marker theo thời gian (Bắt buộc với thư viện này)
        return markers.sort((a, b) => a.time - b.time);
    }

    setAllData(arr) {
        if (!this.chart || !this.candleSeries) return;

        // Convert và lọc dữ liệu lỗi
        const points = arr
            .map(r => this.recToPoint(r))
            .filter(p => !isNaN(p.open) && !isNaN(p.time)); // Bỏ các dòng lỗi NaN

        // Cập nhật nến
        this.candleSeries.setData(points);

        // Cập nhật mũi tên
        const markers = this.createMarkers(points);
        this.candleSeries.setMarkers(markers);

        // Fit toàn bộ biểu đồ vào khung nhìn
        this.chart.timeScale().fitContent();
    }
}

class UIController {
    constructor() {
        this.api = new ApiClient("/api");
        this.chartMgr = new ChartManager("chart");
        this.tfButtons = document.querySelectorAll(".tf-btn");
        this.currentTf = "1d";
        this.init();
    }

    init() {
        this.tfButtons.forEach((btn) => {
            btn.addEventListener("click", async () => {
                const tf = btn.dataset.tf;
                if (!tf) return;
                this.tfButtons.forEach(b => {
                    b.classList.remove("active", "btn-primary");
                    b.classList.add("btn-outline-primary");
                });
                btn.classList.add("active", "btn-primary");
                btn.classList.remove("btn-outline-primary");
                await this.loadTf(tf);
            });
        });
        this.loadTf(this.currentTf);
    }

    async loadTf(tf) {
        console.log(`Đang tải dữ liệu ${tf}...`);
        const data = await this.api.getData(tf);
        
        // Cập nhật thống kê
        if (data && data.length > 0) {
            const last = data[data.length - 1];
            this.updateStats(last);
        } else {
            this.updateStats(null);
        }

        // Cập nhật biểu đồ (Kể cả khi rỗng cũng phải set để xóa chart cũ)
        this.chartMgr.setAllData(data || []);
    }

    updateStats(last) {
        const els = {
            price: document.getElementById("last-price"),
            conf: document.getElementById("forecast-price"),
            desc: document.getElementById("forecast-change"),
            rec: document.getElementById("recommend-text")
        };

        if (!last) {
            if(els.price) els.price.innerText = "$0";
            return;
        }

        if(els.price) els.price.innerText = "$" + Number(last.close).toLocaleString('en-US', {minimumFractionDigits: 2});
        
        const confidence = last.ai_confidence ? (last.ai_confidence * 100).toFixed(2) : "0.00";
        if(els.conf) els.conf.innerText = `${confidence}%`;
        if(els.desc) {
            els.desc.innerText = "Độ tin cậy AI";
            els.desc.className = "small text-muted";
        }

        const action = last.ai_action || "NONE";
        if(els.rec) {
            els.rec.innerText = action;
            els.rec.className = "h3 mb-0 fw-bold";
            if (action === "BUY") els.rec.classList.add("text-success");
            else if (action === "SELL") els.rec.classList.add("text-danger");
            else els.rec.classList.add("text-muted");
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Chỉ chạy khi có div chart để tránh lỗi ở trang khác
    if (document.getElementById("chart")) {
        window.app = new UIController();
    }
});
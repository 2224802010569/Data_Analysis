class ApiClient {
  constructor(base = "/api") {
    this.base = base;
    this.cache = new Map();
  }

  async getData(tf = "1M") {
    if (this.cache.has(tf)) {
      return this.cache.get(tf);
    }
    const url = `${this.base}/data?tf=${encodeURIComponent(tf)}`;
    const res = await fetch(url, { cache: "no-cache" });
    const json = await res.json();
    if (!json || json.status !== "ok" || !Array.isArray(json.data)) {
      return [];
    }
    // Ensure sorted ascending (old -> new)
    const arr = json.data
      .slice()
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    this.cache.set(tf, arr);
    return arr;
  }
}

class ChartManager {
  constructor(containerId = "chart") {
    this.container = document.getElementById(containerId);
    this.chart = null;
    this.candleSeries = null;
    this.allData = [];
    this.displayedCount = 0;
    this.INITIAL_COUNT = 50;
    this.INCREMENT = 20;
    this.setupChart();
  }

  setupChart() {
    this.container.innerHTML = "";
    this.chart = LightweightCharts.createChart(this.container, {
      layout: { backgroundColor: "#ffffff", textColor: "#222" },
      grid: {
        vertLines: { color: "#f0f0f0" },
        horzLines: { color: "#f0f0f0" },
      },
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.1 } },
      timeScale: { timeVisible: true, secondsVisible: false },
    });
    this._sub = this.chart
      .timeScale()
      .subscribeVisibleLogicalRangeChange((range) => {
        if (!range) return;
        if (range.from <= 0) this.tryExpand();
      });
    this.candleSeries = this.chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: true,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    this.chart.timeScale().subscribeVisibleLogicalRangeChange((range) => {
      if (!range) return;
      if (range.from <= 0) {
        this.tryExpand();
      }
    });
  }

  recToPoint(rec) {
    const t = new Date(rec.timestamp).getTime();
    return {
      time: Math.floor(t / 1000),
      open: Number(rec.open),
      high: Number(rec.high),
      low: Number(rec.low),
      close: Number(rec.close),
    };
  }

  setAllData(arr) {
    this.allData = arr;
    this.chart.removeSeries(this.candleSeries);
    this.chart.timeScale().unsubscribeVisibleLogicalRangeChange(this._sub);
    this.candleSeries = this.chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: true,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    const initial = Math.min(this.INITIAL_COUNT, this.allData.length);
    this.displayedCount = 0;
    this.updateDisplayedCount(initial);
  }

  updateDisplayedCount(newCount) {
    const bounded = Math.min(newCount, this.allData.length);
    if (bounded === this.displayedCount) return;
    this.displayedCount = bounded;
    const slice = this.allData.slice(
      Math.max(0, this.allData.length - this.displayedCount)
    );
    const points = slice.map((r) => this.recToPoint(r));
    this.candleSeries.setData(points);
    this.chart.timeScale().fitContent();
  }

  tryExpand() {
    if (this.displayedCount >= this.allData.length) return;
    const target = Math.min(
      this.allData.length,
      this.displayedCount + this.INCREMENT
    );
    this.updateDisplayedCount(target);
  }
}

class UIController {
  constructor() {
    this.api = new ApiClient("/api");
    this.chartMgr = new ChartManager("chart");
    this.tfButtons = document.querySelectorAll(".tf-btn");
    this.lastPriceEl = document.getElementById("last-price");
    this.forecastPriceEl = document.getElementById("forecast-price");
    this.forecastChangeEl = document.getElementById("forecast-change");
    this.recommendTextEl = document.getElementById("recommend-text");
    this.currentTf = "1M";
    this.init();
  }

  init() {
    this.tfButtons.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const tf = btn.dataset.tf;
        if (!tf) return;
        this.tfButtons.forEach((b) => {
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
    this.currentTf = tf;
    const data = await this.api.getData(tf);
    if (!data || data.length === 0) {
      console.warn("No data for", tf);
      this.chartMgr.setAllData([]);
      this.updateStats(null);
      return;
    }
    this.chartMgr.setAllData(data);
    const last = data[data.length - 1];
    this.updateStats(last);
  }

  updateStats(last) {
    if (!last) {
      this.lastPriceEl.innerText = "$0";
      this.forecastPriceEl.innerText = "$0";
      this.forecastChangeEl.innerText = "+0";
      this.recommendTextEl.innerText = "—";
      return;
    }
    const close = Number(last.close);
    this.lastPriceEl.innerText = "$" + close.toFixed(2);
    const forecast = close * 1.05;
    this.forecastPriceEl.innerText = "$" + forecast.toFixed(2);
    this.forecastChangeEl.innerText = "+" + (forecast - close).toFixed(2);
    this.recommendTextEl.innerText = forecast > close ? "MUA" : "BÁN";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("chart")) return;
  window.app = new UIController();
});

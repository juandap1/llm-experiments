<template>
  <div class="q-mb-md">
    <div class="widget-header">
      <div class="header-info">
        <div
          class="text-grey-5 text-weight-bold text-uppercase q-mb-xs"
          style="font-size: 11px; letter-spacing: 1px"
        >
          {{ ticker || 'Portfolio Value' }}
        </div>
        <div class="price-wrapper q-mb-xs">
          <h3 class="q-my-none text-weight-bolder" style="font-size: 32px">
            ${{ (mainMetrics.current || 0).toFixed(2) }}
          </h3>
        </div>
        <div class="return-row flex items-center">
          <span
            :class="mainMetrics.change >= 0 ? 'text-green-4' : 'text-red-4'"
            class="text-weight-bold q-mr-sm"
            style="font-size: 15px"
          >
            {{ mainMetrics.change >= 0 ? '+' : '' }}${{
              (Math.abs(mainMetrics.change) || 0).toFixed(2)
            }}
            ({{ mainMetrics.change >= 0 ? '+' : '' }}{{ (mainMetrics.percent || 0).toFixed(2) }}%)
          </span>
          <span class="text-grey-6" style="font-size: 12px; font-weight: 500">{{
            dateRangeLabel
          }}</span>
        </div>
      </div>

      <div class="header-controls">
        <div class="range-toolbar">
          <div
            class="range-opt"
            :class="{ selected: r == selectedRange }"
            @click="selectedRange = r"
            v-for="r in rangeOptions"
            :key="r"
          >
            {{ r }}
          </div>
        </div>

        <div class="holdings-card q-mt-md" v-if="subMetrics || invested">
          <!-- Position Value & Return -->
          <div
            v-if="subMetrics"
            class="hc-section q-mb-xs q-pb-xs"
            style="border-bottom: 1px solid rgba(255, 255, 255, 0.1)"
          >
            <div
              class="text-grey-6 text-uppercase"
              style="font-size: 9px; letter-spacing: 0.5px; margin-bottom: 2px"
            >
              My Equity
            </div>
            <div class="flex items-center justify-between no-wrap">
              <span
                class="text-white text-weight-bold q-mr-md"
                style="font-size: 16px; line-height: 1.1"
              >
                ${{ subMetrics.current.toFixed(2) }}
              </span>
              <span
                :class="subMetrics.change >= 0 ? 'text-green-4' : 'text-red-4'"
                class="text-weight-bold flex items-center bg-dark-transparent"
                style="
                  font-size: 11px;
                  padding: 2px 6px;
                  border-radius: 4px;
                  background: rgba(255, 255, 255, 0.05);
                "
              >
                {{ subMetrics.change >= 0 ? '+' : '' }}{{ subMetrics.percent.toFixed(2) }}%
              </span>
            </div>
          </div>

          <!-- Invested Amount -->
          <div v-if="invested" class="hc-section">
            <div class="flex items-center justify-between no-wrap">
              <span class="text-grey-6 text-uppercase" style="font-size: 9px; letter-spacing: 0.5px"
                >Cost Basis</span
              >
              <span class="text-grey-4 text-weight-medium" style="font-size: 11px"
                >${{ invested?.toFixed(2) }}</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="chart-container">
      <canvas ref="pchart"></canvas>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import Chart from 'chart.js/auto'

export default defineComponent({
  components: {},
  name: 'PriceChartWidget',
  props: {
    ticker: {
      type: String,
    },
    history: {
      type: Array,
      required: true,
      default: () => [],
    },
    portfolioBalance: {
      type: Number,
      default: 0,
    },
    invested: {
      type: Number,
      default: 0,
    },
    individual: {
      type: Boolean,
    },
  },
  setup() {
    return {
      store: useStore(),
      rangeOptions: ['1W', '1M', 'YTD', '1YR', '5YR', '10YR', 'All'],
      chart: null,
    }
  },
  data() {
    return {
      selectedRange: '1YR',
      filteredHistory: [],
    }
  },
  methods: {
    genChart() {
      if (this.history.length == 0) return
      let reduced = this.reduceDateRange()
      this.filteredHistory = reduced // Store for computed metrics

      const labels = reduced?.map((x) => x.date)
      const data = {
        labels: labels.map((x) =>
          new Date(x).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            timeZone: 'UTC',
          }),
        ),
        datasets: [
          {
            label: this.ticker,
            data: reduced?.map((x) => x.value),
            backgroundColor: '#06d671',
            borderColor: '#06d671',
            pointRadius: 0,
            pointHoverRadius: 4,
          },
        ],
      }
      const config = {
        type: 'line',
        data: data,
        options: {
          layout: {
            padding: {
              bottom: 20,
              top: 10,
            },
          },
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index',
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.dataset.label || ''
                  const value = context.parsed.y
                  return `${label}: $${value.toFixed(2)}`
                },
              },
            },
          },
          scales: {
            x: {
              grid: {
                display: false,
              },
              border: {
                display: true,
                color: '#333',
                width: 2,
              },
              ticks: {
                display: false,
                color: '#aaa',
                font: {
                  weight: 'bold',
                },
                autoSkip: false,
                callback: (value, index) => {
                  let cur = this.formatDate(labels[index])
                  if (index === 0) return cur
                  let prev = this.formatDate(labels[index - 1])
                  return cur !== prev ? cur : ''
                },
              },
            },
            y: {
              grid: {
                display: false,
              },
              border: {
                display: true,
                color: '#333',
                width: 2,
              },
              ticks: {
                color: '#aaa',
                font: {
                  weight: 'bold',
                },
                maxTicksLimit: 8,
                callback: function (value) {
                  return '$' + value.toLocaleString()
                },
              },
            },
          },
        },
        plugins: [
          {
            id: 'centeredLabels',
            afterDraw: (chart) => {
              const {
                ctx,
                chartArea: { bottom },
                scales,
              } = chart
              const xScale = scales.x
              const labelsArray = chart.data.labels

              ctx.save()
              ctx.textAlign = 'center'
              ctx.textBaseline = 'top'
              ctx.fillStyle = '#aaa'
              ctx.font = 'bold 12px Arial'

              const groups = []
              let start = 0
              while (start < labelsArray.length) {
                const label = this.formatDate(labelsArray[start])
                let end = start
                while (
                  end + 1 < labelsArray.length &&
                  this.formatDate(labelsArray[end + 1]) === label
                ) {
                  end++
                }
                groups.push({ label, start, end })
                start = end + 1
              }
              const MAX_LABELS = 8
              // Determine step to sample max labels
              const step = Math.ceil(groups.length / MAX_LABELS)

              // Draw only sampled groups
              groups.forEach((group, i) => {
                if (i % step !== 0) return // skip to reduce labels

                const startPixel = xScale.getPixelForValue(group.start)
                const endPixel = xScale.getPixelForValue(group.end)
                const centerX = Math.min(
                  (startPixel + endPixel) / 2,
                  chart.width - 20, // leave 5px from right edge
                )

                ctx.fillText(group.label, centerX, bottom + 5)
              })

              ctx.restore()
            },
          },
        ],
      }
      let htmlRef = this.$refs.pchart
      if (this.chart) this.chart.destroy()
      this.chart = new Chart(htmlRef, config)
    },
    reduceDateRange() {
      if (this.history.length === 0) return []

      const ONE_DAY_MS = 24 * 60 * 60 * 1000

      // Get the latest date from the data itself, not system time
      // Assume sorted oldest -> newest (standard for charts)
      const lastItem = this.history[this.history.length - 1]
      const latestDataTimestamp = new Date(lastItem.date).getTime()
      const now = new Date(latestDataTimestamp) // "now" is effectively the last available data point

      const ONE_YEAR_MS = 365.25 * ONE_DAY_MS

      let minDateTimestamp = 0
      let samplingIntervalDays = 1

      // Helper to add a buffer to ensure inclusive start dates (e.g. capture the exact start day)
      // Subtracting 12 hours ensures we don't miss the start date due to any DST/Timezone drift if mixed
      const BUFFER = 12 * 60 * 60 * 1000

      switch (this.selectedRange.toLowerCase()) {
        case '1w':
          minDateTimestamp = now.getTime() - 7 * ONE_DAY_MS - BUFFER
          samplingIntervalDays = 1
          break

        case '1m':
          // Approx 30 days
          minDateTimestamp = now.getTime() - 30 * ONE_DAY_MS - BUFFER
          samplingIntervalDays = 1
          break

        case 'ytd':
          // Start of the year of the data, in UTC to match data format
          // Note: Date.UTC returns a timestamp directly
          minDateTimestamp = Date.UTC(now.getUTCFullYear(), 0, 1) - BUFFER
          samplingIntervalDays = 3
          break

        case '1yr':
          minDateTimestamp = now.getTime() - ONE_YEAR_MS - BUFFER
          samplingIntervalDays = 5
          break

        case '5yr':
          minDateTimestamp = now.getTime() - 5 * ONE_YEAR_MS - BUFFER
          samplingIntervalDays = 10
          break

        case '10yr':
          minDateTimestamp = now.getTime() - 10 * ONE_YEAR_MS - BUFFER
          samplingIntervalDays = 20
          break

        case 'all':
          minDateTimestamp = 0 // epoch
          samplingIntervalDays = 60
          break

        default:
          return this.history
      }

      // Filter: Only include items whose date >= minDateTimestamp
      // history items date format: "2025-12-01". new Date("...") returns UTC midnight usually, or local.
      // To be strictly safe, we treat everything as timestamps.
      // We assume this.history is sorted oldest -> newest? The existing code looped backwards.

      const filtered = []
      // Find start index
      for (let i = 0; i < this.history.length; i++) {
        // Create date object from string
        const d = new Date(this.history[i].date).getTime()
        if (d >= minDateTimestamp) {
          filtered.push(this.history[i])
        }
      }

      // If filtering resulted in nothing (e.g. 1W range but no data in last week),
      // maybe return the last data point or empty? Return empty for now.

      let reduced = this.filterByInterval(filtered, samplingIntervalDays)
      return reduced
    },
    filterByInterval(data, intervalDays) {
      if (!data || data.length === 0 || intervalDays <= 1) {
        return data // Return full data for 1-day or invalid intervals
      }

      const reducedData = []
      // Only sample every Nth data point based on the interval
      for (let i = 0; i < data.length; i += intervalDays) {
        reducedData.push(data[i])
      }
      if (reducedData[reducedData.length - 1] !== data[data.length - 1]) {
        reducedData.push(data[data.length - 1])
      }
      return reducedData
    },
    formatDate(d) {
      let options = {
        month: 'short', // "Sep"
        day: 'numeric', // "21"
        year: 'numeric', // "2025"
        timeZone: 'UTC',
      }
      switch (this.selectedRange.toLowerCase()) {
        case '1w':
          options = {
            weekday: 'short',
            timeZone: 'UTC',
          }
          break

        case '1m': // Last 1 month
          options = {
            month: 'short', // "Sep"
            day: 'numeric', // "21"
            timeZone: 'UTC',
          }
          break

        case 'ytd': // Year To Date
        case '1yr': // Last 1 year
          options = {
            month: 'short', // "Sep"
            timeZone: 'UTC',
          }
          break

        case '5yr': // Last 5 years
        case '10yr': // Last 10 years
        case 'all': // All Time (since 1990)
          options = {
            year: 'numeric', // "2025"
            timeZone: 'UTC',
          }
          break
      }
      const formattedDate = new Intl.DateTimeFormat('en-US', options).format(new Date(d))
      return formattedDate
    },
  },
  mounted() {
    this.genChart()
  },
  computed: {
    rangeMetrics() {
      if (!this.filteredHistory || this.filteredHistory.length < 1) {
        return { current: 0, change: 0, percent: 0 }
      }
      const startPrice = Number(this.filteredHistory[0].value)
      const endPrice = Number(this.filteredHistory[this.filteredHistory.length - 1].value)

      if (startPrice === 0) return { current: 0, change: 0, percent: 0 }

      const percentChange = (endPrice - startPrice) / startPrice

      if (this.portfolioBalance) {
        // If we have a balance, we treat this as a position.
        // We calculate the dollar gain proportional to the price movement applied to current balance.
        // StartHoldings = CurrentHoldings / (1 + %Change)
        const startHoldingsValue = this.portfolioBalance / (1 + percentChange)
        const dollarChange = this.portfolioBalance - startHoldingsValue

        return {
          current: this.portfolioBalance,
          change: dollarChange,
          percent: percentChange * 100, // Convert to 0-100 scale
        }
      } else {
        // Pure price chart (no holdings), just show price delta
        return {
          current: endPrice,
          change: endPrice - startPrice,
          percent: percentChange * 100,
        }
      }
    },
    mainMetrics() {
      // If individual page, emphasize Stock Price (unitMetrics)
      // If portfolio page (or non-individual), emphasize Value (rangeMetrics)
      if (this.individual) {
        return this.unitMetrics
      }
      return this.rangeMetrics
    },
    subMetrics() {
      // If individual page AND we have a balance, show the Position Value as secondary
      if (this.individual && this.portfolioBalance) {
        // user wants the return specific to their position (Total Return), not the chart range
        if (this.invested > 0) {
          const change = this.portfolioBalance - this.invested
          const percent = (change / this.invested) * 100
          return {
            current: this.portfolioBalance,
            change: change,
            percent: percent,
          }
        }

        // Fallback if no invested data
        return {
          label: 'Your Position',
          ...this.rangeMetrics,
        }
      }
      return null
    },
    currentPrice() {
      if (this.portfolioBalance) return this.portfolioBalance
      if (this.history && this.history.length > 0) {
        return Number(this.history[this.history.length - 1].value)
      }
      return 0
    },
    dateRangeLabel() {
      if (this.selectedRange === 'All') return 'All Time'
      return `Past ${this.selectedRange}`
    },
    unitMetrics() {
      if (!this.filteredHistory || this.filteredHistory.length < 1) {
        return { current: 0, change: 0, percent: 0 }
      }
      const startVal = Number(this.filteredHistory[0].value)
      const endVal = Number(this.filteredHistory[this.filteredHistory.length - 1].value)

      const change = endVal - startVal
      const percent = startVal !== 0 ? (change / startVal) * 100 : 0

      return { current: endVal, change, percent }
    },
    allTimeReturn() {
      if (!this.invested) return 0
      let change = ((this.portfolioBalance - this.invested) / this.invested) * 100
      return Math.round(change * 100) / 100
    },
  },
  watch: {
    'history.length': function () {
      this.genChart()
    },
    selectedRange: function () {
      this.genChart()
    },
  },
})
</script>
<style lang="scss" scoped>
.widget-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.header-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.range-toolbar {
  background-color: #222;
  padding: 1px;
  border-radius: 50px;
  display: flex;
  gap: 2px;

  .range-opt {
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
    color: #888;
    cursor: pointer;
    border-radius: 50px;
    transition: all 0.2s;
  }

  .range-opt:hover,
  .range-opt.selected {
    color: #222;
    background-color: #aaa;
  }
}

.price-wrapper {
  display: flex;
  align-items: center;
  gap: 5px;
}

.invested-badge {
  opacity: 0.8;
  transition: opacity 0.2s;
}
.invested-badge:hover {
  opacity: 1;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.holdings-card {
  background-color: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 10px;
  min-width: 140px;
  backdrop-filter: blur(5px);
}
</style>

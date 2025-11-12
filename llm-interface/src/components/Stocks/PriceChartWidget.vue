<template>
  <div class="q-mb-md">
    <div class="widget-header">
      <h4>${{ stockInfo?.latest_price.toFixed(2) }}</h4>
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
      <!-- <button class="alt-btn" @click="addModal = true">
        <q-icon name="fas fa-plus" />
        Add
      </button> -->
    </div>
    <canvas ref="pchart"></canvas>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import Chart from 'chart.js/auto'

export default defineComponent({
  components: {},
  name: 'PriceChartWidget',
  props: {},
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
    }
  },
  methods: {
    genChart() {
      if (this.history.length == 0) return
      let reduced = this.reduceDateRange()
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
            label: 'MSFT',
            data: reduced?.map((x) => x.close_price),
            backgroundColor: '#06d671',
            borderColor: '#06d671',
            pointRadius: 0,
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
            },
          },
          responsive: true,
          interaction: {
            intersect: false,
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
      if (this.history.length == 0) return
      const today = new Date()
      let startDate = new Date()
      startDate.setUTCHours(0, 0, 0, 0)
      startDate.setDate(today.getDate() - 8)
      let samplingIntervalDays = 1
      switch (this.selectedRange.toLowerCase()) {
        case '1w':
          startDate.setDate(today.getDate() - 8)
          samplingIntervalDays = 1 // Keep daily data
          break

        case '1m': // Last 1 month
          startDate.setMonth(today.getMonth() - 1)
          samplingIntervalDays = 1 // Keep daily data
          break

        case 'ytd': // Year To Date
          startDate = new Date(today.getFullYear(), 0, 1) // Start of current year
          samplingIntervalDays = 3 // Sample every 3rd day
          break

        case '1yr': // Last 1 year
          startDate.setFullYear(today.getFullYear() - 1)
          samplingIntervalDays = 5 // Sample every 5th day (weekly)
          break

        case '5yr': // Last 5 years
          startDate.setFullYear(today.getFullYear() - 5)
          samplingIntervalDays = 10 // Sample every 10th day
          break

        case '10yr': // Last 10 years
          startDate.setFullYear(today.getFullYear() - 10)
          samplingIntervalDays = 20 // Sample every 20th day (monthly)
          break

        case 'all': // All Time (since 1990)
          // Use a very aggressive sampling rate for full history
          samplingIntervalDays = 60 // Sample every 60th day (quarterly-ish)
          break

        default:
          return this.history
      }
      let startIndex = 0 // Default to 0 (start of array, or ALL time)
      for (let i = this.history.length - 1; i >= 0; i--) {
        const currentDataDate = new Date(this.history[i].date)
        if (currentDataDate < startDate) {
          startIndex = i + 1
          break
        }
      }
      let range =
        this.selectedRange.toLowerCase() == 'all' ? this.history : this.history.slice(startIndex)
      let reduced = this.filterByInterval(range, samplingIntervalDays)
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
    this.store.getStockHistory('MSFT')
    this.genChart()
  },
  computed: {
    stockInfo() {
      return this.store.loadedInfo['MSFT']
    },
    history() {
      if (this.store.history?.['MSFT'] == null) return []
      return this.store.history['MSFT']
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
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.range-toolbar {
  background-color: #222;
  padding: 1px;
  border-radius: 50px;
  display: flex;
  gap: 4px;

  .range-opt {
    padding: 5px 10px;
    font-size: 12px;
    font-weight: bold;
    color: #aaa;
    cursor: pointer;
    border-radius: 50px;
  }

  .range-opt:hover,
  .range-opt.selected {
    color: #222;
    background-color: #aaa;
  }
}
</style>

<template>
  <canvas ref="pchart"></canvas>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import Chart from 'chart.js/auto'

export default defineComponent({
  components: {},
  name: 'LineChart',
  props: {
    labels: {
      type: Array,
      required: true,
      default: () => [],
    },
    data: {
      type: Array,
      required: true,
      default: () => [],
    },
  },
  setup() {
    return {
      store: useStore(),
      chart: null,
    }
  },
  data() {
    return {}
  },
  methods: {
    genChart() {
      const labels = this.labels
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
            data: this.data,
            backgroundColor: '#06d671',
            borderColor: '#06d671',
            pointRadius: 0,
            fill: {
              target: 'origin',
              above: '#06d67133',
            },
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
          maintainAspectRatio: false,
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
        year: 'numeric',
        timeZone: 'UTC',
      }
      const formattedDate = new Intl.DateTimeFormat('en-US', options).format(new Date(d))
      return formattedDate
    },
  },
  mounted() {
    // this.store.getStockHistory('MSFT')
    this.genChart()
  },
  computed: {
    // history() {
    //   if (this.store.history?.['MSFT'] == null) return []
    //   return this.store.history['MSFT']
    // },
    allTimeReturn() {
      if (!this.invested) return 0
      let change = ((this.portfolioBalance - this.invested) / this.invested) * 100
      return Math.round(change * 100) / 100
    },
  },
  watch: {
    'data.length': function () {
      this.genChart()
    },
  },
})
</script>
<style lang="scss" scoped></style>

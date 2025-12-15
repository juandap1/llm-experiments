<template>
  <canvas ref="bchart"></canvas>
</template>

<script>
import { defineComponent } from 'vue'
import Chart from 'chart.js/auto'

export default defineComponent({
  name: 'BarChart',
  props: {
    datasets: {
      // [{label: string, data: number[], backgroundColor: string, borderColor: string, borderWidth: number}]
      type: Array,
      required: true,
    },
    labels: {
      type: Array,
      required: true,
    },
  },
  methods: {
    genChart() {
      const config = {
        type: 'bar',
        data: {
          labels: this.labels,
          datasets: this.datasets,
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false,
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
            },
          },
        },
      }
      let htmlRef = this.$refs.bchart
      if (this.chart) this.chart.destroy()
      this.chart = new Chart(htmlRef, config)
    },
  },
  mounted() {
    this.genChart()
  },
  watch: {
    'labels.length': function () {
      this.genChart()
    },
  },
})
</script>

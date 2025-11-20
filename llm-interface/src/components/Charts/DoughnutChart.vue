<template>
  <div class="chart-cont">
    <canvas ref="dchart"></canvas>
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
      chart: null,
    }
  },
  data() {
    return {}
  },
  methods: {
    genChart() {
      const data = {
        labels: ['Red', 'Blue', 'Yellow'],
        datasets: [
          {
            label: 'My First Dataset',
            data: [300, 50, 100],
            backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)'],
            hoverOffset: 4,
          },
        ],
      }
      const config = {
        type: 'doughnut',
        data: data,
      }
      let htmlRef = this.$refs.dchart
      if (this.chart) this.chart.destroy()
      this.chart = new Chart(htmlRef, config)
    },
  },
  mounted() {
    this.genChart()
  },
  computed: {},
  watch: {},
})
</script>
<style lang="scss" scoped>
.chart-cont {
  width: 500px;
  height: 500px;
}
</style>

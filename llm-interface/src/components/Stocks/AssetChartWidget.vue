<template>
  <div class="asset-chart">
    <DashedCircleChart :data="holdings" :colors="colors" :totalValue="totalValue" />
    <div class="asset-legend">
      <q-scroll-area class="asset-legend-scroll" dark>
        <div class="asset-legend-item" v-for="(item, index) in holdings" :key="index">
          <q-icon name="fas fa-circle" :style="{ color: colors[index] }" />
          <div class="asset-item-main">
            <div class="item-lbl">{{ item.ticker }}</div>
            <div class="item-value">${{ item.value.toFixed(2) }}</div>
          </div>
          <div>
            <div class="asset-ratio">{{ ((item.value / totalValue) * 100).toFixed(2) }}%</div>
          </div>
        </div>
      </q-scroll-area>
    </div>
  </div>
</template>
<script>
import { defineComponent } from 'vue'
import DashedCircleChart from 'src/components/Charts/DashedCircleChart.vue'

export default defineComponent({
  name: 'AssetChartWidget',
  setup() {
    return {
      colors: [
        '#C44E52',
        '#D64646',
        '#E85040',
        '#FF6F00',
        '#FF8C00',
        '#F49451',
        '#FFC300',
        '#FFD700',
        '#E0CF4B',
        '#D5BB60',
        '#79C74E',
        '#55A868',
        '#3CB371',
        '#1B9E77',
        '#00B8AA',
        '#00CED1',
        '#17BECF',
        '#4682B4',
        '#4C72B0',
        '#1E90FF',
        '#7B68EE',
        '#9370DB',
        '#9467BD',
        '#A83C85',
        '#C63A9A',
        '#A000A0',
        '#800080',
      ],
    }
  },
  components: {
    DashedCircleChart,
  },
  props: {
    holdings: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    totalValue() {
      return this.holdings.reduce((acc, x) => acc + x.value, 0)
    },
  },
})
</script>
<style scoped>
.asset-chart {
  display: flex;
  gap: 20px;
}

.asset-legend {
  width: 300px;
  border-radius: 15px;
  background-color: rgb(255, 255, 255, 0.02);
}

.asset-legend-scroll {
  height: 100%;
}

.asset-legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 15px;
}

.asset-item-main {
  flex: 1 1 auto;
}

.asset-ratio {
  color: #ccc;
  font-weight: bold;
}
</style>

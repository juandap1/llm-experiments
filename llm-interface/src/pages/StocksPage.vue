<template>
  <q-page class="basic-page">
    <h6>My Portfolio</h6>
    <!-- <price-chart-widget /> -->
    <dashed-circle-chart />
    <history-widget :transactions="allTransactions" />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from '../components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'
import DashedCircleChart from '../components/DashedCircleChart.vue'
// import PriceChartWidget from '../components/Stocks/PriceChartWidget.vue'

export default defineComponent({
  name: 'StocksPage',
  components: { HistoryWidget, DashedCircleChart },
  setup() {
    return {
      store: useStore(),
    }
  },

  mounted() {},
  computed: {
    allTransactions() {
      return useStore().transactions
    },
  },
})
</script>
<style lang="scss" scoped>
.stock-header {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 25px;
}
</style>

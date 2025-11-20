<template>
  <q-page class="basic-page">
    <h6>My Portfolio</h6>
    <!-- <price-chart-widget /> -->

    <asset-chart-widget :holdings="holdings" />
    <history-widget :transactions="allTransactions" />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from '../components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'
import AssetChartWidget from '../components/Stocks/AssetChartWidget.vue'

export default defineComponent({
  name: 'StocksPage',
  components: { HistoryWidget, AssetChartWidget },
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
    holdings() {
      if (!this.store.currently_holding) return []
      return this.store.currently_holding
        .map((x) => {
          return {
            ticker: x,
            value: this.store.value_map?.[x] || 0,
          }
        })
        .sort((a, b) => b.value - a.value)
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

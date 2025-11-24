<template>
  <q-page class="basic-page">
    <h6>My Portfolio</h6>
    <!-- <price-chart-widget /> -->
    <asset-breakdown-widget :holdings="holdings" />
    <asset-chart-widget :holdings="holdings" />
    <dividend-widget />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import AssetChartWidget from 'src/components/Stocks/AssetChartWidget.vue'
import AssetBreakdownWidget from 'src/components/Stocks/AssetBreakdownWidget.vue'
import DividendWidget from 'src/components/Stocks/DividendWidget.vue'

export default defineComponent({
  name: 'StockAssetPage',
  components: { AssetChartWidget, AssetBreakdownWidget, DividendWidget },
  setup() {
    return {
      store: useStore(),
    }
  },

  mounted() {},
  computed: {
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

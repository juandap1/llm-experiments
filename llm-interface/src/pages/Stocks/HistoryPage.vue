<template>
  <q-page class="basic-page">
    <h6>My Transactions</h6>
    <history-widget :transactions="store.transactions" />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import HistoryWidget from 'src/components/Stocks/HistoryWidget.vue'

export default defineComponent({
  name: 'StockAssetPage',
  components: { HistoryWidget },
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

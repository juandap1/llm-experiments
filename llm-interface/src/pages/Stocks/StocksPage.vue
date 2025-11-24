<template>
  <q-page class="basic-page">
    <h6>My Portfolio</h6>
    <div>
      <h6>Portfolio Balance</h6>
      {{ portfolioBalance }}
    </div>
    <div>
      <h6>Invested</h6>
      {{ store.invested }}
    </div>
    <div class="basic-widget">
      <h5 class="q-pa-md">My Holdings</h5>
      <q-scroll-area dark style="height: 300px">
        <table class="full-width stock-table">
          <thead>
            <tr>
              <th class="text-left">Asset</th>
              <th class="text-right">Price</th>
              <th class="text-right">Shares</th>
              <th class="text-right">Avg Cost</th>
              <th class="text-right">Value</th>
              <th class="text-right">Return</th>
              <th class="text-right">Allocation</th>
            </tr>
          </thead>
          <tbody>
            <stock-holding-item
              v-for="holding in holdings"
              :key="holding.ticker"
              v-bind="holding"
              :totalValue="portfolioBalance"
            />
          </tbody>
        </table>
      </q-scroll-area>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import StockHoldingItem from 'src/components/Stocks/Items/StockHoldingItem.vue'

export default defineComponent({
  name: 'StocksPage',
  components: { StockHoldingItem },
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
    portfolioBalance() {
      return this.holdings.reduce((acc, x) => acc + x.value, 0)
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

.basic-widget {
  margin-top: 25px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.02);
  overflow: hidden;
}

.stock-table {
  border-collapse: collapse;
  width: 100%;

  th {
    padding: 12px 16px;
    font-weight: 600;
    color: #888;
    font-size: 0.85rem;
    border-bottom: 1px solid var(--border-color);
    white-space: nowrap;
  }
}
</style>

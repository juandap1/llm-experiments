<template>
  <q-page class="basic-page q-pa-md">
    <div class="row q-col-gutter-lg">
      <!-- Left Column: Stats & Dividends -->
      <div class="col-12 col-md-4">
        <div class="column q-gutter-y-lg">
          <!-- Portfolio Summary Card -->
          <div class="summary-card">
            <h6>Portfolio Balance</h6>
            <div class="balance-value">${{ portfolioBalance.toFixed(2) }}</div>
            <div class="invested-row">
              <span class="label">Invested:</span>
              <span class="value">${{ store.invested?.toFixed(2) }}</span>
              <span :class="portfolioBalance - store.invested > 0 ? 'positive' : 'negative'">
                {{ portfolioBalance - store.invested > 0 ? '+' : '' }}
                {{ ((portfolioBalance - store.invested) / store.invested).toFixed(2) * 100 }}%
              </span>
            </div>
          </div>

          <!-- Dividend Widget -->
          <dividend-widget />

          <!-- Sector Breakdown Widget -->
          <sector-breakdown-widget />
        </div>
      </div>

      <!-- Right Column: Holdings Table -->
      <div class="col-12 col-md-8">
        <div class="basic-widget price-chart-widget">
          <price-chart-widget :history="store.profitLossHistory" />
        </div>
        <div class="basic-widget">
          <h5 class="q-pa-md">My Holdings</h5>
          <q-scroll-area dark style="height: 600px">
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
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import StockHoldingItem from 'src/components/Stocks/Items/StockHoldingItem.vue'
import DividendWidget from 'src/components/Stocks/DividendWidget.vue'
import SectorBreakdownWidget from 'src/components/Stocks/SectorBreakdownWidget.vue'
import PriceChartWidget from 'src/components/Stocks/PriceChartWidget.vue'

export default defineComponent({
  name: 'StocksPage',
  components: { StockHoldingItem, DividendWidget, SectorBreakdownWidget, PriceChartWidget },
  setup() {
    return {
      store: useStore(),
    }
  },
  methods: {},
  mounted() {
    this.store.batchStockHistoryRequest(this.store.uniqueTickers)
    this.store.batchStockSplitRequest(this.store.uniqueTickers)
  },
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
  watch: {
    'holdings.length': {
      handler() {
        this.store.batchStockHistoryRequest(this.store.uniqueTickers)
        this.store.batchStockSplitRequest(this.store.uniqueTickers)
      },
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
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.02);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.summary-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01));
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);

  h6 {
    margin: 0 0 10px 0;
    font-size: 1rem;
    color: #888;
    font-weight: 500;
  }
}

.balance-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.1;
  margin-bottom: 15px;
}

.invested-row {
  display: flex;
  gap: 8px;
  font-size: 0.9rem;

  .label {
    color: #888;
  }
  .value {
    color: #ddd;
    font-weight: 600;
  }
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

.price-chart-widget {
  padding: 25px;
  padding-bottom: 0;
}
</style>

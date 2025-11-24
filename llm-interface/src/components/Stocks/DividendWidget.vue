<template>
  <div class="dividend-widget">
    <div class="header-section">
      <div class="title-group">
        <h6>Dividends</h6>
        <div class="subtitle">Estimated Annual Income</div>
      </div>
      <div class="total-amount">${{ totalAnnualDividend.toFixed(2) }}</div>
    </div>

    <div class="yield-badge">
      <span class="label">Portfolio Yield</span>
      <span class="value">{{ portfolioYield.toFixed(2) }}%</span>
    </div>

    <div class="divider"></div>

    <div class="holdings-list">
      <div class="list-header">
        <span>Asset</span>
        <span>Payout</span>
      </div>
      <div v-for="item in holdings" :key="item.ticker" class="holding-item">
        <div class="item-left">
          <q-img
            class="stock-logo"
            :src="`http://localhost:3141/logo/${item.ticker}`"
            loading="lazy"
          />
          <div class="ticker-info">
            <span class="ticker">{{ item.ticker }}</span>
            <span class="shares">{{ item.shares.toFixed(2) }} shares</span>
          </div>
        </div>
        <!-- <div>${{ item.dividendPerShare.toFixed(2) }}</div> -->
        <div class="item-right">
          <div class="payout">${{ item.annualPayout.toFixed(2) }}</div>
          <div class="yield-info">{{ item.yield.toFixed(2) }}% Yield</div>
        </div>
      </div>
      <div v-if="holdings.length === 0" class="empty-state">No dividend paying stocks found.</div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'

export default defineComponent({
  name: 'DividendWidget',
  setup() {
    return {
      store: useStore(),
    }
  },
  computed: {
    holdings() {
      const holdingMap = this.store.holding_map
      const loadedInfo = this.store.loadedInfo

      if (!holdingMap) return []

      return Object.keys(holdingMap)
        .map((ticker) => {
          const shares = holdingMap[ticker].reduce((acc, lot) => acc + lot.shares, 0)
          const info = loadedInfo[ticker]
          // Assuming dividend_per_share is annual. If it's quarterly, we might need to adjust based on data source.
          // Usually APIs return 'last annual dividend' or 'dividend per share (ttm)'.
          // We will assume the store provides a usable annual-equivalent or per-share amount.
          // If the user's previous code was just `asset.dividend_per_share`, we stick to that.
          const dividendPerShare = info?.dividend_per_share || 0
          const price = info?.latest_price || 0

          return {
            ticker,
            shares,
            dividendPerShare,
            annualPayout: shares * dividendPerShare,
            yield: price > 0 ? (dividendPerShare / price) * 100 : 0,
          }
        })
        .filter((h) => h.annualPayout > 0)
        .sort((a, b) => b.annualPayout - a.annualPayout)
    },
    totalAnnualDividend() {
      return this.holdings.reduce((acc, h) => acc + h.annualPayout, 0)
    },
    portfolioYield() {
      // Calculate total portfolio value to get accurate yield
      const totalValue = this.store.currently_holding?.reduce((acc, ticker) => {
        return acc + (this.store.value_map?.[ticker] || 0)
      }, 0)

      if (!totalValue || totalValue === 0) return 0
      return (this.totalAnnualDividend / totalValue) * 100
    },
  },
})
</script>

<style lang="scss" scoped>
.dividend-widget {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 15px;
  backdrop-filter: blur(10px);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

h6 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.2;
}

.subtitle {
  font-size: 0.8rem;
  color: #888;
  margin-top: 4px;
}

.total-amount {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4caf50; /* Green for money */
  text-shadow: 0 2px 10px rgba(76, 175, 80, 0.2);
}

.yield-badge {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 20px;
  display: flex;
  gap: 8px;
  font-size: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.1);

  .label {
    color: #aaa;
  }
  .value {
    font-weight: 600;
    color: #fff;
  }
}

.divider {
  height: 1px;
  background: var(--border-color);
  opacity: 0.5;
  margin: 5px 0;
}

.holdings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px; // Space for scrollbar

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 2px;
  }
}

.list-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-bottom: 5px;
}

.holding-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);

  &:last-child {
    border-bottom: none;
  }
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #222;
}

.ticker-info {
  display: flex;
  flex-direction: column;
}

.ticker {
  font-weight: 600;
  font-size: 0.9rem;
}

.shares {
  font-size: 0.75rem;
  color: #888;
}

.item-right {
  text-align: right;
}

.payout {
  font-weight: 600;
  font-size: 0.9rem;
  color: #eee;
}

.yield-info {
  font-size: 0.75rem;
  color: #4caf50;
}

.empty-state {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
  padding: 20px 0;
  font-style: italic;
}
</style>

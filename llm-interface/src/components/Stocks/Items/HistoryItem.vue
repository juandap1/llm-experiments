<template>
  <div class="hist-item">
    <!-- Icon / Type Indicator -->
    <div class="hi-icon">
      <q-icon name="fas fa-arrow-down" color="green-4" size="12px" />
    </div>

    <!-- Main Details -->
    <div class="hi-content">
      <div class="hi-header">
        <span class="hi-ticker">{{ ticker }}</span>
        <span class="hi-action">Market Buy</span>
      </div>
      <div class="hi-sub">{{ share_count }} shares @ ${{ share_price.toFixed(2) }}</div>
    </div>

    <!-- Date (Centered-ish or Right aligned next to values) -->
    <div class="hi-date">{{ date }}</div>

    <!-- Financials -->
    <div class="hi-financials">
      <div class="hi-cost">${{ cost }}</div>
      <div class="price-change" :class="priceChange >= 0 ? 'text-green-4' : 'text-red-4'">
        {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HistoryItem',
  props: {
    id: Number,
    ticker: String,
    share_count: Number,
    share_price: Number,
    transaction_date: String,
  },
  computed: {
    cost() {
      return (this.share_count * this.share_price).toFixed(2)
    },
    date() {
      let d = new Date(this.transaction_date)
      const options = {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        timeZone: 'UTC',
      }
      return new Intl.DateTimeFormat('en-US', options).format(d)
    },
    stockInfo() {
      return useStore().loadedInfo[this.ticker]
    },
    priceChange() {
      let first = parseFloat(this.share_price)
      let last = parseFloat(this.stockInfo?.latest_price)
      if (!last) return 0
      let change = ((last - first) / first) * 100
      return Math.round(change * 100) / 100
    },
  },
})
</script>
<style lang="scss" scoped>
.hist-item {
  display: flex;
  align-items: center;
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.2s ease;
  border-radius: 8px;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  &:last-child {
    border-bottom: none;
  }
}

.hi-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(76, 175, 80, 0.15);
  border-radius: 50%;
  margin-right: 16px;
}

.hi-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.hi-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.hi-ticker {
  font-weight: 700;
  font-size: 14px;
  color: #fff;
}

.hi-action {
  font-size: 11px;
  color: #888;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hi-sub {
  font-size: 12px;
  color: #666;
}

.hi-date {
  font-size: 12px;
  color: #555;
  margin-right: 24px;
  font-weight: 500;
}

.hi-financials {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 80px;
}

.hi-cost {
  font-weight: 700;
  font-size: 14px;
  color: #fff;
  margin-bottom: 2px;
}

.price-change {
  font-size: 11px;
  font-weight: 600;
}
</style>

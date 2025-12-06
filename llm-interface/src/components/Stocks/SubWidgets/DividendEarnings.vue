<template>
  <div>
    <div class="row items-center justify-between q-mb-sm">
      <div class="section-header">Your Earnings History</div>
      <div class="total-earned">
        Total: <span class="text-green-4">${{ totalDividendsEarned.toFixed(2) }}</span>
      </div>
    </div>
    <div class="dividend-list-container" v-if="sortedDividendHistoryDesc.length">
      <div
        v-for="div in sortedDividendHistoryDesc"
        :key="div.ex_dividend_date"
        class="dividend-card"
      >
        <div class="dc-amount" :class="isPaid(div.payment_date) ? 'text-green-4' : ''">
          +${{ div.earned?.toFixed(2) }}
          <div class="dc-shares">({{ div.sharesOwned?.toFixed(2) }} shares)</div>
        </div>
        <div class="dc-date">Ex: {{ formatDate(div.ex_dividend_date) }}</div>
        <div class="dc-pay">Pay: {{ formatDate(div.payment_date) }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DividendEarnings',
  props: {
    totalDividendsEarned: {
      type: Number,
      required: true,
    },
    sortedDividendHistoryDesc: {
      type: Array,
      required: true,
    },
  },
  methods: {
    isPaid(dateStr) {
      if (!dateStr) return false
      return new Date(dateStr) <= new Date()
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleDateString('en-US', {
        month: 'short',
        year: '2-digit',
        day: 'numeric',
        timeZone: 'UTC',
      })
    },
  },
})
</script>
<style lang="css" scoped>
.dividend-list-container {
  display: flex;
  overflow-x: auto;
  gap: 12px;
  padding: 8px 0px;
}

.dividend-list-container::-webkit-scrollbar {
  height: 6px;
}
.dividend-list-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
}
.dividend-list-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.dividend-card {
  min-width: 100px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s;
}

.dividend-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.dc-amount {
  font-weight: bold;
  font-size: 15px;
  color: #fff;
  margin-bottom: 4px;
}

.dc-shares {
  font-size: 11px;
  font-weight: normal;
  color: #aaa;
  margin-left: 2px;
}

.dc-date,
.dc-pay {
  font-size: 10px;
  color: #888;
  white-space: nowrap;
}

.total-earned {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}
</style>

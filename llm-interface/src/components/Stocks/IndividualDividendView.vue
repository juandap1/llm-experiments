<template>
  <div class="q-my-md">
    <h6>Dividends</h6>

    <!-- Current Stats -->
    <div class="row q-col-gutter-md q-mb-lg">
      <div class="col-4">
        <div class="stat-label">Yield</div>
        <div class="stat-value">
          {{
            stockInfo?.latest_price
              ? ((stockInfo.dividend_per_share / stockInfo.latest_price) * 100).toFixed(2)
              : '-'
          }}%
        </div>
      </div>
      <div class="col-4">
        <div class="stat-label">Annual Payout</div>
        <div class="stat-value">${{ stockInfo?.dividend_per_share.toFixed(2) }}</div>
      </div>
      <div class="col-4">
        <div class="stat-label">Est. Annual Income</div>
        <div class="stat-value">${{ (stockInfo?.dividend_per_share * shareCount).toFixed(2) }}</div>
      </div>
    </div>

    <!-- Growth Section -->
    <div class="q-mb-lg">
      <div class="section-header">Dividend Growth</div>
      <div class="dividend-chart">
        <line-chart
          :labels="dividendHistory?.map((x) => x.ex_dividend_date)"
          :data="dividendHistory?.map((x) => x.amount)"
        />
      </div>
      <dividend-growth :dividend-growth="dividendGrowth" />
    </div>

    <!-- Earnings History Section -->
    <dividend-earnings
      :total-dividends-earned="totalDividendsEarned"
      :sorted-dividend-history-desc="sortedDividendHistoryDesc"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import LineChart from 'src/components/Charts/LineChart.vue'
import DividendGrowth from './SubWidgets/DividendGrowth.vue'
import DividendEarnings from './SubWidgets/DividendEarnings.vue'

export default defineComponent({
  name: 'IndividualDividendView',
  components: { LineChart, DividendGrowth, DividendEarnings },
  props: {
    ticker: {
      type: String,
      required: true,
    },
  },
  setup() {
    const store = useStore()
    return {
      store,
    }
  },

  computed: {
    stockInfo() {
      return useStore().loadedInfo[this.ticker]
    },
    holding() {
      return useStore().holding_map?.[this.ticker]
    },
    shareCount() {
      return this.holding?.reduce((a, b) => a + b.shares, 0)
    },
    dividendHistory() {
      return useStore().dividends?.[this.ticker]
    },
    dividendGrowth() {
      const history = this.dividendHistory
      if (!history || history.length === 0) return null

      // Sort descending by ex_dividend_date
      const sorted = [...history]
        .filter((x) => x.ex_dividend_date && x.amount)
        .sort((a, b) => new Date(b.ex_dividend_date) - new Date(a.ex_dividend_date))

      if (sorted.length === 0) return null

      const latest = sorted[0]
      const latestDate = new Date(latest.ex_dividend_date)
      const latestAmount = Number(latest.amount)

      if (latestAmount === 0) return null

      const getClosest = (targetDate) => {
        let closest = null
        let minDiff = Infinity

        for (const item of sorted) {
          const d = new Date(item.ex_dividend_date)
          const diff = Math.abs(d - targetDate)
          // Allow max 180 days drift
          if (diff < minDiff && diff < 1000 * 3600 * 24 * 180) {
            minDiff = diff
            closest = item
          }
        }
        return closest
      }

      const calculateGrowth = (years) => {
        const targetDate = new Date(latestDate)
        targetDate.setFullYear(targetDate.getFullYear() - years)

        // Ensure we have data going back far enough (approx)
        const oldestDate = new Date(sorted[sorted.length - 1].ex_dividend_date)
        if (targetDate < oldestDate && Math.abs(targetDate - oldestDate) > 1000 * 3600 * 24 * 90) {
          return null
        }

        const past = getClosest(targetDate)
        if (!past) return null

        const pastAmount = Number(past.amount)
        if (pastAmount === 0) return null

        // Use actual time difference for accurate CAGR
        const pastDate = new Date(past.ex_dividend_date)
        const actualYears = (latestDate - pastDate) / (1000 * 3600 * 24 * 365.25)

        if (actualYears < 0.5) return null

        const cagr = Math.pow(latestAmount / pastAmount, 1 / actualYears) - 1
        return {
          growth: (cagr * 100).toFixed(2),
          pastAmount: pastAmount.toFixed(2),
          pastDate: past.ex_dividend_date,
          period: `${years}Y`,
        }
      }

      const getAllTime = () => {
        const oldest = sorted[sorted.length - 1]
        const oldestDate = new Date(oldest.ex_dividend_date)
        const oldestAmount = Number(oldest.amount)

        if (oldestAmount === 0) return null
        if (oldestDate.getTime() === latestDate.getTime()) return null

        const yearsDiff = (latestDate - oldestDate) / (1000 * 3600 * 24 * 365.25)
        if (yearsDiff < 1) return null

        const cagr = Math.pow(latestAmount / oldestAmount, 1 / yearsDiff) - 1
        return {
          growth: (cagr * 100).toFixed(2),
          pastAmount: oldestAmount.toFixed(2),
          pastDate: oldest.ex_dividend_date,
          period: 'All',
        }
      }

      return {
        '1Y': calculateGrowth(1),
        '5Y': calculateGrowth(5),
        '10Y': calculateGrowth(10),
        All: getAllTime(),
      }
    },
    totalDividendsEarned() {
      return this.dividendHistory?.reduce((acc, div) => acc + div.amount, 0) || 0
    },
    sortedDividendHistoryDesc() {
      const history = this.dividendHistory
      const transactions = this.adjustedStockTransactions
      if (!history || !transactions) return []

      // Create a list with 'earned' amount attached
      const enriched = history
        .map((div) => {
          const exDate = new Date(div.ex_dividend_date)

          // Find holdings BEFORE ex-dividend date
          const relevantTrans = transactions.filter((t) => new Date(t.transaction_date) < exDate)
          const sharesOwned = relevantTrans.reduce((acc, t) => {
            return t.buying ? acc + t.share_count : acc - t.share_count
          }, 0)

          // Only include positive share counts (floating point errors safety)
          if (sharesOwned < 0.0001) return null

          return {
            ...div,
            earned: sharesOwned * Number(div.amount),
            sharesOwned: sharesOwned, // optional, good for debug
          }
        })
        .filter(Boolean) // Remove nulls

      return enriched.sort((a, b) => new Date(b.ex_dividend_date) - new Date(a.ex_dividend_date))
    },
    adjustedStockTransactions() {
      return useStore().adjustedTransactions?.filter((x) => x.ticker == this.ticker)
    },
  },
})
</script>
<style lang="scss" scoped>
.dividend-chart {
  margin-top: 15px;
  height: 250px;
}

.stat-label {
  font-size: 11px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}
</style>

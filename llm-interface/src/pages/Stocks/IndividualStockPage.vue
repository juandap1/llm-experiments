<template>
  <q-page class="basic-page">
    <div class="stock-header">
      <div class="stock-logo">
        <img :src="`http://localhost:3141/logo/${ticker}`" alt="Stock ticker logo" />
      </div>
      <div>
        <div class="stock-ticker">{{ stockInfo?.ticker }}</div>
        <div class="stock-name">{{ stockInfo?.name }}</div>
      </div>
    </div>
    <price-chart-widget
      :history="stockHistory"
      :portfolioBalance="value"
      :invested="invested"
      :ticker="ticker"
      individual
    />
    <div class="analysis-widget" v-if="analysis">
      <h6><q-icon name="fas fa-star-of-life" /> {{ analysis['general_headline'] }}</h6>
      <div class="analysis-event" v-for="e in analysis['events']" :key="e">
        <div class="ae-title">{{ e.headline }}</div>
        <div class="ae-content">{{ e.summary }}</div>
      </div>
      <div class="analysis-event">
        <div class="ae-title">Broader look: Market and sector context</div>
        <div class="ae-content">{{ analysis['market_summary'] }}</div>
      </div>
    </div>
    <div class="q-my-md">
      <h6>Profile</h6>
      <div class="stock-desc">{{ stockInfo?.description }}</div>
      <div>
        <span class="tag">{{ stockInfo?.sector }}</span>
        <span class="tag">{{ stockInfo?.industry }}</span>
      </div>
    </div>
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
          <div class="stat-value">
            ${{ (stockInfo?.dividend_per_share * shareCount).toFixed(2) }}
          </div>
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
        <div class="growth-row" v-if="dividendGrowth">
          <template v-for="(data, label) in dividendGrowth" :key="label">
            <div v-if="data" class="growth-item">
              <div class="gi-header">
                <span class="gi-label">{{ label }} CAGR</span>
              </div>
              <div class="gi-value" :class="data.growth >= 0 ? 'text-pos' : 'text-neg'">
                <q-icon
                  :name="data.growth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"
                  size="10px"
                  class="q-mr-xs"
                />
                {{ data.growth }}%
              </div>
              <div class="gi-sub">from ${{ data.pastAmount }}</div>
            </div>
          </template>
        </div>
      </div>

      <!-- Earnings History Section -->
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
              +${{ div.earned.toFixed(2) }}
              <div class="dc-shares">({{ div.sharesOwned.toFixed(2) }} shares)</div>
            </div>
            <div class="dc-date">Ex: {{ formatDate(div.ex_dividend_date) }}</div>
            <div class="dc-pay">Pay: {{ formatDate(div.payment_date) }}</div>
          </div>
        </div>
      </div>
    </div>
    <history-widget :transactions="stockTransactions" />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from 'src/components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'
import PriceChartWidget from 'src/components/Stocks/PriceChartWidget.vue'
import LineChart from 'src/components/Charts/LineChart.vue'

export default defineComponent({
  name: 'IndividualStockPage',
  components: { HistoryWidget, PriceChartWidget, LineChart },
  mounted() {
    useStore().getStockInfo(this.ticker)
    useStore().getStockDividends(this.ticker)
  },
  computed: {
    ticker() {
      return this.$route.params.ticker
    },
    stockInfo() {
      return useStore().loadedInfo[this.ticker]
    },
    value() {
      return useStore().value_map[this.ticker]
    },
    invested() {
      return useStore()
        .adjustedTransactions?.filter((x) => x.ticker == this.ticker)
        .reduce((acc, x) => {
          if (x.buying) return acc + x.share_count * x.share_price
          return acc - x.share_count * x.share_price
        }, 0)
    },
    stockHistory() {
      return useStore().history?.[this.ticker]?.map((x) => {
        return {
          ...x,
          value: x.close_price,
        }
      })
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
    holding() {
      return useStore().holding_map?.[this.ticker]
    },
    shareCount() {
      return this.holding?.reduce((a, b) => a + b.shares, 0)
    },
    analysis() {
      if (!this.stockInfo?.analysis || this.stockInfo.analysis == 'loading...') return null
      return JSON.parse(this.stockInfo.analysis)
    },
    stockTransactions() {
      return useStore().transactions?.filter((x) => x.ticker == this.ticker)
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
    totalDividendsEarned() {
      const history = this.dividendHistory
      const transactions = this.adjustedStockTransactions
      if (!history || !transactions) return 0

      // Sort both ascending by date
      const sortedDivs = [...history].sort(
        (a, b) => new Date(a.ex_dividend_date) - new Date(b.ex_dividend_date),
      )

      let totalEarned = 0

      sortedDivs.forEach((div) => {
        const exDate = new Date(div.ex_dividend_date)

        // Find holdings BEFORE ex-dividend date
        const relevantTrans = transactions.filter((t) => new Date(t.transaction_date) < exDate)

        const sharesOwned = relevantTrans.reduce((acc, t) => {
          return t.buying ? acc + t.share_count : acc - t.share_count
        }, 0)

        // Assuming dividend history amounts are per-share (split-adjusted if source is adjusted)
        // If sharesOwned > 0, add to total
        if (sharesOwned > 0) {
          totalEarned += sharesOwned * Number(div.amount)
        }
      })

      return totalEarned
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
<style lang="scss" scoped>
.stock-header {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 25px;
}

.stock-logo {
  width: 60px;
  height: 60px;
  overflow: hidden;
  border-radius: 5px;
  background-color: rgb(255, 255, 255, 0.05);

  img {
    width: 100%;
    height: 100%;
    object-fit: fill;
  }
}

.stock-ticker {
  font-size: 26px;
  font-weight: bold;
}

.stock-name {
  font-size: 18px;
  font-weight: 500;
  color: #aaa;
}

.stock-desc {
  font-weight: bold;
  color: #888;
  margin-bottom: 15px;
}

.analysis-event {
  border-left: 3px solid #555;
  margin: 15px 0px;
  padding-left: 15px;

  .ae-title {
    color: #7cff7c;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 16px;
  }

  .ae-content {
    font-weight: 500;
    color: #ccc;
  }
}

.dividend-chart {
  margin-top: 15px;
  height: 250px;
}

.growth-row {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.growth-item {
  display: flex;
  flex-direction: column;
}

.gi-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #888;
  font-weight: 600;
}

.gi-value {
  font-size: 22px;
  font-weight: 700;
  margin: 4px 0 2px 0;
  display: flex;
  align-items: center;
}

.gi-sub {
  font-size: 11px;
  color: #555;
  font-weight: 500;
}

.text-pos {
  color: #4caf50;
}

.text-neg {
  color: #ef5350;
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

.section-header {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #aaa;
  margin-bottom: 10px;
  border-left: 3px solid #06d671;
  padding-left: 10px;
}

.total-earned {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}
</style>

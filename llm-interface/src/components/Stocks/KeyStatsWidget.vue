<template>
  <div>
    <h6>Key Stats</h6>
    <div class="stat-wrapper">
      <div class="stat-col">
        <div class="stat-item">
          <div>Market Cap</div>
          <div class="stat-item-divider"></div>
          <div>{{ marketCap }}</div>
        </div>
        <div class="stat-item">
          <div>Revenue Growth (QoQ)</div>
          <div class="stat-item-divider"></div>
          <div>{{ qoqRevenueGrowth }}%</div>
        </div>
        <div class="stat-item">
          <div>Revenue Growth (YoY)</div>
          <div class="stat-item-divider"></div>
          <div>{{ yoyRevenueGrowth }}%</div>
        </div>
        <div class="stat-item">
          <div>3Y Revenue CAGR</div>
          <div class="stat-item-divider"></div>
          <div>{{ revenue3yCAGR }}%</div>
        </div>
        <div class="stat-item">
          <div>5Y Revenue CAGR</div>
          <div class="stat-item-divider"></div>
          <div>{{ revenue5yCAGR }}%</div>
        </div>
        <div class="stat-item">
          <div>10Y Revenue CAGR</div>
          <div class="stat-item-divider"></div>
          <div>{{ revenue10yCAGR }}%</div>
        </div>
        <div class="stat-item">
          <div>3Y Earnings CAGR</div>
          <div class="stat-item-divider"></div>
          <div>{{ earnings3yCAGR }}%</div>
        </div>
        <div class="stat-item">
          <div>5Y Earnings CAGR</div>
          <div class="stat-item-divider"></div>
          <div>{{ earnings5yCAGR }}%</div>
        </div>
        <div class="stat-item">
          <div>10Y Earnings CAGR</div>
          <div class="stat-item-divider"></div>
          <div>{{ earnings10yCAGR }}%</div>
        </div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-col">
        <div class="stat-item">
          <div>Gross Margin</div>
          <div class="stat-item-divider"></div>
          <div>{{ grossMargin }}%</div>
        </div>
        <div class="stat-item">
          <div>Operating Margin</div>
          <div class="stat-item-divider"></div>
          <div>{{ operatingMargin }}%</div>
        </div>
        <div class="stat-item">
          <div>Profit Margin</div>
          <div class="stat-item-divider"></div>
          <div>{{ profitMargin }}%</div>
        </div>
      </div>
    </div>
    {{ quarterlyReports[0] }}
  </div>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'KeyStatsWidget',
  props: {
    ticker: {
      type: String,
      required: true,
    },
  },
  mounted() {
    console.log(useStore().loadedInfo)
  },
  computed: {
    stockInfo() {
      return useStore().loadedInfo[this.ticker]
    },
    marketCap() {
      if (!this.stockInfo?.shares_outstanding || !this.stockInfo?.latest_price) return 0
      return this.stockInfo.shares_outstanding * this.stockInfo.latest_price
    },
    annualReports() {
      return useStore()._incomeReports[this.ticker]?.annual_income
    },
    quarterlyReports() {
      return useStore()._incomeReports[this.ticker]?.quarterly_income
    },
    latestIncomeReport() {
      let annualReports = this.annualReports
      return annualReports?.[0]
    },
    grossMargin() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 0
      let revenue = latestIncomeReport['totalRevenue']
      let costOfRevenue = latestIncomeReport['costOfRevenue']
      return (((revenue - costOfRevenue) / revenue) * 100).toFixed(2)
    },
    operatingMargin() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 0
      let revenue = latestIncomeReport['totalRevenue']
      let costOfRevenue = latestIncomeReport['costOfRevenue']
      let operatingExpense = latestIncomeReport['operatingExpenses']
      return (((revenue - costOfRevenue - operatingExpense) / revenue) * 100).toFixed(2)
    },
    profitMargin() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 0
      let revenue = latestIncomeReport['totalRevenue']
      let netIncome = latestIncomeReport['netIncome']
      return ((netIncome / revenue) * 100).toFixed(2)
    },
    yoyRevenueGrowth() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 0
      let revenue = latestIncomeReport['totalRevenue']
      let previousRevenue = this.annualReports?.[1]['totalRevenue']
      return (((revenue - previousRevenue) / previousRevenue) * 100).toFixed(2)
    },
    qoqRevenueGrowth() {
      let latestIncomeReport = this.quarterlyReports?.[0]
      if (!latestIncomeReport) return 0
      let revenue = latestIncomeReport['totalRevenue']
      let previousRevenue = this.quarterlyReports?.[1]['totalRevenue']
      return (((revenue - previousRevenue) / previousRevenue) * 100).toFixed(2)
    },
    revenue3yCAGR() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 'NaN'
      let revenue = latestIncomeReport['totalRevenue']
      let previousRevenue = this.annualReports?.[3]?.['totalRevenue']
      if (!previousRevenue) return 'NaN'
      return ((Math.pow(revenue / previousRevenue, 1 / 3) - 1) * 100).toFixed(2)
    },
    revenue5yCAGR() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 'NaN'
      let revenue = latestIncomeReport['totalRevenue']
      let previousRevenue = this.annualReports?.[5]?.['totalRevenue']
      if (!previousRevenue) return 'NaN'
      return ((Math.pow(revenue / previousRevenue, 1 / 5) - 1) * 100).toFixed(2)
    },
    revenue10yCAGR() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 'NaN'
      let revenue = latestIncomeReport['totalRevenue']
      let previousRevenue = this.annualReports?.[10]?.['totalRevenue']
      if (!previousRevenue) return 'NaN'
      return ((Math.pow(revenue / previousRevenue, 1 / 10) - 1) * 100).toFixed(2)
    },
    earnings3yCAGR() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 'NaN'
      let earnings = latestIncomeReport['grossProfit']
      let previousEarnings = this.annualReports?.[3]?.['grossProfit']
      if (!previousEarnings) return 'NaN'
      return ((Math.pow(earnings / previousEarnings, 1 / 3) - 1) * 100).toFixed(2)
    },
    earnings5yCAGR() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 'NaN'
      let earnings = latestIncomeReport['grossProfit']
      let previousEarnings = this.annualReports?.[5]?.['grossProfit']
      if (!previousEarnings) return 'NaN'
      return ((Math.pow(earnings / previousEarnings, 1 / 5) - 1) * 100).toFixed(2)
    },
    earnings10yCAGR() {
      let latestIncomeReport = this.latestIncomeReport
      if (!latestIncomeReport) return 'NaN'
      let earnings = latestIncomeReport['grossProfit']
      let previousEarnings = this.annualReports?.[10]?.['grossProfit']
      if (!previousEarnings) return 'NaN'
      return ((Math.pow(earnings / previousEarnings, 1 / 10) - 1) * 100).toFixed(2)
    },
  },
})
</script>

<style scoped>
.stat-wrapper {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.stat-col {
  flex: 1;
}
.stat-divider {
  width: 2px;
  background-color: #222;
  margin: 5px 5vw;
}

.stat-item {
  padding: 5px 0px;
  display: flex;
  gap: 30px;
  align-items: center;
  font-size: 14px;
  color: #aaa;
  font-weight: bold;
}

.stat-item-divider {
  height: 2px;
  background-color: #222;
  flex: 1;
}
</style>

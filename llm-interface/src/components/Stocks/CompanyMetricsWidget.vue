<template>
  <div class="q-my-md">
    <h6>Company Metrics</h6>
    <div class="q-my-md">
      <q-tabs
        v-model="tab"
        class="custom-tabs"
        indicator-color="transparent"
        align="left"
        dense
        no-caps
        shrink
      >
        <q-tab name="annual" label="Annual (TTM)" :ripple="false" />
        <q-tab name="quarterly" label="Quarterly" :ripple="false" />
      </q-tabs>
    </div>
    <div class="metric-charts">
      <div class="chart-col">
        <div class="chart-title">Income Overview</div>
        <div class="chart-key">
          <div class="key-item">
            <div class="dot revenue-dot"></div>
            Revenue
          </div>
          <div class="key-item">
            <div class="dot earnings-dot"></div>
            Earnings
          </div>
        </div>
        <div class="chart-container">
          <bar-chart v-if="tab == 'quarterly'" v-bind="quarterlyIncomeData" />
          <bar-chart v-if="tab == 'annual'" v-bind="annualIncomeData" />
        </div>
      </div>
      <div class="chart-col">
        <div class="chart-title">Net Income</div>
        <div class="chart-key">
          <div class="key-item">
            <div class="dot net-income-dot"></div>
            Net Income
          </div>
        </div>
        <div class="chart-container">
          <bar-chart v-if="tab == 'quarterly'" v-bind="quarterlyNetIncomeData" />
          <bar-chart v-if="tab == 'annual'" v-bind="annualNetIncomeData" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'
import BarChart from 'src/components/Charts/BarChart.vue'

export default defineComponent({
  name: 'CompanyMetricsWidget',
  components: {
    BarChart,
  },
  data() {
    return {
      tab: 'quarterly',
    }
  },
  props: {
    ticker: {
      type: String,
    },
  },
  computed: {
    quarterlyIncomeData() {
      let quarterlyIncomeData = useStore()._incomeReports[this.ticker]?.quarterly_income?.slice(
        0,
        18,
      )
      let ret = {
        datasets: [],
        labels: [],
      }
      const thickness = 10
      if (quarterlyIncomeData) {
        ret.labels = quarterlyIncomeData.map((x) => x.fiscalDateEnding)
        ret.datasets.push({
          label: 'Revenue',
          data: quarterlyIncomeData.map((x) => x.totalRevenue),
          backgroundColor: 'rgb(255, 99, 132)',
          barThickness: thickness,
          borderRadius: thickness,
          borderWidth: 3,
        })
        ret.datasets.push({
          label: 'Earnings',
          data: quarterlyIncomeData.map((x) => x.grossProfit),
          backgroundColor: 'rgb(75, 192, 192)',
          barThickness: thickness,
          borderRadius: thickness,
          borderWidth: 3,
        })
      }
      return ret
    },
    annualIncomeData() {
      let annualIncomeData = useStore()._incomeReports[this.ticker]?.annual_income
      let ret = {
        datasets: [],
        labels: [],
      }
      const thickness = 10
      if (annualIncomeData) {
        ret.labels = annualIncomeData.map((x) => x.fiscalDateEnding)
        ret.datasets.push({
          label: 'Revenue',
          data: annualIncomeData.map((x) => x.totalRevenue),
          backgroundColor: 'rgb(255, 99, 132)',
          barThickness: thickness,
          borderRadius: thickness,
          borderWidth: 3,
        })
        ret.datasets.push({
          label: 'Earnings',
          data: annualIncomeData.map((x) => x.grossProfit),
          backgroundColor: 'rgb(75, 192, 192)',
          barThickness: thickness,
          borderRadius: thickness,
          borderWidth: 3,
        })
      }
      return ret
    },
    quarterlyNetIncomeData() {
      let quarterlyIncomeData = useStore()._incomeReports[this.ticker]?.quarterly_income?.slice(
        0,
        18,
      )
      let ret = {
        datasets: [],
        labels: [],
      }
      const thickness = 10
      if (quarterlyIncomeData) {
        ret.labels = quarterlyIncomeData.map((x) => x.fiscalDateEnding)
        ret.datasets.push({
          label: 'Net Income',
          data: quarterlyIncomeData.map((x) => x.netIncome),
          backgroundColor: 'rgb(255, 146, 219)',
          barThickness: thickness,
          borderRadius: thickness,
          borderWidth: 3,
        })
      }
      return ret
    },
    annualNetIncomeData() {
      let annualIncomeData = useStore()._incomeReports[this.ticker]?.annual_income
      let ret = {
        datasets: [],
        labels: [],
      }
      const thickness = 10
      if (annualIncomeData) {
        ret.labels = annualIncomeData.map((x) => x.fiscalDateEnding)
        ret.datasets.push({
          label: 'Net Income',
          data: annualIncomeData.map((x) => x.netIncome),
          backgroundColor: 'rgb(255, 146, 219)',
          barThickness: thickness,
          borderRadius: thickness,
          borderWidth: 3,
        })
      }
      return ret
    },
  },
})
</script>
<style lang="scss" scoped>
.metric-charts {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
}

.chart-col {
  flex: 1;
  min-width: 300px;
  max-width: 95vw;
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
}

.chart-key {
  display: flex;
  gap: 15px;
  margin: 10px 0;
}

.key-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: bold;
  color: #888;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  &.revenue-dot {
    background-color: rgb(255, 99, 132);
  }
  &.earnings-dot {
    background-color: rgb(75, 192, 192);
  }

  &.net-income-dot {
    background-color: rgb(255, 146, 219);
  }
}

.chart-container {
  height: 300px;
  max-height: 50vw;
}

.custom-tabs {
  display: inline-flex;
  background: #282828;
  padding: 5px 0px;
  border-radius: 500px;

  :deep(.q-tab) {
    min-height: 28px;
    border-radius: 20px;
    padding: 0 16px;
    font-size: 13px;
    font-weight: 600;
    margin: 0 5px;
    color: #ccc;
    transition: all 0.2s ease;
    text-transform: capitalize;

    &.q-tab--active {
      color: #000;
      background: #aaa; /* Dark pill background */
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

      .q-tab__content::after {
        display: none; /* No dot */
      }
    }

    &:hover:not(.q-tab--active) {
      color: #ccc;
      background: rgba(255, 255, 255, 0.03);
    }

    .q-tab__indicator {
      display: none;
    }

    .q-tab__content {
      padding: 0;
    }
  }
}
</style>

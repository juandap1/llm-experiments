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
    <div class="q-my-xs">
      <div class="chart-title">Income Overview</div>
      <div class="chart-key">
        <div class="key-item">
          <div class="revenue-dot"></div>
          Revenue
        </div>
        <div class="key-item">
          <div class="earnings-dot"></div>
          Earnings
        </div>
      </div>
      <div class="chart-container">
        <bar-chart v-if="tab == 'quarterly'" v-bind="quarterlyIncomeData" />
        <bar-chart v-if="tab == 'annual'" v-bind="annualIncomeData" />
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
      let quarterlyIncomeData = useStore()
        ._incomeReports[this.ticker]?.quarterly_income?.sort((a, b) => {
          return new Date(a.fiscalDateEnding) - new Date(b.fiscalDateEnding)
        })
        .slice(-12)
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
      let annualIncomeData = useStore()
        ._incomeReports[this.ticker]?.annual_income?.sort((a, b) => {
          return new Date(a.fiscalDateEnding) - new Date(b.fiscalDateEnding)
        })
        .slice(-12)
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
  },
})
</script>
<style lang="scss" scoped>
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

.revenue-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: rgb(255, 99, 132);
}
.earnings-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: rgb(75, 192, 192);
}

.chart-container {
  height: 300px;
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

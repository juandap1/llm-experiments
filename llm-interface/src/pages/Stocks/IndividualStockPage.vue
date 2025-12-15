<template>
  <q-page class="basic-page">
    <div class="stock-header">
      <div class="flex items-center" style="gap: 15px">
        <div class="stock-logo">
          <img :src="`http://localhost:3141/logo/${ticker}`" alt="Stock ticker logo" />
        </div>
        <div>
          <div class="stock-ticker">{{ stockInfo?.ticker }}</div>
          <div class="stock-name">{{ stockInfo?.name }}</div>
        </div>
      </div>
      <q-btn flat no-caps class="refresh-btn" @click="refreshData" :loading="refreshing">
        <q-icon name="fas fa-sync-alt" size="12px" class="q-mr-sm" />
        <div>Refresh</div>
      </q-btn>
    </div>
    <div class="q-mb-lg">
      <q-tabs
        v-model="tab"
        class="custom-tabs"
        indicator-color="transparent"
        active-color="white"
        align="left"
        dense
        no-caps
        shrink
      >
        <q-tab name="overview" label="Overview" :ripple="false" />
        <q-tab name="dividends" label="Dividends" :ripple="false" />
        <q-tab name="history" label="History" :ripple="false" />
      </q-tabs>
    </div>

    <q-tab-panels v-model="tab" animated class="bg-transparent text-white">
      <q-tab-panel name="overview" class="q-pa-none">
        <price-chart-widget
          :history="stockHistory"
          :portfolioBalance="value"
          :invested="invested"
          :ticker="ticker"
          individual
        />
        <div class="analysis-widget" v-if="analysis">
          <h6><q-icon name="fas fa-star-of-life" /> {{ analysis['general_headline'] }}</h6>
          <div class="text-grey-6 text-italic q-mb-md" style="font-size: 11px">
            Last Updated: {{ formatDate(stockInfo?.analysis_updated) }}
          </div>
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
        <company-metrics-widget :ticker="ticker" />
        <key-stats-widget :ticker="ticker" />
      </q-tab-panel>

      <q-tab-panel name="dividends" class="q-pa-none">
        <individual-dividend-view :ticker="ticker" />
      </q-tab-panel>

      <q-tab-panel name="history" class="q-pa-none">
        <history-widget :transactions="stockTransactions" />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from 'src/components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'
import PriceChartWidget from 'src/components/Stocks/PriceChartWidget.vue'
import IndividualDividendView from 'src/components/Stocks/IndividualDividendView.vue'
import CompanyMetricsWidget from 'src/components/Stocks/CompanyMetricsWidget.vue'
import KeyStatsWidget from 'src/components/Stocks/KeyStatsWidget.vue'

export default defineComponent({
  name: 'IndividualStockPage',
  components: {
    HistoryWidget,
    PriceChartWidget,
    IndividualDividendView,
    CompanyMetricsWidget,
    KeyStatsWidget,
  },
  data() {
    return {
      tab: 'overview',
      refreshing: false,
    }
  },
  mounted() {
    useStore().getStockIncomeReports(this.ticker)
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
    holding() {
      return useStore().holding_map?.[this.ticker]
    },
    shareCount() {
      return this.holding?.reduce((a, b) => a + b.shares, 0)
    },
    analysis() {
      if (!this.stockInfo?.analysis || this.stockInfo.analysis == 'loading...') return null
      if (typeof this.stockInfo.analysis == 'string')
        return JSON.parse(this.removeControlCharacters(this.stockInfo.analysis))
      return this.stockInfo.analysis
    },
    stockTransactions() {
      return useStore().transactions?.filter((x) => x.ticker == this.ticker)
    },
    adjustedStockTransactions() {
      return useStore().adjustedTransactions?.filter((x) => x.ticker == this.ticker)
    },
  },
  methods: {
    removeControlCharacters(jsonString) {
      // Regex: Finds all ASCII control characters (U+0000 to U+001F)
      // which includes the newlines, tabs, and other non-printable characters.
      return jsonString.replace(/[\u0000-\u001F]/g, '')
    },
    async refreshData() {
      this.refreshing = true
      const store = useStore()
      let response = await store.refreshStock(this.ticker)
      let data = response.data
      store._loadedInfo[this.ticker] = {
        ticker: this.ticker,
        name: data['name'],
        description: data['description'],
        latest_price: data['latest_price'],
        sector: data['sector'],
        industry: data['industry'],
        analysis: data['analysis'],
        analysis_updated: data['analysis_updated'],
        book_value: data['book_value'],
        earnings_per_share: data['earnings_per_share'],
        revenue_per_share: data['revenue_per_share'],
        dividend_per_share: data['dividend_per_share'],
        shares_outstanding: data['shares_outstanding'],
        analyst_target_price: data['analyst_target_price'],
        ebitda: data['ebitda'],
      }
      store._history[this.ticker] = data.price_history
      store._splitHistory[this.ticker] = data.split_history
      store._dividends[this.ticker] = data.dividend_history
      setTimeout(() => {
        this.refreshing = false
      }, 500)
    },
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
  align-items: center;
  justify-content: space-between;
  margin-bottom: 25px;
}

.refresh-btn {
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  color: #888;
  font-weight: 600;
  font-size: 11px;
  padding: 4px 12px;
  min-height: 32px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }
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

.custom-tabs {
  background: transparent;
  padding: 0;

  :deep(.q-tab) {
    min-height: 32px;
    border-radius: 20px;
    padding: 0 16px;
    margin-right: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #777;
    transition: all 0.2s ease;
    text-transform: capitalize;

    &.q-tab--active {
      color: #fff;
      background: #333; /* Dark pill background */
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

      .q-tab__content::after {
        display: none; /* No dot */
      }
    }

    &:hover:not(.q-tab--active) {
      color: #aaa;
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

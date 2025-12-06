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

export default defineComponent({
  name: 'IndividualStockPage',
  components: { HistoryWidget, PriceChartWidget, IndividualDividendView },
  data() {
    return {
      tab: 'overview',
    }
  },
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
    adjustedStockTransactions() {
      return useStore().adjustedTransactions?.filter((x) => x.ticker == this.ticker)
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

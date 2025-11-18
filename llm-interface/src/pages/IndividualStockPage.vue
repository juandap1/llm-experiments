<template>
  <q-page class="basic-page">
    <div class="stock-header">
      <div class="stock-logo">
        <img src="http://localhost:3141/logo/MSFT" alt="Stock ticker logo" />
      </div>
      <div>
        <div class="stock-ticker">{{ stockInfo?.ticker }}</div>
        <div class="stock-name">{{ stockInfo?.name }}</div>
      </div>
    </div>
    <price-chart-widget />
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
    <history-widget />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from '../components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'
import PriceChartWidget from '../components/Stocks/PriceChartWidget.vue'

export default defineComponent({
  name: 'IndividualStockPage',
  components: { HistoryWidget, PriceChartWidget },
  mounted() {
    useStore().getStockInfo('MSFT')
  },
  computed: {
    stockInfo() {
      return useStore().loadedInfo['MSFT']
    },
    analysis() {
      if (!this.stockInfo?.analysis || this.stockInfo.analysis == 'loading...') return null
      return JSON.parse(this.stockInfo.analysis)
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
</style>

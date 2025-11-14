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
</style>

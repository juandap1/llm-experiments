<template>
  <q-page class="basic-page">
    <h6>My Portfolio</h6>
    <!-- <price-chart-widget /> -->
    <div class="asset-widget">
      <h6>Assets</h6>
      <div class="bar-cont">
        <div
          class="bar-seg"
          v-for="i in Object.keys(assetBreakdown)"
          :key="i"
          :style="{
            width: `${assetRatio[i]}%`,
            'background-color': colors[i],
          }"
        ></div>
      </div>
      <div class="asset-list">
        <div class="asset-item" v-for="i in Object.keys(assetBreakdown)" :key="i">
          <div class="asset-name">
            <div class="color-key" :style="{ 'background-color': colors[i] }"></div>
            <div>{{ capitalizeFirst(i) }}</div>
          </div>
          <div>
            <div class="asset-val">${{ assetBreakdown[i].toFixed(2) }}</div>
            <div class="asset-ratio">{{ assetRatio[i] }}%</div>
          </div>
        </div>
      </div>
    </div>
    <history-widget :transactions="allTransactions" />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from '../components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'
// import PriceChartWidget from '../components/Stocks/PriceChartWidget.vue'

export default defineComponent({
  name: 'StocksPage',
  components: { HistoryWidget },
  setup() {
    return {
      store: useStore(),
      colors: {
        stocks: '#A7C7E7', // pastel blue
        etfs: '#F7C8A0', // pastel peach/orange
        cash: '#A8E6A3', // pastel green
      },
    }
  },
  methods: {
    capitalizeFirst(str) {
      if (!str) return ''
      return str.charAt(0).toUpperCase() + str.slice(1)
    },
  },
  mounted() {},
  computed: {
    allTransactions() {
      return useStore().transactions
    },
    assetBreakdown() {
      let breakdown = {
        stocks: 0,
        etfs: 0,
        cash: 25087.27,
      }
      return this.store.currently_holding?.reduce((acc, item) => {
        let asset = this.store.loadedInfo[item]
        if (!asset?.latest_price || asset.latest_price == -1) return acc
        let val = this.store.value_map?.[item]
        if (asset.is_etf) {
          acc.etfs += val
        } else {
          acc.stocks += val
        }
        return acc
      }, breakdown)
    },
    assetRatio() {
      let values = this.assetBreakdown
      let total = Object.values(values).reduce((a, v) => a + v, 0)

      let props = {}
      let sum = 0
      let largestKey = null
      let largestVal = -Infinity

      for (let key in values) {
        let pct = Math.round((values[key] / total) * 100)
        props[key] = pct
        sum += pct

        if (pct > largestVal) {
          largestVal = pct
          largestKey = key
        }
      }
      props[largestKey] -= sum - 100
      return props
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

.asset-widget {
  border: 1px solid #333;
  border-radius: 20px;
  padding: 20px;
  width: 400px;
}

.bar-cont {
  margin: 20px 0px;
  border-radius: 50px;
  width: 100%;
  height: 10px;
  background-color: rgb(255, 255, 255, 0.1);
  display: flex;
  overflow: hidden;
}

.bar-seg {
  height: 100%;
  transition: all 0.3s;
}

.asset-item {
  display: flex;
  align-items: start;
  gap: 5px;
  padding: 5px 0px;

  .color-key {
    width: 10px;
    height: 10px;
  }

  .asset-name {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1 1 auto;
    font-weight: bold;
    font-size: 16px;
  }

  .asset-val {
    font-weight: bold;
  }

  .asset-ratio {
    color: #aaa;
    font-size: 13px;
    font-weight: bold;
    text-align: end;
  }
}
</style>

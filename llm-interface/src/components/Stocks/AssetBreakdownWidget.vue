<template>
  <div class="asset-widget">
    <h6>Assets</h6>
    <!--Switch out bar for dashed bar-->
    <div class="bar-cont" @mouseleave="hovered = null">
      <div
        class="bar-seg"
        v-for="(type, i) in segments"
        :key="i"
        @mouseenter="hovered = type"
        :style="{
          'background-color': colors[type],
          opacity: hovered && hovered !== type ? 0.2 : 1,
        }"
      ></div>
    </div>
    <div class="asset-list">
      <div
        class="asset-item"
        v-for="i in Object.keys(assetBreakdown)"
        :key="i"
        @mouseenter="hovered = i"
        @mouseleave="hovered = null"
        :style="{ opacity: hovered && hovered !== i ? 0.2 : 1 }"
      >
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
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useStore } from 'src/stores/store'

export default defineComponent({
  name: 'AssetBreakdownWidget',
  setup() {
    const hovered = ref(null)
    return {
      store: useStore(),
      hovered,
      colors: {
        stocks: '#3b82f6', // Blue
        etfs: '#a855f7', // Purple
        cash: '#22c55e', // Green
      },
    }
  },
  methods: {
    capitalizeFirst(str) {
      if (!str) return ''
      return str.charAt(0).toUpperCase() + str.slice(1)
    },
  },
  computed: {
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
      if (largestKey) {
        props[largestKey] -= sum - 100
      }
      return props
    },
    segments() {
      const ratios = this.assetRatio
      const keys = Object.keys(ratios)
      let cumulative = 0
      const thresholds = keys.map((key) => {
        cumulative += ratios[key]
        return { key, threshold: cumulative }
      })

      const segs = []
      for (let i = 0; i < 50; i++) {
        const midpoint = i * 2 + 1
        const match = thresholds.find((t) => midpoint <= t.threshold)
        segs.push(match ? match.key : keys[keys.length - 1])
      }
      return segs
    },
  },
})
</script>
<style lang="scss" scoped>
.asset-widget {
  border: 1px solid #333;
  border-radius: 20px;
  padding: 20px;
  width: 400px;
}

.bar-cont {
  margin: 20px 0px;
  width: 100%;
  height: 12px;
  display: flex;
  gap: 2px;
}

.bar-seg {
  flex: 1;
  height: 100%;
  transition: all 0.3s;
  border-radius: 2px;
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

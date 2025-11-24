<template>
  <tr class="stock-item" v-if="stockInfo">
    <th scope="row" class="asset-col text-left">
      <div class="item-info">
        <q-img class="stock-logo" :src="`http://localhost:3141/logo/${ticker}`" loading="lazy" />
        <div class="text-col">
          <div class="item-ticker">{{ ticker }}</div>
          <div class="item-name">{{ stockInfo.name }}</div>
        </div>
      </div>
    </th>
    <td class="text-right">${{ stockInfo.latest_price.toFixed(2) }}</td>
    <td class="text-right">{{ holding.toFixed(2) }}</td>
    <td class="text-right">${{ avgCost.toFixed(2) }}</td>
    <td class="text-right font-weight-bold">${{ value.toFixed(2) }}</td>
    <td class="text-right">
      <div class="return-col" :class="{ positive: diff > 0, negative: diff < 0 }">
        <div class="return-val">{{ diff > 0 ? '+' : '' }}{{ diff.toFixed(2) }}</div>
        <div class="return-pct">{{ roi > 0 ? '+' : '' }}{{ roi?.toFixed(2) }}%</div>
      </div>
    </td>
    <td class="allocation-col">
      <div class="allocation-wrapper">
        <div class="ratio-text">{{ ratio.toFixed(1) }}%</div>
        <div class="ratio-track">
          <div class="ratio-fill" :style="{ width: ratio + '%' }"></div>
        </div>
      </div>
    </td>
  </tr>
</template>
<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'StockHoldingItem',
  props: {
    ticker: {
      type: String,
      required: true,
    },
    value: {
      type: Number,
      required: true,
    },
    totalValue: {
      type: Number,
      required: true,
    },
  },
  setup() {
    return {
      store: useStore(),
    }
  },
  computed: {
    stockInfo() {
      return this.store.loadedInfo[this.ticker]
    },
    holding() {
      return this.store.holding_map?.[this.ticker]?.reduce((acc, x) => acc + x.shares, 0)
    },
    ratio() {
      return (this.value / this.totalValue) * 100
    },
    bought() {
      return this.store.holding_map?.[this.ticker]?.reduce(
        (acc, x) => acc + x.shares * x.cost_per_share,
        0,
      )
    },
    roi() {
      return ((this.value - this.bought) / this.bought) * 100
    },
    diff() {
      return this.value - this.bought
    },
    avgCost() {
      return this.holding ? this.bought / this.holding : 0
    },
  },
})
</script>
<style lang="scss" scoped>
.stock-item {
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.03);
  }

  td,
  th {
    padding: 12px 16px;
    vertical-align: middle;
    font-size: 0.9rem;
    color: #eee;
    font-weight: normal; /* Reset th bold */
  }
}

.asset-col {
  width: 250px;
  border: none; /* Fix potential border issues on th */
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #222;
}

.text-col {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.item-ticker {
  font-weight: 700;
  font-size: 0.95rem;
  color: #fff;
}

.item-name {
  font-size: 0.75rem;
  color: #888;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.return-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.2;

  &.positive {
    color: #4caf50;
  }
  &.negative {
    color: #ef5350;
  }
}

.return-val {
  font-weight: 600;
}

.return-pct {
  font-size: 0.75rem;
  opacity: 0.8;
}

.allocation-col {
  width: 150px;
}

.allocation-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.ratio-text {
  font-size: 0.8rem;
  color: #aaa;
  width: 40px;
  text-align: right;
}

.ratio-track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  min-width: 60px;
}

.ratio-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 3px;
}

.font-weight-bold {
  font-weight: 600;
}
</style>

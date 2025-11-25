<template>
  <div class="sector-widget">
    <div class="header-section">
      <h6>Sector Allocation</h6>
      <div class="subtitle">Portfolio Diversification</div>
    </div>

    <div class="sector-chart">
      <DashedCircleChart
        :data="chartData"
        :colors="sectorColors"
        :totalValue="totalValue"
        v-model:hoveredTicker="hoveredSector"
        :size="280"
        :totalRects="150"
      />
    </div>

    <div class="divider"></div>

    <div class="sector-list">
      <div
        v-for="item in sectorData"
        :key="item.sector"
        class="sector-item"
        :class="{ hovered: hoveredSector === item.sector }"
        @mouseenter="hoveredSector = item.sector"
        @mouseleave="hoveredSector = null"
      >
        <div class="sector-info">
          <div class="sector-color" :style="{ background: item.color }"></div>
          <div class="sector-details">
            <span class="sector-name">{{ item.sector || 'Unknown' }}</span>
            <span class="sector-count"
              >{{ item.count }} {{ item.count === 1 ? 'stock' : 'stocks' }}</span
            >
            <div class="ticker-badges" :class="{ visible: hoveredSector === item.sector }">
              <span v-for="ticker in item.tickers" :key="ticker" class="ticker-badge">
                {{ ticker }}
              </span>
            </div>
          </div>
        </div>
        <div class="sector-right">
          <div class="sector-value">${{ item.value.toFixed(2) }}</div>
          <div class="sector-percentage">{{ item.percentage.toFixed(1) }}%</div>
        </div>
      </div>
      <div v-if="sectorData.length === 0" class="empty-state">No sector data available.</div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useStore } from 'src/stores/store'
import DashedCircleChart from 'src/components/Charts/DashedCircleChart.vue'

export default defineComponent({
  name: 'SectorBreakdownWidget',
  components: {
    DashedCircleChart,
  },
  setup() {
    return {
      store: useStore(),
    }
  },
  data() {
    return {
      hoveredSector: null,
      sectorColors: [
        '#C44E52',
        '#E85040',
        '#FF8C00',
        '#FFC300',
        '#D5BB60',
        '#79C74E',
        '#3CB371',
        '#00CED1',
        '#4C72B0',
        '#7B68EE',
        '#9467BD',
        '#C63A9A',
      ],
    }
  },
  computed: {
    sectorData() {
      const holdingMap = this.store.holding_map
      const loadedInfo = this.store.loadedInfo
      const valueMap = this.store.value_map

      if (!holdingMap) return []

      const sectorGroups = {}
      let totalValue = 0

      // Group holdings by sector (exclude ETFs)
      Object.keys(holdingMap).forEach((ticker) => {
        const info = loadedInfo[ticker]

        // Skip ETFs
        if (info?.is_etf) return

        const value = valueMap?.[ticker] || 0
        const sector = info?.sector || 'Unknown'

        if (!sectorGroups[sector]) {
          sectorGroups[sector] = {
            sector,
            value: 0,
            count: 0,
            tickers: [],
          }
        }

        sectorGroups[sector].value += value
        sectorGroups[sector].count += 1
        sectorGroups[sector].tickers.push(ticker)
        totalValue += value
      })

      // Convert to array and add percentages and colors
      return Object.values(sectorGroups)
        .map((group, index) => ({
          ...group,
          percentage: totalValue > 0 ? (group.value / totalValue) * 100 : 0,
          color: this.sectorColors[index % this.sectorColors.length],
        }))
        .sort((a, b) => b.value - a.value)
    },
    chartData() {
      // Transform sectorData to match the format expected by DashedCircleChart
      return this.sectorData.map((sector) => ({
        ticker: sector.sector,
        value: sector.value,
      }))
    },
    totalValue() {
      return this.sectorData.reduce((acc, sector) => acc + sector.value, 0)
    },
  },
  methods: {},
})
</script>

<style lang="scss" scoped>
.sector-widget {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 20px;
  backdrop-filter: blur(10px);
}

.header-section {
  h6 {
    margin: 0 0 5px 0;
    font-size: 1.1rem;
    font-weight: 600;
  }
}

.subtitle {
  font-size: 0.8rem;
  color: #888;
}

.sector-chart {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}

.divider {
  height: 1px;
  background: var(--border-color);
  opacity: 0.5;
}

.sector-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 2px;
  }
}

.sector-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  cursor: pointer;

  &:hover,
  &.hovered {
    background-color: rgba(255, 255, 255, 0.05);
  }
}

.sector-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sector-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.sector-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sector-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #fff;
}

.sector-count {
  font-size: 0.75rem;
  color: #888;
}

.ticker-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.3s ease;

  &.visible {
    max-height: 100px;
    opacity: 1;
  }
}

.ticker-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  color: #aaa;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.sector-right {
  text-align: right;
}

.sector-value {
  font-weight: 600;
  font-size: 0.9rem;
  color: #eee;
}

.sector-percentage {
  font-size: 0.75rem;
  color: #4caf50;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
  padding: 20px 0;
  font-style: italic;
}
</style>

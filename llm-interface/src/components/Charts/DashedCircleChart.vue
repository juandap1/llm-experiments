<template>
  <div class="knob-container">
    <svg :width="size" :height="size" viewBox="0 0 100 100">
      <g
        v-for="(item, index) in totalRects"
        :key="index"
        @mouseenter="$emit('update:hoveredTicker', processedData[index]?.ticker)"
        @mouseleave="$emit('update:hoveredTicker', null)"
      >
        <!-- Invisible Hit Area (Wider and Taller) -->
        <rect
          :x="43.5"
          :y="-2"
          width="5"
          height="10"
          fill="transparent"
          :transform="`rotate(${(360 / totalRects) * index + 90}, 50, 50)`"
        />
        <!-- Visible Dash -->
        <rect
          :x="45.5"
          :y="0"
          width="1"
          height="6"
          rx="0.5"
          ry="0.5"
          pointer-events="none"
          :fill="colors[processedData[index]?.count]"
          :transform="`rotate(${(360 / totalRects) * index + 90}, 50, 50)`"
          :style="{
            opacity: hoveredTicker && processedData[index]?.ticker !== hoveredTicker ? 0.2 : 1,
          }"
        />
      </g>
    </svg>
    <div class="val-vis">
      <div v-if="hoveredTicker && hoveredItem" class="column flex-center">
        <div class="text-caption text-grey-5">{{ hoveredTicker }}</div>
        <div>{{ formatPriceCompact(hoveredItem.value) }}</div>
      </div>
      <div v-else>{{ formatPriceCompact(totalValue) }}</div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['update:hoveredTicker'],
  setup() {
    return {}
  },
  props: {
    size: {
      type: Number,
      default: 360,
    },
    totalRects: {
      type: Number,
      default: 200, // Number of rectangles around the knob
    },
    data: {
      type: Array,
      default: () => [],
    },
    totalValue: {
      type: Number,
      default: 1,
    },
    colors: {
      type: Array,
      default: () => [],
    },
    hoveredTicker: {
      type: String,
      default: null,
    },
  },
  methods: {
    formatPriceCompact(price) {
      // Use 'en-US' locale as a standard, use 'currency' style, and enable 'compact' notation
      return new Intl.NumberFormat('en-US', {
        notation: 'compact',
        compactDisplay: 'short', // Use 'K' instead of 'thousand'
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0, // Avoid cents on large numbers
        maximumFractionDigits: 2, // Keep one decimal place if needed (e.g., 1.5K)
      }).format(price)
    },
  },
  computed: {
    hoveredItem() {
      if (!this.hoveredTicker) return null
      return this.data.find((x) => x.ticker === this.hoveredTicker)
    },
    processedData() {
      let assignedRects = 0
      const totalRects = this.totalRects // e.g., 200
      const totalValue = this.totalValue

      // 1. Calculate initial counts and store them
      let currentRects = this.data.map((x) => {
        // Calculate and floor the ideal number of rectangles
        let rectCount = Math.floor((x.value / totalValue) * totalRects)
        assignedRects += rectCount
        return {
          ticker: x.ticker || 'N/A', // Assuming ticker name is in x.ticker
          value: x.value,
          count: rectCount,
        }
      })

      // 2. Determine the deficit (the missing rectangles due to flooring)
      let deficit = totalRects - assignedRects

      // 3. Distribute the deficit to the largest remaining slices (first N elements)
      // Since the list is already sorted, we just iterate through the start of the array
      for (let i = 0; i < currentRects.length && deficit > 0; i++) {
        currentRects[i].count += 1
        deficit--
      }

      // 4. Flatten the final array and assign the correct count/index
      let finalRects = []
      let rectIndex = 0

      for (let i = 0; i < currentRects.length; i++) {
        const item = currentRects[i]

        // Only include items that were large enough to get at least one rectangle
        if (item.count > 0) {
          finalRects.push(
            ...Array(item.count).fill({
              ticker: item.ticker,
              value: item.value,
              count: rectIndex, // Use the item's position index in the chart
            }),
          )
          rectIndex++ // Increment the index for the next distinct ticker
        }
      }

      return finalRects
    },
  },
}
</script>

<style scoped>
.knob-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

svg {
  transform: rotate(-90deg); /* To start from the top */
}

rect {
  transition: all 0.3s ease;
}

.val-vis {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  font-weight: bold;
}
</style>

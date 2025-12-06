<template>
  <div class="growth-row" v-if="dividendGrowth">
    <template v-for="(data, label) in dividendGrowth" :key="label">
      <div v-if="data" class="growth-item">
        <div class="gi-header">
          <span class="gi-label">{{ label }} CAGR</span>
        </div>
        <div class="gi-value" :class="data.growth >= 0 ? 'text-pos' : 'text-neg'">
          <q-icon
            :name="data.growth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"
            size="10px"
            class="q-mr-xs"
          />
          {{ data.growth }}%
        </div>
        <div class="gi-sub">from ${{ data.pastAmount }}</div>
      </div>
    </template>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DividendGrowth',
  props: {
    dividendGrowth: {
      type: Object,
    },
  },
})
</script>
<style lang="css" scoped>
.growth-row {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.growth-item {
  display: flex;
  flex-direction: column;
}

.gi-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #888;
  font-weight: 600;
}

.gi-value {
  font-size: 22px;
  font-weight: 700;
  margin: 4px 0 2px 0;
  display: flex;
  align-items: center;
}

.gi-sub {
  font-size: 11px;
  color: #555;
  font-weight: 500;
}
</style>

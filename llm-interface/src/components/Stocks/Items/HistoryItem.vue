<template>
  <div class="hist-item">
    <div class="hist-row main">
      <div>{{ ticker }} market buy</div>
      <div>${{ cost }} <span class="price-change positive">+ 0.47%</span></div>
    </div>
    <div class="hist-row alt">
      <div>{{ date }}</div>
      <div>{{ share_count }} shares at ${{ share_price }}</div>
    </div>
    <hr />
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HistoryItem',
  props: {
    id: Number,
    ticker: String,
    share_count: Number,
    share_price: Number,
    transaction_date: String,
  },
  computed: {
    cost() {
      return (this.share_count * this.share_price).toFixed(2)
    },
    date() {
      let d = new Date(this.transaction_date)
      const options = {
        month: 'short', // "Sep"
        day: 'numeric', // "21"
        year: 'numeric', // "2025"
        timeZone: 'UTC',
      }
      const formattedDate = new Intl.DateTimeFormat('en-US', options).format(d)
      return formattedDate
    },
  },
})
</script>
<style lang="scss" scoped>
.hist-item {
  padding: 0px 10px;
}

.hist-row {
  display: flex;
  justify-content: space-between;

  :last-child {
    justify-content: flex-end;
  }
}

.hist-row.main {
  font-weight: bold;
}

.hist-row.alt {
  font-weight: bold;
  color: #aaa;
  font-size: 13px;
}

hr {
  border: none; /* Remove default borders */
  height: 1px; /* Set the height of the line */
  background-color: var(--border-color); /* Set the color of the line */
  margin: 10px 15px;
}

.price-change {
  border-radius: 50px;
  padding: 2px 10px;
  background-color: rgb(255, 255, 255, 0.1);
  font-size: 13px;
}

.price-change.positive {
  color: #7cff7c;
  background-color: #7cff7c35;
}
</style>

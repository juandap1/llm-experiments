<template>
  <q-page class="basic-page">
    <img src="http://localhost:3141/logo/MSFT" alt="Stock ticker logo" />
    <history-widget />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from '../components/Stocks/HistoryWidget.vue'
import { useStore } from 'src/stores/store'

export default defineComponent({
  name: 'StocksPage',
  components: { HistoryWidget },
  mounted() {
    useStore().getStockInfo('MSFT')
  },
})
</script>
<style scoped></style>

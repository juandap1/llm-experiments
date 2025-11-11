<template>
  <q-page class="basic-page">
    <img src="http://localhost:3141/logo/MSFT" alt="Stock ticker logo" />
    <history-widget />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import HistoryWidget from '../components/Stocks/HistoryWidget.vue'

export default defineComponent({
  name: 'StocksPage',
  components: { HistoryWidget },
})
</script>
<style scoped></style>

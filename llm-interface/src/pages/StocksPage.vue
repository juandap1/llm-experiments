<template>
  <q-page class="basic-page">
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

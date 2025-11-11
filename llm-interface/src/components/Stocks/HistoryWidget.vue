<template>
  <div class="basic-widget">
    <div class="widget-header">
      <h6>History</h6>
      <button class="alt-btn" @click="addModal = true">
        <q-icon name="fas fa-plus" />
        Add
      </button>
    </div>
    <template v-if="store.transactions != null">
      <history-item v-for="i in store.transactions" :key="i" v-bind="i" />
    </template>
    <q-dialog v-model="addModal">
      <div class="modal">
        <h6>Add Stock Purchase</h6>
        <div class="inp-wrapper">
          <q-input
            v-model="ticker"
            dark
            outlined
            dense
            placeholder="Stock Ticker (i.e. NVDA)"
          ></q-input>
        </div>
        <div class="inp-wrapper">
          <q-input
            type="number"
            v-model.number="count"
            dark
            outlined
            dense
            placeholder="Share Count"
          ></q-input>
        </div>
        <div class="inp-wrapper">
          <q-input
            prefix="$"
            type="number"
            v-model.number="price"
            dark
            outlined
            dense
            placeholder="Share Price"
          ></q-input>
        </div>
        <div class="inp-wrapper">
          <q-input
            type="date"
            v-model="purchaseDate"
            dark
            outlined
            dense
            placeholder="Purchase Date"
          ></q-input>
        </div>
        <div>Buying? <q-toggle v-model="buy" color="green" keep-color /></div>
        <button class="btn full" @click="addTransaction">Submit</button>
      </div>
    </q-dialog>
  </div>
</template>

<script>
import { api } from 'src/boot/axios'
import { defineComponent } from 'vue'
import HistoryItem from './Items/HistoryItem.vue'
import { useStore } from 'src/stores/store'

export default defineComponent({
  components: { HistoryItem },
  name: 'HistoryWidget',
  props: {},
  setup() {
    return {
      store: useStore(),
    }
  },
  data() {
    return {
      addModal: false,
      ticker: '',
      count: 0,
      price: 0,
      purchaseDate: '2025-11-08',
      buy: true,
    }
  },
  methods: {
    addTransaction() {
      let data = {
        ticker: this.ticker,
        share_count: this.count,
        share_price: this.price,
        transaction_date: this.purchaseDate,
        buying: this.buy,
      }
      console.log(data)
      api
        .post('/transaction', data)
        .then((response) => {
          console.log(response.data)
          this.addModal = false
          data.id = response.data.id
          //should be sorted
          this.store._transactions.unshift(data)
        })
        .catch((error) => {
          console.error('Error creating transaction:', error)
          this.addModal = false
        })
    },
  },
  mounted() {
    this.store.getTransactions()
  },
})
</script>
<style lang="scss" scoped>
.basic-widget {
  padding: 20px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.modal {
  width: 50vw;
  padding: 25px;
  border-radius: 25px;
  background-color: #222;
}

.inp-wrapper {
  margin: 20px 0px;
}
</style>

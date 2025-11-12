import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useStore = defineStore('counter', {
  state: () => ({
    _transactions: null,
    _loadedInfo: {},
    _history: {},
  }),

  getters: {
    transactions: (state) => state._transactions,
    loadedInfo: (state) => state._loadedInfo,
    history: (state) => state._history,
  },

  actions: {
    getStockInfo(ticker) {
      api
        .get('/stock/' + ticker, {
          params: {},
        })
        .then((response) => {
          // console.log(response)
          this._loadedInfo[ticker] = response.data
        })
        .catch(console.error)
    },
    getTransactions() {
      api
        .get('/transactions', {
          params: {},
        })
        .then((response) => {
          // console.log(response)
          this._transactions = response.data
        })
        .catch(console.error)
    },
    getStockHistory(ticker) {
      if (this._history[ticker] != null) return
      api
        .get('/stock/history/' + ticker, {
          params: {},
        })
        .then((response) => {
          // console.log(response)
          this._history[ticker] = response.data
        })
        .catch(console.error)
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}

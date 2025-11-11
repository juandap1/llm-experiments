import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useStore = defineStore('counter', {
  state: () => ({
    _history: null,
    _loadedInfo: {},
  }),

  getters: {
    history: (state) => state._history,
    loadedInfo: (state) => state._loadedInfo,
  },

  actions: {
    getStockInfo(ticker) {
      api
        .get('/stock/' + ticker, {
          params: {},
        })
        .then((response) => {
          console.log(response)
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
          console.log(response)
          this._history = response.data
        })
        .catch(console.error)
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}

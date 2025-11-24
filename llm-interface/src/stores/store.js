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
    holding_map: (state) =>
      state.transactions
        ?.slice()
        .reverse()
        .reduce((acc, item) => {
          if (acc[item.ticker] == null) {
            acc[item.ticker] = [] // This will store an ordered list of 'lots'
          }

          // Handle BUYING (Adding a new lot)
          if (item.buying) {
            acc[item.ticker].push({
              shares: item.share_count,
              cost_per_share: item.share_price,
            })
          }
          // Handle SELLING (Applying FIFO to remove lots)
          else {
            let shares_to_sell = item.share_count
            const lots = acc[item.ticker]

            while (shares_to_sell > 0 && lots.length > 0) {
              // FIFO: Always take from the FIRST lot (lots[0])
              if (lots.length == 0) break
              const first_lot = lots[0]

              if (first_lot.shares > shares_to_sell) {
                // Case 1: The first lot has MORE shares than we are selling.
                // Decrease the lot's shares and we're done with the sale.
                first_lot.shares -= shares_to_sell
                shares_to_sell = 0
              } else {
                // Case 2: The first lot has FEWER or EQUAL shares than we are selling.
                // The entire lot is consumed (removed).
                shares_to_sell -= first_lot.shares
                lots.shift()
              }
            }
            if (lots.length == 1 && lots[0].shares * lots[0].cost_per_share < 1) lots.shift()
            // No longer holding this stock
            if (lots.length == 0) delete acc[item.ticker]
          }

          return acc
        }, {}),
    currently_holding: (state) => {
      if (state.holding_map == null) return []
      return Object.keys(state.holding_map).filter((x) => state.holding_map[x].length != 0)
    },
    value_map: (state) =>
      state.currently_holding?.reduce((acc, item) => {
        let asset = state.loadedInfo[item]
        if (!asset?.latest_price || asset.latest_price == -1) return acc
        let val = state.holding_map[item].reduce((value, transaction) => {
          return value + transaction.shares * asset.latest_price
        }, 0)
        acc[item] = val
        return acc
      }, {}),
    invested() {
      return this.currently_holding.reduce((acc, item) => {
        acc += this.holding_map[item].reduce((value, transaction) => {
          return value + transaction.shares * transaction.cost_per_share
        }, 0)
        return acc
      }, 0)
    },
  },

  actions: {
    getStockInfo(ticker, refresh = false) {
      if (this.loadedInfo[ticker] && !refresh) return
      api
        .get('/stock/' + ticker, {
          params: {},
        })
        .then((response) => {
          // console.log(response)
          this._loadedInfo[ticker] = response.data
          if (!response.data.analysis) {
            this._loadedInfo[ticker].analysis = 'loading...'
            this.getStockAnalysis(ticker)
          }
        })
        .catch(console.error)
    },
    batchStockInfoRequest(tickers) {
      api
        .post('/stock/batch', {
          tickers,
        })
        .then((response) => {
          console.log(response.data)
          Object.assign(this._loadedInfo, response.data)
        })
        .catch((error) => {
          console.error('Error batch requesting stocks:', error)
        })
    },
    getTransactions() {
      api
        .get('/transactions', {
          params: {},
        })
        .then((response) => {
          // console.log(response)
          this._transactions = response.data
          let uniqueStocks = new Set(response.data.map((x) => x.ticker))
          this.batchStockInfoRequest(Array.from(uniqueStocks))
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
    getStockAnalysis(ticker) {
      let loadedInfo = this.loadedInfo[ticker]
      api
        .get('/stock/analysis', {
          params: {
            ticker,
            company: loadedInfo.name,
          },
        })
        .then((response) => {
          console.log(response)
          this._loadedInfo[ticker].analysis = response.data
        })
        .catch(console.error)
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}

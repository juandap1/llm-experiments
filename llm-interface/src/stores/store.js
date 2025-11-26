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
          console.log('history for ' + ticker)
          console.log(response)
          console.log('----------------')
          this._history[ticker] = response.data
        })
        .catch(console.error)
    },
    async batchStockHistoryRequest(tickers) {
      // Filter out tickers that already have history
      const tickersToFetch = tickers.filter((ticker) => this._history[ticker] == null)

      if (tickersToFetch.length === 0) {
        console.log('All stock histories already loaded')
        return
      }

      console.log(`Attempting to fetch history for ${tickersToFetch.length} stocks...`)

      // PHASE 1: Try all requests at once (cached requests will succeed instantly)
      const failedTickers = []
      const promises = tickersToFetch.map((ticker) => {
        return api
          .get('/stock/history/' + ticker, {
            params: {},
          })
          .then((response) => {
            console.log(`✅ Loaded history for ${ticker}`)
            this._history[ticker] = response.data
          })
          .catch((error) => {
            console.log(`⏳ ${ticker} needs rate-limited fetch ${error}`)
            failedTickers.push(ticker)
          })
      })

      await Promise.all(promises)

      // PHASE 2: If any failed (rate limited), process them in batches
      if (failedTickers.length === 0) {
        console.log('✅ All stock histories loaded from cache')
        return
      }

      console.log(`📦 Queueing ${failedTickers.length} stocks for rate-limited batch processing`)

      const BATCH_SIZE = 5
      const DELAY_MS = 60000 // 60 seconds

      for (let i = 0; i < failedTickers.length; i += BATCH_SIZE) {
        const batch = failedTickers.slice(i, i + BATCH_SIZE)

        console.log(
          `Processing batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(failedTickers.length / BATCH_SIZE)}: ${batch.join(', ')}`,
        )

        // Fetch all in current batch simultaneously
        const batchPromises = batch.map((ticker) => {
          return api
            .get('/stock/history/' + ticker, {
              params: {},
            })
            .then((response) => {
              console.log(`✅ Loaded history for ${ticker}`)
              this._history[ticker] = response.data
            })
            .catch((error) => {
              console.error(`❌ Failed to load history for ${ticker}:`, error)
            })
        })

        await Promise.all(batchPromises)

        // Wait before next batch (unless this was the last batch)
        if (i + BATCH_SIZE < failedTickers.length) {
          console.log(`⏸️  Waiting 60 seconds before next batch...`)
          await new Promise((resolve) => setTimeout(resolve, DELAY_MS))
        }
      }

      console.log('✅ All stock histories loaded')
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

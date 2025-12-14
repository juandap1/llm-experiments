<template>
  <q-layout view="lHh Lpr lFf">
    <q-header>
      <q-toolbar class="navbar">
        <div class="search-inp">
          <input type="text" placeholder="Search" />
          <span> <q-icon name="mdi-apple-keyboard-command" /> + F </span>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer class="sidebar" v-model="showSidebar" show-if-above>
      <div class="sidebar-header">
        <div class="logo">Thrive</div>
      </div>
      <div class="sidebar-content">
        <router-link to="/stocks" active-class="active">
          <div class="sidebar-item"><q-icon name="mdi-home" /> My Dashboard</div>
        </router-link>
        <router-link to="/stocks/assets" active-class="active">
          <div class="sidebar-item"><q-icon name="mdi-bank" /> My Assets</div>
        </router-link>
        <router-link to="/stocks/news" active-class="active">
          <div class="sidebar-item"><q-icon name="mdi-newspaper" /> News/Media</div>
        </router-link>
        <router-link to="/stocks/history" active-class="active">
          <div class="sidebar-item"><q-icon name="mdi-history" /> History</div>
        </router-link>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'MainLayout',

  components: {},

  setup() {
    const store = useStore()
    return {
      store,
    }
  },
  data() {
    return {
      showSidebar: true,
    }
  },
  mounted() {
    useStore().getTransactions()
  },
  computed: {
    holdings() {
      if (!this.store.currently_holding) return []
      return this.store.currently_holding
        .map((x) => {
          return {
            ticker: x,
            value: this.store.value_map?.[x] || 0,
          }
        })
        .sort((a, b) => b.value - a.value)
    },
  },
  watch: {
    'holdings.length': {
      handler() {
        this.store.batchStockHistoryRequest(this.store.uniqueTickers)
        this.store.batchStockSplitRequest(this.store.uniqueTickers)
        this.store.batchStockDividendRequest(this.store.uniqueTickers)
      },
    },
  },
})
</script>
<style lang="scss" scoped>
.search-inp {
  border: 1px solid var(--border-color);
  height: 34px;
  border-radius: 5px;
  width: 300px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  padding: 0px 10px;
  color: #777;

  input {
    flex: 1 1 auto;
    background: transparent;
    outline: none;
    border: none;
    color: white;
  }
}

.sidebar-content {
  padding: 20px 5px;

  .sidebar-item {
    padding: 10px;
    color: #ccc;
    cursor: pointer;
    transition: background-color 0.2s;
    border-radius: 5px;
    font-weight: 500;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 10px;

    &:hover {
      background-color: rgba(255, 255, 255, 0.05);
    }
  }

  .active .sidebar-item {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }
}
</style>

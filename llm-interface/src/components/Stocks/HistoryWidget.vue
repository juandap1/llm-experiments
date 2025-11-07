<template>
  <div class="basic-widget">
    <div class="widget-header">
      <h6>History</h6>
      <button class="alt-btn">
        <q-icon name="fas fa-plus" />
        Add
      </button>
    </div>
    <div class="hist-item" v-for="i in 3" :key="i">
      <div class="hist-row main">
        <div>AMZN market buy</div>
        <div>-235.97</div>
      </div>
      <div class="hist-row alt">
        <div>Sep 23, 2025</div>
        <div>1.06073 shares at $222.46</div>
      </div>
      <hr />
    </div>
    <q-dialog v-model="addModal">
      <div class="modal">
        <h6>Add Stock Purchase</h6>
        <div class="inp-wrapper">
          <q-input dark outlined dense placeholder="Stock Ticker"></q-input>
        </div>
        <div class="inp-wrapper">
          <q-input dark outlined dense placeholder="Share Count"></q-input>
        </div>
        <div class="inp-wrapper">
          <q-input dark outlined dense placeholder="Share Price"></q-input>
        </div>
        <div class="inp-wrapper">
          <q-date v-model="date" landscape dark />
        </div>
        <button class="btn full">Submit</button>
      </div>
    </q-dialog>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HistoryWidget',
  props: {},
  data() {
    return {
      addModal: true,
    }
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
  margin-bottom: 10px;
}

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

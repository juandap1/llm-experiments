<template>
  <div class="wrapper">
    <div class="bar" :style="cssProps"></div>
  </div>
</template>

<script>
import { useStore } from 'src/stores/store'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ProgressBar',
  props: {
    percent: {
      type: Number,
      default: 0,
    },
  },
  components: {},
  setup() {
    return {
      store: useStore(),
    }
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
  computed: {
    cssProps() {
      return {
        '--progress-percent': this.percent + '%',
      }
    },
  },
})
</script>
<style scoped>
.wrapper {
  width: 100%;
  height: 8px;
  background-color: #29b5f622;
}

.bar {
  width: var(--progress-percent);
  height: 100%;
  background-color: #29b6f6;
  transition: width 0.3s ease;
}
</style>

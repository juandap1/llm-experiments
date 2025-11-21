<template>
  <div class="sidebar-wrapper">
    <div class="side-header">AWS Cloud Architect Associate</div>
    <div class="sidebar-content">
      <q-scroll-area class="side-scroller">
        <div class="scroller-content">
          <slot></slot>
        </div>
      </q-scroll-area>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DefaultSidebar',
  props: {},
  components: {},
  setup() {
    return {}
  },
  data() {
    return {}
  },
  methods: {},
  mounted() {},
})
</script>
<style scoped></style>

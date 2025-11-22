<template>
  <div class="json-layout">
    <q-banner class="bg-warning text-black q-mb-md" rounded dense>
      <template v-slot:avatar>
        <q-icon name="warning" />
      </template>
      Edits made here will override the visual editor.
    </q-banner>
    <textarea
      :value="modelValue"
      class="json-editor"
      @input="$emit('update:modelValue', $event.target.value)"
    ></textarea>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'JsonEditor',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue'],
})
</script>

<style scoped>
.json-layout {
  display: flex;
  flex-direction: column;
  padding: 20px;
  width: 100%;
  height: 100%;
}

.json-editor {
  flex: 1;
  background-color: #111;
  color: #0f0;
  font-family: monospace;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  resize: none;
  outline: none;
}
</style>

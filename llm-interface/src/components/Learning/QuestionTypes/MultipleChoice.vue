<template>
  <div
    :class="'mc-opt noselect' + (selectedOpt(i) ? ' selected' : '') + (multi ? ' multi' : '')"
    v-for="(c, i) in shuffled"
    :key="c"
    @click="selectOpt(i)"
  >
    <div class="mc-left-sect">
      <q-icon v-if="!multi" class="not-selected" name="far fa-circle" />
      <q-icon v-else class="not-selected" name="far fa-square" />
      <div class="selected-marker">
        <q-icon name="fas fa-check" />
      </div>
    </div>
    <div class="mc-label">
      {{ c.label }}
    </div>
  </div>
</template>
<script>
import { useUtilityStore } from 'src/stores/utility'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'multiple-choice',
  emits: ['update:modelValue'],
  props: {
    choices: {
      type: Array,
      default() {
        return []
      },
    },
    modelValue: [String, Number, Object, Array],
    multi: Boolean,
  },
  setup() {
    return {}
  },
  data() {
    return {
      selected: -1,
      multiSelected: [],
      value: null,
      shuffled: [],
    }
  },
  methods: {
    selectOpt(i) {
      if (this.selectedOpt(i)) {
        if (this.multi) {
          this.multiSelected.splice(this.multiSelected.indexOf(i), 1)
        } else {
          this.selected = -1
          this.value = null
        }
      } else {
        if (this.multi) {
          this.multiSelected.push(i)
          if (this.value == null) this.value = []
          if ('value' in this.shuffled[i]) {
            let sel = this.shuffled[i].value
            sel.id = this.shuffled[i].id
            this.value.push(sel)
          } else {
            this.value.push({ id: this.shuffled[i].id })
          }
        } else {
          this.selected = i
          if ('value' in this.shuffled[i]) {
            this.value = this.shuffled[i].value
            this.value.id = this.shuffled[i].id
          } else {
            this.value = {
              id: this.shuffled[i].id,
            }
          }
        }
      }
    },
    selectedOpt(ind) {
      return this.multi ? this.multiSelected.includes(ind) : this.selected == ind
    },
    loadSaved(val) {
      if (val == null || val == undefined) return
      if (this.multi) {
        this.multiSelected = val.map((v) => {
          return this.shuffled.findIndex((x) => x.id == v.id)
        })
      } else {
        this.selected = this.shuffled.findIndex((x) => x.id == val.id)
      }
    },
    isArray(a) {
      return !!a && a.constructor === Array
    },
  },
  mounted() {
    if (this.choices.length > 0) {
      this.shuffled = useUtilityStore().shuffle(this.choices)
    }
    this.value = this.modelValue
    this.loadSaved(this.value)
    //gte
  },
  components: {},
  watch: {
    value: function (newVal) {
      this.$emit('update:modelValue', newVal)
    },
    choices: function (newVal) {
      //console.log(newVal);
      if (newVal.length > 0) {
        this.shuffled = useUtilityStore().shuffle(newVal)
      }
    },
  },
})
</script>
<style scoped>
.mc-opt {
  padding: 7.5px 10px;
  border-radius: 7.5px;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #ccc;
  margin: 5px 0px;
  background-color: rgb(255, 255, 255, 0.03);
}

.mc-opt:not(.selected):hover {
  background-color: rgb(255, 255, 255, 0.1);
}

.mc-opt.selected {
  background-color: rgb(122, 122, 255);
  color: white;
}

.mc-opt:hover .mc-left-sect .selected-marker,
.mc-opt.selected .mc-left-sect .selected-marker {
  display: flex;
}

.mc-opt:hover .mc-left-sect .not-selected,
.mc-opt.selected .mc-left-sect .not-selected {
  display: none;
}

.mc-left-sect {
  width: 30px;
  height: 30px;
  margin-right: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.mc-label {
  font-size: 15px;
}

.selected-marker {
  width: 25px;
  height: 25px;
  background-color: rgb(0, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  display: none;
}

.multi .selected-marker {
  border-radius: 5px;
}
</style>

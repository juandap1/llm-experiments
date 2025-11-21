<template>
  <div v-if="question">
    <div class="basic-instruct">
      {{ instructTxt(question.type, question.multi) }}
    </div>
    <div class="question">{{ question.question }}</div>
    <div class="details" v-if="question.details" v-html="question.details"></div>
    <div class="main-sect" :key="question.id">
      <multiple-choice v-if="question.type == 'mc'" :choices="question.choices" />
      <!-- <free-response v-else-if="question.type == 'frq'" v-model="store.responses[question.id]" />
      <code-response v-else-if="type == 'code'" v-model="store.responses[question.id]" /> -->
    </div>
    <div class="test-footer">
      <q-btn class="back-btn" no-caps @click="back" outline style="color: #a4a4ff">
        <q-icon name="fas fa-chevron-left" size="18px" />
        Back
      </q-btn>
      <div style="flex: 1 1 auto"></div>
      <q-btn class="next-btn" no-caps @click="next">
        Next
        <q-icon name="fas fa-chevron-right" size="18px" />
      </q-btn>
    </div>
  </div>
</template>
<script>
import { defineComponent } from 'vue'
import MultipleChoice from './QuestionTypes/MultipleChoice.vue'
import { useExamStore } from 'src/stores/examination'
// import { api } from 'src/boot/axios'
// import { useUserStore } from 'src/stores/user'
// import FreeResponse from './QuestionTypes/FreeResponse.vue'
// import CodeResponse from './QuestionTypes/CodeResponse.vue'

export default defineComponent({
  name: 'mbti-modal',
  setup() {
    const store = useExamStore()
    // const question = computed(() => store.questions[store.index])
    return {
      store,
      question: {
        id: 'e3ca23ac-83e5-4044-92cb-8b1106843009',
        question: 'Which word in the pair appeals to you more?',
        choices: [
          {
            label: 'Casual',
            value: {
              quality: 'P',
              weight: 2,
            },
            id: 'cd42f5cc-97db-45e5-824b-a5b289006427',
          },
          {
            label: 'Systematic',
            value: {
              quality: 'J',
              weight: 2,
            },
            id: '54046405-914e-4446-9818-d8a8f59b6831',
          },
        ],
        type: 'mc',
      },
    }
  },
  data() {
    return {}
  },
  methods: {
    instructTxt(type, multi = false) {
      if (type == 'mc' && multi) {
        return '(Select All That Apply)'
      } else if (type == 'mc' && !multi) {
        return '(Select an Answer)'
      }
    },
    next() {
      if (useExamStore().questions.length > useExamStore().index + 1) {
        useExamStore().index++
        if (useExamStore().index > useExamStore().maxInd)
          useExamStore().maxInd = useExamStore().index
        /*this.$router.push(
          `/exam/${useExamStore()._id}/${useExamStore().index}`
        );*/
      } else {
        this.submit()
      }
    },
    processResponses(res) {
      let clone = structuredClone(res)
      let processed = {}
      for (let i in clone) {
        processed[i] = clone[i].id
      }
      return processed
    },
    submit() {},
    validResponse(res) {
      var regex = /(<([^>]+)>)/gi
      if (typeof res == 'string') return res.replace(regex, '').trim().length != 0
      return res != undefined && res != null
    },
  },
  mounted() {},
  components: { MultipleChoice },
  watch: {
    $route(to) {
      if (to.params.ind != useExamStore().index) {
        if (useExamStore().backtrack) {
          useExamStore().index = parseInt(to.params.ind)
        }
      }
    },
  },
})
</script>
<style scoped>
.basic-instruct {
  color: #bdbdbd;
}

.question {
  font-weight: bold;
  font-size: 20px;
  padding: 10px 0px;
  line-height: 1.2;
}

.details {
  font-size: 16px;
}

.main-sect {
  flex: 1 1 auto;
  padding: 15px 0px;
}

.test-footer {
  display: flex;
}

.next-btn {
  background-color: #a4a4ff;
  font-size: 16px;
  border-radius: 7.5px;
  line-height: 1;
  color: white;
  cursor: pointer;
}

.next-btn:hover,
.back-btn:hover {
  scale: 1.02;
}

.back-btn {
  font-size: 16px;
  border-radius: 7.5px;
  line-height: 1;
  cursor: pointer;
}
</style>

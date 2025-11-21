<template>
  <div class="layout-container">
    <default-navbar />
    <div class="layout-main">
      <default-sidebar></default-sidebar>
      <div class="content-container flexed">
        <div class="chat-view">
          <q-scroll-area class="chat-scroller" dark>
            <div class="chat-inner">
              <div class="chat-entry-row">
                <div class="chat-entry">Hi</div>
              </div>
              <div class="chat-entry-row left">
                <div class="">
                  The drink in your photo is Sangaria Melon Soda (サンガリア メロンソーダ) — a
                  popular Japanese soft drink. No, it does not contain caffeine. 🍈 It's a
                  carbonated melon-flavored soda made mostly from water, sugar, carbon dioxide, and
                  flavoring. Sangaria’s melon sodas are non-caffeinated, similar to drinks like
                  Sprite or Fanta. Would you like me to tell you what ingredients or nutrition info
                  it usually has (in English)?
                </div>
              </div>
            </div>
          </q-scroll-area>
        </div>
        <div class="chat-footer">
          <div class="chat-inp-wrapper">
            <input class="chat-inp" type="text" placeholder="Ask Anything" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
// import HomeNavbar from 'src/components/TabsNavbar.vue'
import DefaultNavbar from 'src/components/DefaultNavbar.vue'
import DefaultSidebar from 'src/components/DefaultSidebar.vue'

export default defineComponent({
  name: 'ChatPage',
  components: { DefaultNavbar, DefaultSidebar },
  data() {
    return {}
  },
})
</script>
<style scoped>
.content-container.flexed {
  display: flex;
  flex-flow: column;
}

.chat-view {
  flex: 1 1 auto;
}

.chat-scroller {
  height: 100%;
}

.chat-inner {
  padding: 20px 0px;
  width: 80%;
  margin: auto;
}

.chat-entry-row {
  display: flex;
  justify-content: end;
  font-size: 16px;
  font-weight: 500;
  padding: 10px 0px;
}

.chat-entry-row.left {
  justify-content: start;
}

.chat-entry {
  border-radius: 500px;
  padding: 5px 15px;
  background-color: #333;
}

.chat-footer {
  position: relative;
  height: 56px;
}

.chat-inp-wrapper {
  border-radius: 500px;
  background-color: #333;
  height: 56px;
  width: 80%;
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
}

.chat-inp {
  height: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: #ccc;
  padding: 0px 24px;
  font-size: 20px;
  width: 100%;
}
</style>

<template>
  <q-page class="flex flex-center overflow-hidden bg-black">
    <canvas ref="canvasRef" class="absolute-full"></canvas>

    <div
      class="relative-position z-top text-center q-pa-xl rounded-borders"
      :style="{ backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }"
    >
      <h2 class="text-white q-mb-md text-weight-bold" style="letter-spacing: 2px">SYSTEM UPDATE</h2>

      <transition name="fade" mode="out-in">
        <div v-if="!loading" key="start">
          <q-btn
            color="white"
            text-color="black"
            size="lg"
            rounded
            label="INITIATE SEQUENCE"
            class="text-weight-bold q-px-xl q-py-xs"
            @click="startWarp"
          />
        </div>

        <div v-else key="loading" class="text-white">
          <div class="text-h5 q-mb-sm text-cyan-3">PROCESSING DATA</div>
          <div class="text-subtitle1 text-grey-4">Optimizing neural pathways...</div>
          <q-btn flat dense round icon="close" color="grey-5" class="q-mt-md" @click="stopWarp" />
        </div>
      </transition>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
const loading = ref(false)

// Animation state
let animationFrameId = null
let stars = []
const STAR_COUNT = 1000 // Number of stars
const SPEED_IDLE = 0.2
const SPEED_WARP = 30
let speed = SPEED_IDLE
let targetSpeed = SPEED_IDLE

// Canvas dimensions
let width = 0
let height = 0
let cx = 0
let cy = 0

class Star {
  constructor() {
    this.reset(true)
  }

  reset(randomZ = false) {
    this.x = (Math.random() - 0.5) * width * 2 // Spread wider than screen
    this.y = (Math.random() - 0.5) * height * 2
    this.z = randomZ ? Math.random() * width : width // Start far away
    this.pz = this.z // Previous z for trail effect
  }

  update() {
    this.pz = this.z
    this.z -= speed

    // Reset if it passes the camera or goes off screen
    if (this.z < 1) {
      this.reset()
      this.z = width
      this.pz = this.z
    }
  }

  draw(ctx) {
    // Project 3D position to 2D
    const sx = (this.x / this.z) * width + cx
    const sy = (this.y / this.z) * height + cy

    const px = (this.x / this.pz) * width + cx
    const py = (this.y / this.pz) * height + cy

    // Don't draw if outside canvas
    if (sx < 0 || sx > width || sy < 0 || sy > height) return

    // Calculate distance from center for opacity (keep center clear)
    const dx = sx - cx
    const dy = sy - cy
    const dist = Math.sqrt(dx * dx + dy * dy)
    const centerSafeZone = 150 // Radius of safe zone

    let alpha = 1
    if (dist < centerSafeZone) {
      alpha = Math.max(0, (dist - 50) / (centerSafeZone - 50))
    }

    // Also fade based on Z (closer = brighter)
    const depthAlpha = 1 - this.z / width
    alpha *= depthAlpha

    if (alpha <= 0.01) return

    // Draw the star/streak
    ctx.beginPath()
    ctx.moveTo(px, py)
    ctx.lineTo(sx, sy)

    // Monocolor effect (Cyan/White)
    ctx.strokeStyle = `rgba(100, 255, 255, ${alpha})`
    ctx.lineWidth = speed > 2 ? 2 : 1.5
    ctx.stroke()
  }
}

const initStars = () => {
  stars = []
  for (let i = 0; i < STAR_COUNT; i++) {
    stars.push(new Star())
  }
}

const resize = () => {
  if (!canvasRef.value) return
  width = window.innerWidth
  height = window.innerHeight
  canvasRef.value.width = width
  canvasRef.value.height = height
  cx = width / 2
  cy = height / 2
  // Re-init stars to cover new area if needed, or just let them flow
}

const animate = () => {
  if (!canvasRef.value) return
  const ctx = canvasRef.value.getContext('2d')

  // Clear with fade effect for trails? Or just clear.
  // Standard clear for crisp lines
  ctx.fillStyle = 'black'
  ctx.fillRect(0, 0, width, height)

  // Ease speed
  speed += (targetSpeed - speed) * 0.05

  stars.forEach((star) => {
    star.update()
    star.draw(ctx)
  })

  animationFrameId = requestAnimationFrame(animate)
}

const startWarp = () => {
  loading.value = true
  targetSpeed = SPEED_WARP
}

const stopWarp = () => {
  loading.value = false
  targetSpeed = SPEED_IDLE
}

onMounted(() => {
  window.addEventListener('resize', resize)
  resize()
  initStars()
  animate()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  cancelAnimationFrame(animationFrameId)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.z-top {
  z-index: 10;
}
</style>

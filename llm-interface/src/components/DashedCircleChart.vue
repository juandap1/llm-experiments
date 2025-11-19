<template>
  <div class="knob-container">
    <svg :width="size" :height="size" viewBox="0 0 100 100">
      <!-- Draw center circle -->
      <!-- <circle :cx="size * 0.5" :cy="size * 0.5" :r="size * 0.4" stroke="none" fill="none" /> -->

      <!-- Draw rectangles circling the center -->
      <g v-for="(item, index) in totalRects" :key="index">
        <rect
          :x="45"
          :y="0"
          width="1"
          height="6"
          rx="1"
          ry="1"
          :fill="index < filled ? color : '#888'"
          :transform="`rotate(${(360 / totalRects) * index + 90}, 50, 50)`"
        />
      </g>
    </svg>
    <div class="val-vis">100k</div>
  </div>
</template>

<script>
export default {
  props: {
    size: {
      type: Number,
      default: 220,
    },
    totalRects: {
      type: Number,
      default: 90, // Number of rectangles around the knob
    },
    color: {
      type: String,
      default: '#ff964f',
    },
    filled: {
      type: Number,
      default: 50,
    },
  },
}
</script>

<style scoped>
.knob-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

svg {
  transform: rotate(-90deg); /* To start from the top */
}

rect {
  transition: all 0.3s ease;
}

.val-vis {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 50px;
  font-weight: bold;
}
</style>

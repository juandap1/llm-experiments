<template>
  <div class="dependency-editor">
    <div class="toolbar">
      <div class="left-tools">
        <q-btn-group outline>
          <q-btn
            :color="mode === 'view' ? 'secondary' : 'grey-8'"
            icon="open_with"
            label="Move"
            @click="mode = 'view'"
            size="sm"
          />
          <q-btn
            :color="mode === 'connect' ? 'secondary' : 'grey-8'"
            icon="link"
            label="Connect"
            @click="mode = 'connect'"
            size="sm"
          />
        </q-btn-group>
        <div class="mode-hint" v-if="mode === 'connect'">
          {{ connectionSource ? 'Select target node to connect' : 'Select source node' }}
        </div>
      </div>
      <div class="right-tools">
        <q-btn flat round icon="refresh" size="sm" @click="runLayout" color="white">
          <q-tooltip>Reset Layout</q-tooltip>
        </q-btn>
      </div>
    </div>

    <div class="graph-wrapper">
      <v-network-graph
        v-if="nodesObject && Object.keys(nodesObject).length > 0"
        class="graph"
        :nodes="nodesObject"
        :edges="edgesObject"
        :layouts="layouts"
        :configs="configs"
        :event-handlers="eventHandlers"
      >
        <!-- Custom Node Layer -->
        <template #override-node="{ nodeId, config, ...slotProps }">
          <circle
            :r="config.radius * 1.5"
            :fill="config.color"
            :stroke="
              connectionSource === nodeId ? '#fff' : mode === 'connect' ? '#ffffff44' : 'none'
            "
            :stroke-width="connectionSource === nodeId ? 4 : 2"
            v-bind="slotProps"
          />
          <!-- Label -->
          <text
            :x="0"
            :y="config.radius * 1.5 + 15"
            font-size="10"
            text-anchor="middle"
            fill="#ffffff"
            style="pointer-events: none; user-select: none"
          >
            {{ nodesObject[nodeId].name }}
          </text>
        </template>
      </v-network-graph>
      <div v-else class="empty-state">No skills found. Add skills in the Content tab first.</div>

      <!-- Legend -->
      <div class="legend" v-if="Object.keys(unitColorMap).length > 0">
        <div class="legend-title">Units</div>
        <div class="legend-item" v-for="(color, unitName) in unitColorMap" :key="unitName">
          <span class="color-dot" :style="{ backgroundColor: color }"></span>
          <span class="label-text">{{ unitName }}</span>
        </div>
      </div>

      <!-- Edge Preview Card -->
      <transition name="fade">
        <div v-if="selectedEdgeId" class="edge-preview">
          <div class="preview-header">
            <span class="preview-title">Dependency Details</span>
            <q-btn flat round icon="close" size="xs" @click="selectedEdgeId = null" />
          </div>
          <div class="preview-body">
            <div class="preview-row">
              <span class="label">Source (Prerequisite)</span>
              <span class="value source-value">{{ edgesObject[selectedEdgeId].source }}</span>
            </div>
            <div class="preview-row">
              <span class="label">Target (Dependent)</span>
              <span class="value target-value">{{ edgesObject[selectedEdgeId].target }}</span>
            </div>
            <div class="preview-row">
              <span class="label">Reason</span>
              <q-input
                v-model="editingReason"
                filled
                dark
                dense
                autogrow
                type="textarea"
                rows="3"
                class="reason-input"
                @update:model-value="saveEdge"
                debounce="500"
              />
            </div>
            <div class="actions-row">
              <q-btn
                outline
                color="negative"
                label="Remove Dependency"
                size="sm"
                class="full-width"
                icon="delete"
                @click="deleteSelectedEdge"
              />
            </div>
          </div>
        </div>
      </transition>

      <!-- Node Preview Card -->
      <transition name="fade">
        <div v-if="selectedNodeId" class="edge-preview">
          <div class="preview-header">
            <span class="preview-title">Skill Details</span>
            <q-btn flat round icon="close" size="xs" @click="selectedNodeId = null" />
          </div>
          <div class="preview-body">
            <div class="preview-row">
              <span class="label">Name</span>
              <span class="value" :style="{ color: nodesObject[selectedNodeId].color }">
                {{ nodesObject[selectedNodeId].name }}
              </span>
            </div>
            <div class="preview-row">
              <span class="label">Unit</span>
              <span class="value">{{ nodesObject[selectedNodeId].unit }}</span>
            </div>
            <div class="preview-row">
              <span class="label">Concept</span>
              <span class="value">{{ nodesObject[selectedNodeId].concept }}</span>
            </div>
            <div class="preview-row">
              <span class="label">Rule</span>
              <span class="value">{{ nodesObject[selectedNodeId].rule }}</span>
            </div>
            <div class="preview-row" v-if="nodesObject[selectedNodeId].description">
              <span class="label">Description</span>
              <span class="value">{{ nodesObject[selectedNodeId].description }}</span>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, watch, onMounted } from 'vue'
import { VNetworkGraph, GridLayout } from 'v-network-graph'
import * as d3 from 'd3'
import 'v-network-graph/lib/style.css'

export default defineComponent({
  name: 'DependencyEditor',
  components: {
    VNetworkGraph,
  },
  props: {
    dependencies: {
      type: Array,
      required: true,
    },
    skills: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['add-dependency', 'remove-dependency', 'update-dependency'],
  setup(props, { emit }) {
    const mode = ref('view') // 'view' or 'connect'
    const connectionSource = ref(null)
    const layouts = ref({ nodes: {} })
    const selectedEdgeId = ref(null)
    const selectedNodeId = ref(null)
    const editingReason = ref('')

    // Colors for different units to visually distinguish them
    const unitColors = [
      '#ff7f50', // Coral
      '#87cefa', // Sky Blue
      '#90ee90', // Light Green
      '#dda0dd', // Plum
      '#f0e68c', // Khaki
      '#ff69b4', // Hot Pink
      '#40e0d0', // Turquoise
    ]

    const unitColorMap = computed(() => {
      const map = {}
      const unitMap = new Map()
      let unitColorIndex = 0

      props.skills.forEach((skill) => {
        if (!unitMap.has(skill.unit)) {
          const color = unitColors[unitColorIndex % unitColors.length]
          unitMap.set(skill.unit, color)
          map[skill.unit] = color
          unitColorIndex++
        }
      })
      return map
    })

    const nodesObject = computed(() => {
      const obj = {}
      // Reuse the computed map logic implicitly or explicitly
      // Ideally we use unitColorMap but that's a computed ref.
      // We can access it via unitColorMap.value

      props.skills.forEach((skill) => {
        const color = unitColorMap.value[skill.unit] || '#888'
        obj[skill.name] = {
          id: skill.name,
          name: skill.name,
          color: color,
          radius: 10,
          ...skill,
        }
      })
      return obj
    })

    const edgesObject = computed(() => {
      const obj = {}
      props.dependencies.forEach((dep, index) => {
        // Create a unique ID for the edge based on source-target
        const id = `edge-${index}`
        obj[id] = {
          source: dep.source,
          target: dep.target,
          reason: dep.reason,
          originalIndex: index,
        }
      })
      return obj
    })

    const configs = ref({
      view: {
        autoPanAndZoomOnLoad: 'fit-content',
        layoutHandler: new GridLayout({ grid: 15 }),
      },
      node: {
        selectable: true,
        normal: {
          radius: 10,
          color: (n) => n.color,
        },
        hover: {
          radius: 12,
        },
        label: {
          visible: false, // We use custom label in template
        },
      },
      edge: {
        selectable: true,
        normal: {
          width: 2,
          color: '#666',
        },
        hover: {
          width: 3,
          color: '#fff',
        },
        marker: {
          target: {
            type: 'arrow',
            width: 4,
            height: 4,
          },
        },
      },
    })

    const eventHandlers = {
      'node:click': ({ node }) => {
        if (mode.value === 'connect') {
          if (!connectionSource.value) {
            connectionSource.value = node
          } else {
            if (connectionSource.value !== node) {
              // Create dependency
              createDependency(connectionSource.value, node)
              connectionSource.value = null
            } else {
              // Deselect if clicking same node
              connectionSource.value = null
            }
          }
        } else {
          // View mode: Show node details
          selectedNodeId.value = node
          selectedEdgeId.value = null
        }
      },
      'edge:click': ({ edge }) => {
        if (mode.value === 'view') {
          selectedEdgeId.value = edge
          selectedNodeId.value = null
          editingReason.value = edgesObject.value[edge].reason || ''
        }
      },
      'view:click': () => {
        if (mode.value === 'connect') {
          connectionSource.value = null
        } else {
          selectedEdgeId.value = null
          selectedNodeId.value = null
        }
      },
    }

    function createDependency(source, target) {
      // Check if already exists
      const exists = props.dependencies.some((d) => d.source === source && d.target === target)
      if (exists) {
        return
      }
      emit('add-dependency', { source, target, reason: '' })
    }

    function deleteSelectedEdge() {
      if (selectedEdgeId.value) {
        const index = edgesObject.value[selectedEdgeId.value].originalIndex
        emit('remove-dependency', index)
        selectedEdgeId.value = null
      }
    }

    function saveEdge() {
      if (selectedEdgeId.value) {
        const index = edgesObject.value[selectedEdgeId.value].originalIndex
        emit('update-dependency', { index, reason: editingReason.value })
      }
    }

    function runLayout() {
      if (Object.keys(nodesObject.value).length === 0) return

      const simulationNodes = Object.values(nodesObject.value).map((n) => ({
        id: n.id,
        ...n,
        x: Math.random() * 500,
        y: Math.random() * 500,
      }))

      const simulationEdges = props.dependencies
        .map((d) => ({
          source: d.source,
          target: d.target,
        }))
        .filter((e) => nodesObject.value[e.source] && nodesObject.value[e.target])

      const simulation = d3
        .forceSimulation(simulationNodes)
        .force(
          'link',
          d3
            .forceLink(simulationEdges)
            .id((d) => d.id)
            .distance(150),
        )
        .force('charge', d3.forceManyBody().strength(-500))
        .force('center', d3.forceCenter(0, 0))
        .force('collide', d3.forceCollide(30))
        .stop()

      // Run simulation for some ticks
      for (let i = 0; i < 300; ++i) simulation.tick()

      const newLayouts = {}
      simulationNodes.forEach((n) => {
        newLayouts[n.id] = { x: n.x, y: n.y }
      })
      layouts.value.nodes = newLayouts
    }

    // Run layout on mount and when skills change
    watch(
      () => props.skills,
      () => {
        runLayout()
      },
      { deep: true },
    )

    onMounted(() => {
      setTimeout(runLayout, 100)
    })

    return {
      mode,
      connectionSource,
      layouts,
      configs,
      nodesObject,
      edgesObject,
      eventHandlers,
      selectedEdgeId,
      selectedNodeId,
      editingReason,
      unitColorMap,
      runLayout,
      deleteSelectedEdge,
      saveEdge,
    }
  },
})
</script>

<style scoped>
.dependency-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #1e1e1e;
  position: relative;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #252525;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.left-tools {
  display: flex;
  align-items: center;
  gap: 15px;
}

.mode-hint {
  font-size: 0.9em;
  color: var(--secondary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

.graph-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.graph {
  width: 100%;
  height: 100%;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #666;
  font-size: 1.2em;
}

/* Legend Styles */
.legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background-color: rgba(30, 30, 30, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.legend-title {
  font-size: 0.9em;
  font-weight: bold;
  color: #aaa;
  margin-bottom: 4px;
  text-transform: uppercase;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.label-text {
  font-size: 0.9em;
  color: #eee;
}

/* Edge/Node Preview Card Styles */
.edge-preview {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  background-color: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  z-index: 20;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 8px;
}

.preview-title {
  font-size: 1.1em;
  font-weight: bold;
  color: #fff;
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-row .label {
  font-size: 0.8em;
  color: #888;
  text-transform: uppercase;
  font-weight: 500;
}

.preview-row .value {
  font-size: 0.95em;
  color: #ddd;
  word-break: break-word;
  font-weight: 500;
}

.source-value {
  color: #ff7f50; /* Matches typical source color or custom */
}

.target-value {
  color: #87cefa; /* Matches typical target color or custom */
}

.reason-input {
  font-size: 0.9em;
}

.actions-row {
  margin-top: 10px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

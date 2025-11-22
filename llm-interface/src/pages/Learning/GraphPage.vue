<template>
  <div class="graph-page">
    <div v-if="loading" class="loading-container">
      <q-spinner size="50px" color="secondary" />
    </div>

    <div v-else class="graph-container">
      <v-network-graph
        v-if="nodes.length > 0"
        class="graph"
        :nodes="nodesObject"
        :edges="edgesObject"
        :layouts="layouts"
        :configs="configs"
        :event-handlers="eventHandlers"
      >
        <template #edge-label="{ edge, ...slotProps }">
          <v-edge-label
            :text="edge.type"
            align="center"
            vertical-align="above"
            v-bind="slotProps"
          />
        </template>
      </v-network-graph>
      <div v-else class="empty-state">No graph data found.</div>

      <!-- Legend -->
      <div class="legend">
        <div class="legend-item" v-for="(color, label) in nodeColors" :key="label">
          <span class="color-dot" :style="{ backgroundColor: color }"></span>
          <span class="label-text">{{ label }}</span>
        </div>
      </div>

      <!-- Node Preview Card -->
      <transition name="fade">
        <div v-if="selectedNode" class="node-preview">
          <div class="preview-header">
            <span class="preview-title">{{ selectedNode.name }}</span>
            <q-btn flat round icon="close" size="xs" @click="selectedNode = null" />
          </div>
          <div class="preview-body">
            <div class="preview-row">
              <span class="label">Type:</span>
              <span class="value" :style="{ color: selectedNode.color }">{{
                selectedNode.labels ? selectedNode.labels[0] : 'Unknown'
              }}</span>
            </div>
            <div v-for="(value, key) in selectedNode" :key="key">
              <div
                v-if="!['name', 'color', 'radius', 'labels', 'id', 'x', 'y'].includes(key)"
                class="preview-row"
              >
                <span class="label">{{ key }}:</span>
                <span class="value">{{ value }}</span>
              </div>
            </div>

            <!-- Relationships Section -->
            <div v-if="selectedNodeRelationships.length > 0" class="relationships-section">
              <div class="section-title">Relationships</div>
              <q-scroll-area class="relationship-list" dark>
                <div
                  v-for="(rel, index) in selectedNodeRelationships"
                  :key="index"
                  class="relationship-item"
                >
                  <span class="rel-direction" :class="rel.direction.toLowerCase()">{{
                    rel.direction === 'Outgoing' ? '→' : '←'
                  }}</span>
                  <span class="rel-type">{{ rel.type }}</span>
                  <span class="rel-target" :style="{ color: rel.otherNodeColor }">{{
                    rel.otherNodeName
                  }}</span>
                </div>
              </q-scroll-area>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import { llmService } from 'src/services/llm'
import { VNetworkGraph, VEdgeLabel } from 'v-network-graph'
import * as d3 from 'd3'
import 'v-network-graph/lib/style.css'

export default defineComponent({
  name: 'GraphPage',
  components: {
    VNetworkGraph,
    VEdgeLabel,
  },
  setup() {
    const loading = ref(true)
    const nodes = ref([])
    const edges = ref([])
    const layouts = ref({ nodes: {} })
    const selectedNode = ref(null)

    const nodeColors = {
      Unit: '#ff7f50', // Coral
      Concept: '#87cefa', // Light Sky Blue
      Rule: '#90ee90', // Light Green
      Skill: '#dda0dd', // Plum
      Course: '#aaaaaa',
    }

    const nodeSizes = {
      Course: 40,
      Unit: 30,
      Concept: 20,
      Rule: 15,
      Skill: 10,
      Unknown: 10,
    }

    const nodesObject = computed(() => {
      const obj = {}
      nodes.value.forEach((n) => {
        const label = n.labels && n.labels.length > 0 ? n.labels[0] : 'Unknown'
        obj[n.id] = {
          id: n.id,
          name: n.properties.name || n.id,
          color: nodeColors[label] || nodeColors.Course,
          radius: nodeSizes[label] || nodeSizes.Unknown,
          labels: n.labels,
          ...n.properties,
        }
      })
      return obj
    })

    const edgesObject = computed(() => {
      const obj = {}
      edges.value.forEach((e) => {
        obj[e.id] = {
          source: e.source,
          target: e.target,
          type: e.type,
        }
      })
      return obj
    })

    const eventHandlers = {
      'node:click': ({ node }) => {
        selectedNode.value = nodesObject.value[node]
      },
      'view:click': () => {
        selectedNode.value = null
      },
    }

    const configs = ref({
      view: {
        autoPanAndZoomOnLoad: 'fit-content',
      },
      node: {
        normal: {
          type: 'circle',
          radius: (node) => node.radius,
          color: (node) => node.color,
        },
        hover: {
          radius: (node) => node.radius + 2,
          strokeWidth: 2,
          strokeColor: '#ffffff',
        },
        label: {
          visible: true,
          color: '#ffffff',
          fontSize: 12,
        },
      },
      edge: {
        normal: {
          width: 2,
          color: '#666666',
        },
        marker: {
          target: {
            type: 'arrow',
            width: 4,
            height: 4,
          },
        },
        label: {
          color: '#ffffff',
          fontSize: 10,
          background: {
            visible: true,
            color: '#161616',
            padding: {
              vertical: 1,
              horizontal: 4,
            },
            borderRadius: 2,
          },
        },
      },
    })

    async function loadGraph() {
      try {
        loading.value = true
        const data = await llmService.getGraphData()
        nodes.value = data.nodes || []
        edges.value = data.edges || []

        // Initialize layouts with random positions
        const initialLayouts = {}
        nodes.value.forEach((n) => {
          initialLayouts[n.id] = {
            x: (Math.random() - 0.5) * 1000,
            y: (Math.random() - 0.5) * 1000,
          }
        })
        layouts.value.nodes = initialLayouts

        // Run d3 simulation
        if (nodes.value.length > 0) {
          // Map nodes to include radius for collision detection
          const simulationNodes = nodes.value.map((n) => {
            const label = n.labels && n.labels.length > 0 ? n.labels[0] : 'Unknown'
            return {
              id: n.id,
              radius: nodeSizes[label] || nodeSizes.Unknown,
              ...initialLayouts[n.id],
            }
          })
          const simulationEdges = edges.value.map((e) => ({
            source: e.source,
            target: e.target,
          }))

          d3.forceSimulation(simulationNodes)
            .force(
              'link',
              d3
                .forceLink(simulationEdges)
                .id((d) => d.id)
                .distance(200),
            ) // Increased distance
            .force('charge', d3.forceManyBody().strength(-3000)) // Increased repulsion
            .force('center', d3.forceCenter(0, 0))
            .force(
              'collide',
              d3.forceCollide((d) => d.radius + 10),
            ) // Dynamic collision radius with padding
            .on('tick', () => {
              const newLayouts = {}
              simulationNodes.forEach((n) => {
                newLayouts[n.id] = { x: n.x, y: n.y }
              })
              layouts.value.nodes = newLayouts
            })
        }
      } catch (error) {
        console.error('Error loading graph:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadGraph()
    })

    const selectedNodeRelationships = computed(() => {
      if (!selectedNode.value) return []
      const nodeId = selectedNode.value.id
      return edges.value
        .filter((e) => e.source === nodeId || e.target === nodeId)
        .map((e) => {
          const isSource = e.source === nodeId
          const otherNodeId = isSource ? e.target : e.source
          const otherNode = nodesObject.value[otherNodeId]
          return {
            type: e.type,
            direction: isSource ? 'Outgoing' : 'Incoming',
            otherNodeName: otherNode ? otherNode.name : otherNodeId,
            otherNodeColor: otherNode ? otherNode.color : '#888',
          }
        })
    })

    return {
      loading,
      nodes,
      edges,
      nodesObject,
      edgesObject,
      configs,
      layouts,
      loadGraph,
      nodeColors,
      selectedNode,
      selectedNodeRelationships,
      eventHandlers,
    }
  },
})
</script>

<style scoped>
.graph-page {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  padding: 20px;
  background-color: #161616;
  color: #eee;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.graph-container {
  flex: 1;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  background-color: #1e1e1e;
  position: relative; /* For legend and preview positioning */
}

.graph {
  width: 100%;
  height: 100%;
}

.loading-container,
.empty-state {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.2em;
  color: #888;
}

.legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background-color: rgba(30, 30, 30, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
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

.node-preview {
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
  margin-bottom: 10px;
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
  gap: 8px;
}

.preview-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.preview-row .label {
  font-size: 0.8em;
  color: #888;
  text-transform: uppercase;
}

.preview-row .value {
  font-size: 0.95em;
  color: #ddd;
  word-break: break-word;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.relationships-section {
  margin-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 10px;
}

.section-title {
  font-size: 0.9em;
  font-weight: bold;
  color: #aaa;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.relationship-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 150px;
}

.relationship-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
}

.rel-direction {
  font-weight: bold;
  color: #888;
}

.rel-direction.outgoing {
  color: #ff7f50;
}

.rel-direction.incoming {
  color: #87cefa;
}

.rel-type {
  color: #bbb;
  font-style: italic;
  font-size: 0.85em;
}

.rel-target {
  color: #eee;
  font-weight: 500;
}
</style>

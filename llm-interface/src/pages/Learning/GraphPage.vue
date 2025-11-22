<template>
  <div class="graph-page">
    <div class="header-row">
      <div class="text-h4">Curriculum Graph</div>
      <q-btn flat icon="refresh" @click="loadGraph" :loading="loading" color="white" />
    </div>

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
        // Handle the case where 'Unknown' might be used if label is not found in nodeColors
        // But here we want to map label to color/size directly
        obj[n.id] = {
          name: n.properties.name || n.id,
          color: nodeColors[label] || nodeColors.Course, // Default to Course color if unknown
          radius: nodeSizes[label] || nodeSizes.Unknown,
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
          const simulationEdges = edges.value.map((e) => ({ source: e.source, target: e.target }))

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
  position: relative; /* For legend positioning */
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
</style>

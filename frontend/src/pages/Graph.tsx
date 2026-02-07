import { useEffect, useRef, useCallback, useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ForceGraph2D from 'react-force-graph-2d'
import { Network, RefreshCw, ZoomIn, ZoomOut, Info, Maximize2, X, Eye, EyeOff } from 'lucide-react'
import { graphApi, GraphNode, GraphEdge } from '@/lib/api'
import { PageTitle, Card, Button, Spinner, Badge, EmptyState } from '@/components/ui'
import { useTheme } from '@/hooks'

// Extended node type for force graph
interface GraphNodeExt {
  id: string
  type: string
  label: string
  description?: string
  size?: number
  color?: string
  x?: number
  y?: number
  vx?: number
  vy?: number
}

interface GraphLinkExt {
  source: string | GraphNodeExt
  target: string | GraphNodeExt
  relationship?: string
  weight?: number
}

// Dark theme color palette for entity types - optimized for dark background
const TYPE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  symbol: { bg: '#a78bfa', border: '#8b5cf6', text: 'Symbol' },
  character: { bg: '#34d399', border: '#10b981', text: 'Character' },
  emotion: { bg: '#fbbf24', border: '#f59e0b', text: 'Emotion' },
  theme: { bg: '#60a5fa', border: '#3b82f6', text: 'Theme' },
  location: { bg: '#f472b6', border: '#ec4899', text: 'Location' },
  archetype: { bg: '#22d3ee', border: '#06b6d4', text: 'Archetype' },
  person: { bg: '#34d399', border: '#10b981', text: 'Person' },
  action: { bg: '#fb923c', border: '#f97316', text: 'Action' },
  object: { bg: '#c084fc', border: '#a855f7', text: 'Object' },
  personalmeaning: { bg: '#f87171', border: '#ef4444', text: 'Personal' },
  self: { bg: '#2dd4bf', border: '#14b8a6', text: 'Self' },
  entity: { bg: '#94a3b8', border: '#6b7280', text: 'Entity' },
  default: { bg: '#9ca3af', border: '#6b7280', text: 'Other' },
}

const getNodeStyle = (type: string) => {
  const normalized = type.toLowerCase().replace(/_/g, '')
  return TYPE_COLORS[normalized] || TYPE_COLORS.default
}

export function Graph() {
  const queryClient = useQueryClient()
  const { theme } = useTheme()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const graphRef = useRef<any>()
  const containerRef = useRef<HTMLDivElement>(null)

  const [selectedNode, setSelectedNode] = useState<GraphNodeExt | null>(null)
  const [hoveredNode, setHoveredNode] = useState<GraphNodeExt | null>(null)
  const [filterType, setFilterType] = useState<string | null>(null)
  const [showLabels, setShowLabels] = useState(false)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  // Index mutation
  const indexMutation = useMutation({
    mutationKey: ['graph-index'],
    mutationFn: () => graphApi.index(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['graph-status'] })
      queryClient.invalidateQueries({ queryKey: ['graph-export'] })
    },
  })

  // Reindex mutation
  const reindexMutation = useMutation({
    mutationKey: ['graph-reindex'],
    mutationFn: () => graphApi.reindex(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['graph-status'] })
      queryClient.invalidateQueries({ queryKey: ['graph-export'] })
    },
  })

  // Fetch graph status
  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['graph-status'],
    queryFn: () => graphApi.status().then((r) => r.data),
    refetchInterval: () => {
      // Poll every 5s while indexing is in progress
      const isIndexing = indexMutation.isPending || reindexMutation.isPending
      return isIndexing ? 5000 : false
    },
  })

  // Fetch graph data
  const { data: rawGraphData, isLoading: graphLoading } = useQuery({
    queryKey: ['graph-export'],
    queryFn: () => graphApi.export().then((r) => r.data),
    enabled: status?.graph_exists,
  })

  // Process graph data for visualization
  const graphData = useMemo(() => {
    if (!rawGraphData) return { nodes: [], links: [] }

    let nodes: GraphNodeExt[] = rawGraphData.nodes.map((node: GraphNode) => ({
      ...node,
      color: getNodeStyle(node.type).bg,
      size: node.size || 1,
    }))

    let links: GraphLinkExt[] = rawGraphData.edges.map((edge: GraphEdge) => ({
      source: edge.source,
      target: edge.target,
      relationship: edge.relationship,
      weight: edge.weight || 1,
    }))

    // Count connections per node for sizing
    const connectionCount = new Map<string, number>()
    links.forEach(link => {
      const sourceId = typeof link.source === 'string' ? link.source : link.source.id
      const targetId = typeof link.target === 'string' ? link.target : link.target.id
      connectionCount.set(sourceId, (connectionCount.get(sourceId) || 0) + 1)
      connectionCount.set(targetId, (connectionCount.get(targetId) || 0) + 1)
    })

    // Update node sizes based on connections
    nodes = nodes.map(node => ({
      ...node,
      size: Math.max(1, connectionCount.get(node.id) || 1),
    }))

    // Apply type filter
    if (filterType) {
      const matchingNodeIds = new Set(
        nodes.filter(n => n.type.toLowerCase().replace(/_/g, '') === filterType.toLowerCase()).map(n => n.id)
      )
      const connectedIds = new Set<string>()
      links.forEach(l => {
        const sourceId = typeof l.source === 'string' ? l.source : l.source.id
        const targetId = typeof l.target === 'string' ? l.target : l.target.id
        if (matchingNodeIds.has(sourceId)) connectedIds.add(targetId)
        if (matchingNodeIds.has(targetId)) connectedIds.add(sourceId)
      })
      const visibleIds = new Set([...matchingNodeIds, ...connectedIds])
      nodes = nodes.filter(n => visibleIds.has(n.id))
      links = links.filter(l => {
        const sourceId = typeof l.source === 'string' ? l.source : l.source.id
        const targetId = typeof l.target === 'string' ? l.target : l.target.id
        return visibleIds.has(sourceId) && visibleIds.has(targetId)
      })
    }

    return { nodes, links }
  }, [rawGraphData, filterType])

  // Get unique types for filter
  const uniqueTypes = useMemo(() => {
    if (!rawGraphData) return []
    const types = new Map<string, number>()
    rawGraphData.nodes.forEach((n: GraphNode) => {
      const t = n.type.toLowerCase().replace(/_/g, '')
      types.set(t, (types.get(t) || 0) + 1)
    })
    return Array.from(types.entries()).sort((a, b) => b[1] - a[1])
  }, [rawGraphData])

  // Connected nodes for selected node panel
  const connectedNodes = useMemo(() => {
    if (!selectedNode) return []
    const connected: { node: GraphNodeExt; relationship: string }[] = []
    graphData.links.forEach(l => {
      const source = typeof l.source === 'string' ? null : l.source
      const target = typeof l.target === 'string' ? null : l.target
      const sourceId = typeof l.source === 'string' ? l.source : l.source.id
      const targetId = typeof l.target === 'string' ? l.target : l.target.id
      if (sourceId === selectedNode.id && target) {
        connected.push({ node: target, relationship: l.relationship || 'connected' })
      } else if (targetId === selectedNode.id && source) {
        connected.push({ node: source, relationship: l.relationship || 'connected' })
      }
    })
    return connected.slice(0, 5)
  }, [selectedNode, graphData.links])

  // Attach ResizeObserver once the Card is in the DOM (after statusLoading resolves)
  useEffect(() => {
    if (!containerRef.current) return
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        if (width > 0 && height > 0) {
          setDimensions({ width, height })
        }
      }
    })
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [statusLoading])

  // Zoom-to-fit when graph data loads or canvas resizes
  useEffect(() => {
    if (graphData.nodes.length > 0 && graphRef.current && dimensions.width > 0 && dimensions.height > 0) {
      const timer = setTimeout(() => {
        graphRef.current?.zoomToFit(400, 80)
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [graphData.nodes.length, dimensions])

  // Custom node rendering - clean circles with optional labels
  const drawNode = useCallback((node: GraphNodeExt, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label || node.id
    const baseSize = Math.max(5, Math.min(14, (node.size || 1) * 1.5 + 4))
    const isSelected = selectedNode?.id === node.id
    const isHovered = hoveredNode?.id === node.id
    const style = getNodeStyle(node.type)

    // Scale size
    const size = isSelected ? baseSize * 1.3 : isHovered ? baseSize * 1.15 : baseSize

    // Ambient outer ring for large nodes
    if (baseSize >= 4 && !isSelected && !isHovered) {
      ctx.beginPath()
      ctx.arc(node.x!, node.y!, size + 10, 0, 2 * Math.PI)
      ctx.fillStyle = style.bg + '15'
      ctx.fill()
    }

    // Double-ring glow for selected/hovered
    if (isSelected || isHovered) {
      ctx.beginPath()
      ctx.arc(node.x!, node.y!, size + 12, 0, 2 * Math.PI)
      ctx.fillStyle = style.bg + '20'
      ctx.fill()

      ctx.beginPath()
      ctx.arc(node.x!, node.y!, size + 6, 0, 2 * Math.PI)
      ctx.fillStyle = style.bg + '40'
      ctx.fill()
    }

    // Main circle with gradient-like effect
    ctx.beginPath()
    ctx.arc(node.x!, node.y!, size, 0, 2 * Math.PI)
    ctx.fillStyle = style.bg
    ctx.fill()

    // Border
    ctx.strokeStyle = style.border
    ctx.lineWidth = isSelected ? 3 : 1.5
    ctx.stroke()

    // Inner highlight - adjusted for dark theme
    ctx.beginPath()
    ctx.arc(node.x! - size * 0.25, node.y! - size * 0.25, size * 0.25, 0, 2 * Math.PI)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
    ctx.fill()

    // Draw label only when: always if showLabels, or on hover/select
    const shouldShowLabel = showLabels || isHovered || isSelected

    if (shouldShowLabel) {
      const fontSize = Math.max(7, 9 / globalScale)
      ctx.font = `${isSelected ? '600' : '500'} ${fontSize}px Inter, system-ui, sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'

      // Measure text
      const textWidth = ctx.measureText(label).width
      const padding = 5 // Slightly reduced padding
      const labelY = node.y! + size + 5 // Slightly reduced gap

      // Label background with rounded corners effect
      ctx.fillStyle = theme === 'dark' ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)'
      ctx.shadowColor = 'rgba(0, 0, 0, 0.3)'
      ctx.shadowBlur = 8
      ctx.shadowOffsetY = 2
      ctx.beginPath()
      const rectX = node.x! - textWidth / 2 - padding
      const rectY = labelY - 2
      const rectW = textWidth + padding * 2
      const rectH = fontSize + 4 // Reduced height
      const radius = 3 // Slightly smaller radius
      ctx.moveTo(rectX + radius, rectY)
      ctx.lineTo(rectX + rectW - radius, rectY)
      ctx.quadraticCurveTo(rectX + rectW, rectY, rectX + rectW, rectY + radius)
      ctx.lineTo(rectX + rectW, rectY + rectH - radius)
      ctx.quadraticCurveTo(rectX + rectW, rectY + rectH, rectX + rectW - radius, rectY + rectH)
      ctx.lineTo(rectX + radius, rectY + rectH)
      ctx.quadraticCurveTo(rectX, rectY + rectH, rectX, rectY + rectH - radius)
      ctx.lineTo(rectX, rectY + radius)
      ctx.quadraticCurveTo(rectX, rectY, rectX + radius, rectY)
      ctx.closePath()
      ctx.fill()
      ctx.shadowColor = 'transparent'

      // Label text
      ctx.fillStyle = theme === 'dark' ? '#f8fafc' : '#18181b'
      ctx.fillText(label, node.x!, labelY)
    }
  }, [selectedNode, hoveredNode, showLabels, theme])

  // Handle node click
  const handleNodeClick = useCallback((node: GraphNodeExt) => {
    setSelectedNode(prev => prev?.id === node.id ? null : node)

    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 500)
      graphRef.current.zoom(2.5, 500)
    }
  }, [])

  // Link color with purple tint and selection awareness
  const getLinkColor = useCallback((link: GraphLinkExt) => {
    if (!selectedNode) return 'rgba(139,92,246,0.25)'
    const sourceId = typeof link.source === 'string' ? link.source : link.source.id
    const targetId = typeof link.target === 'string' ? link.target : link.target.id
    if (sourceId === selectedNode.id || targetId === selectedNode.id) {
      return 'rgba(139,92,246,0.7)'
    }
    return 'rgba(139,92,246,0.08)'
  }, [selectedNode])

  // Particle color matches source node type
  const getParticleColor = useCallback((link: GraphLinkExt) => {
    const source = typeof link.source === 'string' ? null : link.source
    if (source) return getNodeStyle(source.type).bg
    return '#8b5cf6'
  }, [])

  // Zoom controls
  const handleZoomIn = () => graphRef.current?.zoom(graphRef.current.zoom() * 1.5, 300)
  const handleZoomOut = () => graphRef.current?.zoom(graphRef.current.zoom() / 1.5, 300)
  const handleFitView = () => graphRef.current?.zoomToFit(400, 60)

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="p-6 h-full flex flex-col">
      <PageTitle>Knowledge Graph</PageTitle>

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <Badge variant={status?.graph_exists ? 'success' : 'default'}>
            {status?.graph_exists ? 'Active' : 'Not Built'}
          </Badge>
          <span className="text-sm text-muted">
            {graphData.nodes.length} entities • {graphData.links.length} connections
          </span>
        </div>

        <div className="flex gap-2">
          {status?.pending_dreams && status.pending_dreams > 0 && (
            <Button
              onClick={() => indexMutation.mutate()}
              isLoading={indexMutation.isPending}
              variant="secondary"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Index {status.pending_dreams} Pending
            </Button>
          )}
          <Button
            onClick={() => {
              if (confirm('This will rebuild the entire graph. Continue?')) {
                reindexMutation.mutate()
              }
            }}
            isLoading={reindexMutation.isPending}
            variant="ghost"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Rebuild
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-4">
        <Card className="p-3 border-l-2 border-l-foreground">
          <div className="text-2xl font-bold text-foreground">{status?.total_dreams || 0}</div>
          <div className="text-xs text-muted">Total Dreams</div>
        </Card>
        <Card className="p-3 border-l-2 border-l-success">
          <div className="text-2xl font-bold text-success">{status?.indexed_dreams || 0}</div>
          <div className="text-xs text-muted">Indexed</div>
        </Card>
        <Card className="p-3 border-l-2 border-l-warning">
          <div className="text-2xl font-bold text-warning">{status?.pending_dreams || 0}</div>
          <div className="text-xs text-muted">Pending</div>
        </Card>
        <Card className="p-3 border-l-2 border-l-accent">
          <div className="text-2xl font-bold text-accent">{status?.entity_count || 0}</div>
          <div className="text-xs text-muted">Graph Entities</div>
        </Card>
      </div>

      {/* Graph Container */}
      <Card className="flex-1 relative overflow-hidden !p-0" ref={containerRef}>
        {graphLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <Spinner size="lg" />
          </div>
        ) : graphData.nodes.length > 0 ? (
          <>
            {/* Force Graph with matched background */}
            <ForceGraph2D
              ref={graphRef}
              width={dimensions.width}
              height={dimensions.height}
              graphData={graphData}
              nodeId="id"
              nodeLabel=""
              nodeCanvasObject={drawNode}
              nodePointerAreaPaint={(node, color, ctx) => {
                const n = node as GraphNodeExt
                const size = Math.max(5, Math.min(14, (n.size || 1) * 1.5 + 4)) + 8
                ctx.fillStyle = color
                ctx.beginPath()
                ctx.arc(node.x!, node.y!, size, 0, 2 * Math.PI)
                ctx.fill()
              }}
              linkColor={getLinkColor as any}
              linkWidth={link => {
                const l = link as GraphLinkExt
                const sourceId = typeof l.source === 'string' ? l.source : l.source.id
                const targetId = typeof l.target === 'string' ? l.target : l.target.id
                return selectedNode && (sourceId === selectedNode.id || targetId === selectedNode.id) ? 3 : 1.5
              }}
              linkDirectionalParticles={2}
              linkDirectionalParticleWidth={3}
              linkDirectionalParticleSpeed={0.003}
              linkDirectionalParticleColor={getParticleColor as any}
              onNodeClick={handleNodeClick}
              onNodeHover={node => setHoveredNode(node as GraphNodeExt | null)}
              onBackgroundClick={() => setSelectedNode(null)}
              backgroundColor={theme === 'dark' ? '#0f0f0f' : '#fafafa'}
              cooldownTicks={100}
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
              enableZoomInteraction={true}
              enablePanInteraction={true}
              enableNodeDrag={true}
            />

            {/* Vignette overlay */}
            <div
              className="absolute inset-0 pointer-events-none"
              style={{ background: theme === 'dark'
                ? 'radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.5) 100%)'
                : 'radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.08) 100%)'
              }}
            />

            {/* Labels Toggle */}
            <div className="absolute top-4 left-4">
              <button
                onClick={() => setShowLabels(!showLabels)}
                className={`p-2 rounded-lg border shadow-sm transition-colors ${
                  showLabels
                    ? 'bg-accent/20 border-accent/30 text-accent'
                    : 'bg-surface border-border text-muted hover:bg-surface-2'
                }`}
                title={showLabels ? 'Hide labels' : 'Show labels'}
              >
                {showLabels ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              </button>
            </div>

            {/* Legend - Compact */}
            <div className="absolute top-4 right-4 bg-surface/95 backdrop-blur-sm border border-border rounded-xl p-3 shadow-lg max-w-[250px]">
              <div className="text-xs font-semibold text-muted-foreground mb-2">Entity Types</div>
              <div className="flex flex-wrap gap-1.5">
                {uniqueTypes.map(([type, count]) => {
                  const style = getNodeStyle(type)
                  const isActive = filterType === type
                  const typeName = style.text || type.charAt(0).toUpperCase() + type.slice(1)

                  return (
                    <button
                      key={type}
                      onClick={() => setFilterType(isActive ? null : type)}
                      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs transition-all ${
                        isActive
                          ? 'ring-2 ring-offset-1 ring-offset-surface'
                          : 'hover:scale-105 hover:bg-surface-2/50'
                      }`}
                      style={{
                        backgroundColor: isActive ? style.bg : style.bg + '20',
                        color: isActive ? 'white' : style.bg,
                        outlineColor: isActive ? style.bg : 'transparent',
                      }}
                      title={`${typeName}: ${count} entities`}
                    >
                      <span
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: isActive ? 'white' : style.bg }}
                      />
                      <span className="truncate max-w-[70px]">{typeName}</span>
                      <span className="font-semibold ml-0.5 flex-shrink-0">{count}</span>
                    </button>
                  )
                })}
              </div>
              {filterType && (
                <button
                  onClick={() => setFilterType(null)}
                  className="mt-2 text-xs text-muted hover:text-muted-foreground flex items-center gap-1"
                >
                  <X className="w-3 h-3" /> Clear filter
                </button>
              )}
            </div>

            {/* Zoom Controls */}
            <div className="absolute bottom-4 right-4 flex flex-col gap-1.5">
              <button
                onClick={handleZoomIn}
                className="p-2 bg-surface border border-border rounded-lg hover:bg-surface-2 transition-colors shadow-sm"
                title="Zoom In"
              >
                <ZoomIn className="w-4 h-4 text-muted-foreground" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-2 bg-surface border border-border rounded-lg hover:bg-surface-2 transition-colors shadow-sm"
                title="Zoom Out"
              >
                <ZoomOut className="w-4 h-4 text-muted-foreground" />
              </button>
              <button
                onClick={handleFitView}
                className="p-2 bg-surface border border-border rounded-lg hover:bg-surface-2 transition-colors shadow-sm"
                title="Fit to View"
              >
                <Maximize2 className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            {/* Selected Node Details */}
            {selectedNode && (
              <div className="absolute bottom-4 left-4 max-w-xs bg-surface/95 backdrop-blur-sm border border-border rounded-xl p-4 shadow-xl max-h-[300px] overflow-y-auto">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: getNodeStyle(selectedNode.type).bg }}
                      />
                      <span className="font-semibold text-foreground truncate">{selectedNode.label}</span>
                    </div>
                    <span
                      className="inline-block px-2 py-0.5 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: getNodeStyle(selectedNode.type).bg + '30',
                        color: getNodeStyle(selectedNode.type).bg,
                      }}
                    >
                      {getNodeStyle(selectedNode.type).text}
                    </span>
                  </div>
                  <button
                    onClick={() => setSelectedNode(null)}
                    className="text-muted hover:text-muted-foreground p-1"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                {selectedNode.description && (
                  <p className="text-sm text-muted-foreground mt-3 line-clamp-3">
                    {selectedNode.description}
                  </p>
                )}
                <div className="text-xs text-muted mt-3 pt-2 border-t border-border">
                  {graphData.links.filter(l => {
                    const sourceId = typeof l.source === 'string' ? l.source : l.source.id
                    const targetId = typeof l.target === 'string' ? l.target : l.target.id
                    return sourceId === selectedNode.id || targetId === selectedNode.id
                  }).length} connections
                </div>
                {/* Connected nodes */}
                {connectedNodes.length > 0 && (
                  <div className="mt-2 space-y-1.5">
                    {connectedNodes.map(({ node, relationship }, i) => {
                      const nodeStyle = getNodeStyle(node.type)
                      return (
                        <div key={i} className="flex items-center gap-2 text-xs">
                          <span
                            className="w-2 h-2 rounded-full flex-shrink-0"
                            style={{ backgroundColor: nodeStyle.bg }}
                          />
                          <span className="text-foreground truncate">{node.label}</span>
                          <span className="text-muted ml-auto flex-shrink-0">{relationship}</span>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )}

            {/* Help text */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs text-muted bg-surface/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border">
              Hover to see labels • Click for details • Scroll to zoom • Drag to explore
            </div>
          </>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <EmptyState
              icon={<Network className="w-12 h-12 text-muted" />}
              title="No graph data"
              description={
                status?.pending_dreams && status.pending_dreams > 0
                  ? `Index your ${status.pending_dreams} pending dreams to build the knowledge graph`
                  : 'Start recording dreams to build your knowledge graph'
              }
              action={
                status?.pending_dreams && status.pending_dreams > 0 ? (
                  <Button onClick={() => indexMutation.mutate()}>
                    Index Dreams
                  </Button>
                ) : undefined
              }
            />
          </div>
        )}
      </Card>

      {/* Info Footer */}
      <div className="mt-4 flex items-start gap-2 text-xs text-muted">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <p>
          The knowledge graph visualizes connections between symbols, characters, emotions, and themes.
          Larger nodes have more connections. Colors represent entity types.
        </p>
      </div>
    </div>
  )
}

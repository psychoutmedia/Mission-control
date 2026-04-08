import { create } from 'zustand'
import { AgentType } from '../agents'
import { getGateway } from '../services/gateway'

type Screen = 'signin' | 'dashboard' | 'agent-select' | 'agent-config'
export type AgentStatus = 'idle' | 'working' | 'error' | 'disconnected'

export interface GatewaySession {
  sessionKey: string
  label: string
  status: 'active' | 'idle' | 'busy' | 'error' | 'working' | 'disconnected'
  lastSeen: string
  channel?: string
}

export interface ChatMessage {
  id: string
  from: string
  fromLabel: string
  message: string
  timestamp: string
}

interface AgentState {
  id: string
  name: string
  color: string
  type: AgentType['type']
  ssh: string
  gatewayUrl: string
  autoConnect: boolean
  status: AgentStatus
  lastSeen: string | null
  currentTask: string | null
  sessionKey?: string
  messages: ChatMessage[]
}

interface GatewayState {
  isConnected: boolean
  sessions: GatewaySession[]
  chatMessages: ChatMessage[]
  lastError: string | null
  connect: () => Promise<void>
  disconnect: () => void
  sendMessage: (toSessionKey: string, message: string, fromName: string) => Promise<void>
  addLocalAgent: (agent: AgentState) => void
  updateAgentStatus: (sessionKey: string, status: AgentStatus) => void
}

interface AppState {
  // Screen state
  currentScreen: Screen
  setScreen: (screen: Screen) => void
  
  // Company state
  companyName: string
  setCompanyName: (name: string) => void
  
  // Agent state
  activeAgents: AgentState[]
  selectedAgent: AgentState | null
  addAgent: (agent: AgentType) => void
  removeAgent: (id: string) => void
  selectAgent: (agent: AgentState | null) => void
  updateAgent: (id: string, updates: Partial<AgentState>) => void
  setAgentStatus: (id: string, status: AgentStatus, task?: string) => void
  addMessage: (agentId: string, message: ChatMessage) => void
  
  // Scene state
  selectedZone: string | null
  setSelectedZone: (zone: string | null) => void
  
  // Gateway state
  gateway: GatewayState
}

const defaultAgentState: AgentState = {
  id: '',
  name: '',
  color: '',
  type: 'claude',
  ssh: 'openclaw',
  gatewayUrl: 'ws://127.0.0.1:18789',
  autoConnect: false,
  status: 'idle',
  lastSeen: null,
  currentTask: null,
  messages: []
}

// Gateway store slice
const useGatewayStore = create<GatewayState>((set) => ({
  isConnected: false,
  sessions: [],
  chatMessages: [],
  lastError: null,
  
  connect: async () => {
    try {
      const gateway = getGateway()
      await gateway.connect()
      set({ isConnected: true, lastError: null })
      
      console.log('[Gateway] Connected, fetching sessions...')
      
      // Get sessions from gateway
      const sessions = await gateway.getSessions()
      console.log('[Gateway] Found sessions:', sessions.length)
      set({ sessions })
      
      // Listen for incoming messages
      gateway.subscribe((message) => {
        console.log('[Gateway] Message:', message.type, message.payload)
        
        if (message.type === 'message' || message.type === 'session_send') {
          const chatMsg: ChatMessage = {
            id: `msg-${Date.now()}`,
            from: message.sessionKey || 'unknown',
            fromLabel: message.payload?.from || 'Unknown',
            message: message.payload?.message || message.payload || '',
            timestamp: message.timestamp
          }
          set(state => ({ chatMessages: [...state.chatMessages, chatMsg] }))
        }
        
        if (message.type === 'session_list' && message.payload?.sessions) {
          set({ sessions: message.payload.sessions })
        }
      })
      
    } catch (error: any) {
      console.error('[Gateway] Connection failed:', error)
      set({ isConnected: false, lastError: error?.message || 'Connection failed' })
    }
  },
  
  disconnect: () => {
    const gateway = getGateway()
    gateway.disconnect()
    set({ isConnected: false, sessions: [] })
  },
  
  sendMessage: async (toSessionKey, message, fromName) => {
    const gateway = getGateway()
    if (!gateway.isConnected()) {
      throw new Error('Not connected to gateway')
    }
    
    await gateway.sendMessage(toSessionKey, message, fromName)
    
    // Add to local messages
    const chatMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      from: 'local',
      fromLabel: fromName,
      message,
      timestamp: new Date().toISOString()
    }
    set(state => ({ chatMessages: [...state.chatMessages, chatMsg] }))
  },
  
  addLocalAgent: (agent) => {
    const status = agent.status === 'working' ? 'busy' : (agent.status === 'idle' ? 'idle' : agent.status)
    set(state => ({
      sessions: [
        ...state.sessions,
        {
          sessionKey: agent.sessionKey || agent.id,
          label: agent.name,
          status,
          lastSeen: agent.lastSeen || new Date().toISOString()
        }
      ]
    }))
  },
  
  updateAgentStatus: (sessionKey, status) => {
    set(state => ({
      sessions: state.sessions.map(s =>
        s.sessionKey === sessionKey ? { ...s, status } : s
      )
    }))
  }
}))

// Main store
const useStore = create<AppState>((set) => ({
  // Screen
  currentScreen: 'dashboard',
  setScreen: (screen) => set({ currentScreen: screen }),
  
  // Company
  companyName: 'MY Company Inc.',
  setCompanyName: (name) => set({ companyName: name }),
  
  // Agents
  activeAgents: [
    { ...defaultAgentState, name: 'Claude', color: '#ff4444', type: 'claude', id: '1', status: 'idle', messages: [] },
    { ...defaultAgentState, name: 'Codex', color: '#ffffff', type: 'codex', id: '2', status: 'idle', messages: [] }
  ],
  selectedAgent: null,
  addAgent: (agentType) => set((state) => ({
    activeAgents: [
      ...state.activeAgents,
      { ...defaultAgentState, ...agentType, id: agentType.id || Date.now().toString(), status: 'idle', messages: [] }
    ]
  })),
  removeAgent: (id) => set((state) => ({
    activeAgents: state.activeAgents.filter((a) => a.id !== id),
    selectedAgent: state.selectedAgent?.id === id ? null : state.selectedAgent
  })),
  selectAgent: (agent) => set({ selectedAgent: agent, currentScreen: agent ? 'agent-config' : 'dashboard' }),
  updateAgent: (id, updates) => set((state) => ({
    activeAgents: state.activeAgents.map((a) => 
      a.id === id ? { ...a, ...updates } : a
    ),
    selectedAgent: state.selectedAgent?.id === id 
      ? { ...state.selectedAgent, ...updates } 
      : state.selectedAgent
  })),
  setAgentStatus: (id, status, task) => set((state) => ({
    activeAgents: state.activeAgents.map((a) => 
      a.id === id ? { ...a, status, currentTask: task || null, lastSeen: new Date().toISOString() } : a
    ),
    selectedAgent: state.selectedAgent?.id === id 
      ? { ...state.selectedAgent, status, currentTask: task || null, lastSeen: new Date().toISOString() }
      : state.selectedAgent
  })),
  addMessage: (agentId, message) => set((state) => ({
    activeAgents: state.activeAgents.map((a) =>
      a.id === agentId ? { ...a, messages: [...a.messages, message] } : a
    )
  })),
  
  // Scene
  selectedZone: null,
  setSelectedZone: (zone) => set({ selectedZone: zone }),
  
  // Gateway
  gateway: useGatewayStore.getState()
}))

// Sync gateway state
useGatewayStore.subscribe((state) => {
  useStore.setState({ gateway: state })
})

export { useGatewayStore }
export default useStore

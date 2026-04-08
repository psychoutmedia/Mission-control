import useStore, { AgentStatus } from '../../stores/useStore'
import ChatPanel from '../components/ChatPanel'

export default function ConfigPanel() {
  const { selectedAgent, updateAgent, setScreen, selectAgent, setAgentStatus } = useStore()
  
  if (!selectedAgent) return null
  
  const statusColors: Record<AgentStatus, string> = {
    idle: '#888888',
    working: '#ffaa00',
    error: '#ff4444',
    disconnected: '#666666'
  }
  
  const handleSave = () => {
    selectAgent(null)
    setScreen('dashboard')
  }
  
  const simulateTask = () => {
    const tasks = [
      'Running tests...',
      'Building project...',
      'Analyzing code...',
      'Deploying to staging...',
      'Indexing files...'
    ]
    const randomTask = tasks[Math.floor(Math.random() * tasks.length)]
    setAgentStatus(selectedAgent.id, 'working', randomTask)
    
    // Reset to idle after 5 minutes
    setTimeout(() => {
      setAgentStatus(selectedAgent.id, 'idle')
    }, 300000)
  }
  
  return (
    <div style={{
      position: 'fixed',
      right: 20,
      top: 80,
      bottom: 80,
      width: 360,
      background: 'rgba(26, 26, 26, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRadius: 20,
      border: '1px solid rgba(255, 68, 68, 0.3)',
      padding: 24,
      zIndex: 1500,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'auto'
    }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            background: selectedAgent.color,
            boxShadow: `0 0 20px ${selectedAgent.color}40`
          }} />
          <div>
            <h2 style={{ color: '#fff', fontSize: 18, margin: 0 }}>{selectedAgent.name}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: statusColors[selectedAgent.status],
                boxShadow: `0 0 8px ${statusColors[selectedAgent.status]}`
              }} />
              <span style={{ color: statusColors[selectedAgent.status], fontSize: 12, textTransform: 'uppercase' }}>
                {selectedAgent.status}
              </span>
            </div>
          </div>
        </div>
        
        {/* Tabs */}
        <div style={{ display: 'flex', gap: 16, borderBottom: '1px solid #333', paddingBottom: 12 }}>
          <button style={{
            background: '#333',
            border: 'none',
            borderRadius: 6,
            color: '#fff',
            fontSize: 12,
            padding: '6px 12px',
            cursor: 'pointer'
          }}>
            Connection
          </button>
          <button style={{
            background: 'transparent',
            border: 'none',
            borderRadius: 6,
            color: '#666',
            fontSize: 12,
            padding: '6px 12px',
            cursor: 'pointer'
          }}>
            Routing
          </button>
          <button style={{
            background: 'rgba(255, 68, 68, 0.2)',
            border: '1px solid rgba(255, 68, 68, 0.3)',
            borderRadius: 6,
            color: '#ff6666',
            fontSize: 12,
            padding: '6px 12px',
            cursor: 'pointer'
          }}>
            Monitor
          </button>
        </div>
      </div>
      
      {/* Monitor Panel */}
      <div style={{ flex: 1 }}>
        {/* Status Card */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: 12,
          padding: 16,
          marginBottom: 20
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ color: '#888', fontSize: 12 }}>Status</span>
            <span style={{ color: statusColors[selectedAgent.status], fontSize: 12, fontWeight: 600 }}>
              {selectedAgent.status.toUpperCase()}
            </span>
          </div>
          
          {selectedAgent.currentTask && (
            <div style={{ marginBottom: 12 }}>
              <span style={{ color: '#888', fontSize: 12 }}>Current Task</span>
              <div style={{ color: '#fff', fontSize: 14, marginTop: 4 }}>
                {selectedAgent.currentTask}
              </div>
            </div>
          )}
          
          {selectedAgent.lastSeen && (
            <div>
              <span style={{ color: '#888', fontSize: 12 }}>Last Seen</span>
              <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>
                {new Date(selectedAgent.lastSeen).toLocaleTimeString()}
              </div>
            </div>
          )}
        </div>
        
        {/* Simulation */}
        <div style={{
          background: 'rgba(255, 68, 68, 0.1)',
          border: '1px solid rgba(255, 68, 68, 0.2)',
          borderRadius: 12,
          padding: 16,
          marginBottom: 20
        }}>
          <div style={{ color: '#ff6666', fontSize: 12, marginBottom: 12, fontWeight: 600 }}>
            SIMULATION
          </div>
          <p style={{ color: '#888', fontSize: 11, marginBottom: 12 }}>
            Simulate agent activity for testing
          </p>
          <button
            onClick={simulateTask}
            disabled={selectedAgent.status === 'working'}
            style={{
              width: '100%',
              padding: '10px 16px',
              fontSize: 14,
              borderRadius: 8,
              border: 'none',
              background: selectedAgent.status === 'working' ? '#333' : 'linear-gradient(135deg, #ff4444, #cc3333)',
              color: selectedAgent.status === 'working' ? '#666' : '#fff',
              cursor: selectedAgent.status === 'working' ? 'not-allowed' : 'pointer'
            }}
          >
            {selectedAgent.status === 'working' ? 'Agent Busy...' : 'Simulate Task'}
          </button>
        </div>
        
        {/* Chat Panel */}
        <ChatPanel 
          agentId={selectedAgent.id}
          agentName={selectedAgent.name}
          agentSessionKey={selectedAgent.sessionKey || selectedAgent.id}
        />
        
        {/* Connection Form */}
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', color: '#888', fontSize: 12, marginBottom: 6 }}>SSH connection</label>
          <input
            type="text"
            value={selectedAgent.ssh}
            onChange={(e) => updateAgent(selectedAgent.id, { ssh: e.target.value })}
            style={{
              width: '100%',
              padding: '10px 12px',
              fontSize: 14,
              borderRadius: 8,
              border: '1px solid #333',
              background: '#0a0a0a',
              color: '#fff',
              outline: 'none'
            }}
          />
        </div>
        
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', color: '#888', fontSize: 12, marginBottom: 6 }}>Local Gateway URL</label>
          <input
            type="text"
            value={selectedAgent.gatewayUrl}
            onChange={(e) => updateAgent(selectedAgent.id, { gatewayUrl: e.target.value })}
            style={{
              width: '100%',
              padding: '10px 12px',
              fontSize: 14,
              borderRadius: 8,
              border: '1px solid #333',
              background: '#0a0a0a',
              color: '#fff',
              outline: 'none',
              fontFamily: 'monospace'
            }}
          />
        </div>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          padding: '12px 0',
          borderTop: '1px solid #333'
        }}>
          <span style={{ color: '#888', fontSize: 14 }}>Auto-connect on agent start</span>
          <button
            onClick={() => updateAgent(selectedAgent.id, { autoConnect: !selectedAgent.autoConnect })}
            style={{
              width: 44,
              height: 24,
              borderRadius: 12,
              border: 'none',
              background: selectedAgent.autoConnect ? '#ff4444' : '#333',
              cursor: 'pointer',
              position: 'relative',
              transition: 'all 0.2s'
            }}
          >
            <div style={{
              position: 'absolute',
              top: 2,
              left: selectedAgent.autoConnect ? 22 : 2,
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: '#fff',
              transition: 'all 0.2s'
            }} />
          </button>
        </div>
      </div>
      
      {/* Footer */}
      <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
        <button
          onClick={() => selectAgent(null)}
          style={{
            flex: 1,
            padding: '12px 16px',
            fontSize: 14,
            borderRadius: 8,
            border: '1px solid #333',
            background: 'transparent',
            color: '#888',
            cursor: 'pointer'
          }}
        >
          Cancel
        </button>
        <button
          style={{
            flex: 1,
            padding: '12px 16px',
            fontSize: 14,
            borderRadius: 8,
            border: 'none',
            background: '#333',
            color: '#fff',
            cursor: 'pointer'
          }}
        >
          Test
        </button>
        <button
          onClick={handleSave}
          style={{
            flex: 1,
            padding: '12px 16px',
            fontSize: 14,
            fontWeight: 600,
            borderRadius: 8,
            border: 'none',
            background: 'linear-gradient(135deg, #ff4444, #cc3333)',
            color: '#fff',
            cursor: 'pointer'
          }}
        >
          Save
        </button>
      </div>
    </div>
  )
}

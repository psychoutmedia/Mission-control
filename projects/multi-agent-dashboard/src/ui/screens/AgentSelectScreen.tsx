import { AVAILABLE_AGENTS } from '../../agents'
import useStore from '../../stores/useStore'

export default function AgentSelectScreen() {
  const { setScreen, addAgent } = useStore()
  
  const handleSelect = (agent: typeof AVAILABLE_AGENTS[0]) => {
    addAgent(agent)
    setScreen('dashboard')
  }
  
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.9)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000
    }}>
      <div style={{
        background: '#1a1a1a',
        padding: 32,
        borderRadius: 20,
        border: '1px solid rgba(255, 68, 68, 0.3)',
        maxWidth: 700,
        width: '90%'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <h2 style={{ color: '#fff', fontSize: 20 }}>Recruit Agent</h2>
          <button
            onClick={() => setScreen('dashboard')}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#666',
              fontSize: 24,
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 16
        }}>
          {AVAILABLE_AGENTS.map((agent) => (
            <button
              key={agent.id}
              onClick={() => handleSelect(agent)}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '2px solid transparent',
                borderRadius: 16,
                padding: 20,
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = agent.color
                e.currentTarget.style.background = `${agent.color}15`
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'transparent'
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
              }}
            >
              {/* Agent avatar placeholder */}
              <div style={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                background: agent.color,
                margin: '0 auto 12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 24,
                fontWeight: 'bold',
                color: agent.type === 'codex' ? '#000' : '#fff'
              }}>
                {agent.name[0]}
              </div>
              
              <div style={{ color: '#fff', fontWeight: 600, marginBottom: 4 }}>{agent.name}</div>
              <div style={{ color: '#666', fontSize: 12 }}>{agent.description}</div>
            </button>
          ))}
        </div>
        
        {/* Tabs */}
        <div style={{
          display: 'flex',
          gap: 24,
          marginTop: 24,
          borderTop: '1px solid #333',
          paddingTop: 16
        }}>
          <button style={{
            background: 'transparent',
            border: 'none',
            color: '#ff4444',
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            paddingBottom: 8,
            borderBottom: '2px solid #ff4444'
          }}>
            Recruiting
          </button>
          <button style={{
            background: 'transparent',
            border: 'none',
            color: '#666',
            fontSize: 14,
            cursor: 'pointer'
          }}>
            Customizations
          </button>
        </div>
      </div>
    </div>
  )
}

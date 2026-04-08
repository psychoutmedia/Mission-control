import useStore from '../../stores/useStore'

export default function GatewayStatus() {
  const { gateway } = useStore()
  const { sessions, lastError } = gateway

  return (
    <div style={{
      position: 'fixed',
      left: 20,
      bottom: 20,
      background: 'rgba(26, 26, 26, 0.95)',
      backdropFilter: 'blur(10px)',
      borderRadius: 12,
      border: '1px solid rgba(255, 68, 68, 0.3)',
      padding: 16,
      zIndex: 1000,
      minWidth: 200
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 8,
        marginBottom: 12 
      }}>
        <div style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: sessions.length > 0 ? '#00ff00' : (lastError ? '#ff4444' : '#666666'),
          boxShadow: sessions.length > 0 ? '0 0 8px #00ff00' : 'none'
        }} />
        <span style={{ color: '#fff', fontSize: 12, fontWeight: 600 }}>
          Agents
        </span>
        <span style={{ color: '#888', fontSize: 10 }}>
          ({sessions.length})
        </span>
      </div>

      {lastError && (
        <div style={{ 
          color: '#ff6666', 
          fontSize: 10, 
          marginBottom: 8,
          maxWidth: 180
        }}>
          {lastError}
        </div>
      )}

      {/* Sessions list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {sessions.map((session) => (
          <div key={session.sessionKey} style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 10,
            color: '#888'
          }}>
            <div style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: session.status === 'busy' ? '#ffaa00' : '#00ff00'
            }} />
            <span style={{ 
              color: '#ccc',
              maxWidth: 120,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {session.label || session.sessionKey.slice(0, 15)}
            </span>
          </div>
        ))}
        
        {sessions.length === 0 && (
          <div style={{ fontSize: 10, color: '#666' }}>
            No agents connected
          </div>
        )}
      </div>
    </div>
  )
}

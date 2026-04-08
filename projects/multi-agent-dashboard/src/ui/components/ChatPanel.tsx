import { useState } from 'react'
import useStore from '../../stores/useStore'

interface ChatPanelProps {
  agentId: string
  agentName: string
  agentSessionKey?: string
}

export default function ChatPanel({ agentId, agentName }: ChatPanelProps) {
  const { gateway, activeAgents } = useStore()
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  
  // Get other agents to chat with
  const otherAgents = activeAgents.filter(a => a.id !== agentId)
  
  const handleSend = async () => {
    if (!message.trim() || otherAgents.length === 0) return
    
    setSending(true)
    try {
      // Send to all other agents
      for (const agent of otherAgents) {
        await gateway.sendMessage(
          agent.sessionKey || agent.id,
          message,
          agentName
        )
      }
      setMessage('')
    } catch (e) {
      console.error('Failed to send message:', e)
    }
    setSending(false)
  }
  
  const quickMessages = [
    'Hey! How\'s it going?',
    'Running tests now...',
    'Need help with something',
    'Build complete!',
    'Deploying to staging...',
    'Hey, check this out!',
  ]
  
  return (
    <div style={{
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: 12,
      padding: 16,
      marginTop: 16
    }}>
      <div style={{ 
        color: '#ff6666', 
        fontSize: 12, 
        fontWeight: 600,
        marginBottom: 12 
      }}>
        CHAT
      </div>
      
      {/* Send to other agents */}
      <div style={{ marginBottom: 12 }}>
        <label style={{ display: 'block', color: '#888', fontSize: 11, marginBottom: 6 }}>
          Send to: {otherAgents.map(a => a.name).join(', ') || 'None'}
        </label>
        
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          style={{
            width: '100%',
            padding: '10px 12px',
            fontSize: 13,
            borderRadius: 8,
            border: '1px solid #333',
            background: '#0a0a0a',
            color: '#fff',
            outline: 'none',
            resize: 'none',
            minHeight: 60,
            fontFamily: 'inherit'
          }}
        />
        
        <button
          onClick={handleSend}
          disabled={sending || !message.trim()}
          style={{
            marginTop: 8,
            width: '100%',
            padding: '10px 16px',
            fontSize: 13,
            borderRadius: 8,
            border: 'none',
            background: sending ? '#333' : 'linear-gradient(135deg, #ff4444, #cc3333)',
            color: sending ? '#666' : '#fff',
            cursor: sending ? 'not-allowed' : 'pointer'
          }}
        >
          {sending ? 'Sending...' : 'Send Message'}
        </button>
      </div>
      
      {/* Quick messages */}
      <div>
        <label style={{ display: 'block', color: '#666', fontSize: 10, marginBottom: 6 }}>
          Quick messages
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {quickMessages.map((msg, i) => (
            <button
              key={i}
              onClick={() => setMessage(msg)}
              style={{
                padding: '6px 10px',
                fontSize: 10,
                borderRadius: 6,
                border: '1px solid #333',
                background: 'rgba(255, 255, 255, 0.05)',
                color: '#aaa',
                cursor: 'pointer'
              }}
            >
              {msg.slice(0, 20)}...
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

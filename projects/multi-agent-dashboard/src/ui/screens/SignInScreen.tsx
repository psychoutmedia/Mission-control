import { useState } from 'react'
import useStore from '../../stores/useStore'

export default function SignInScreen() {
  const { companyName, setCompanyName, setScreen } = useStore()
  const [inputName, setInputName] = useState(companyName)
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setCompanyName(inputName)
    setScreen('dashboard')
  }
  
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000
    }}>
      <div style={{
        background: '#1a1a1a',
        padding: 40,
        borderRadius: 20,
        border: '1px solid rgba(255, 68, 68, 0.3)',
        width: 400,
        textAlign: 'center'
      }}>
        <h1 style={{ color: '#fff', marginBottom: 8, fontSize: 24 }}>Welcome Back</h1>
        <p style={{ color: '#888', marginBottom: 32, fontSize: 14 }}>Enter your company name</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            placeholder="Company Name"
            style={{
              width: '100%',
              padding: '14px 16px',
              fontSize: 16,
              borderRadius: 10,
              border: '1px solid #333',
              background: '#0a0a0a',
              color: '#fff',
              marginBottom: 20,
              outline: 'none'
            }}
          />
          
          <button
            type="submit"
            style={{
              width: '100%',
              padding: '14px 24px',
              fontSize: 16,
              fontWeight: 600,
              borderRadius: 10,
              border: 'none',
              background: 'linear-gradient(135deg, #ff4444, #cc3333)',
              color: '#fff',
              cursor: 'pointer'
            }}
          >
            Continue
          </button>
        </form>
      </div>
    </div>
  )
}

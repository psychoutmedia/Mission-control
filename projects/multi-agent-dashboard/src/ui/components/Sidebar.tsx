import useStore from '../../stores/useStore'

type Screen = 'signin' | 'dashboard' | 'agent-select' | 'agent-config'

export default function Sidebar() {
  const { currentScreen, setScreen } = useStore()
  
  const icons: { name: string; symbol: string; screen: Screen | null }[] = [
    { name: 'Home', symbol: '⌂', screen: 'dashboard' },
    { name: 'Hand', symbol: '✋', screen: null },
    { name: 'Map', symbol: '📍', screen: null },
    { name: 'Flask', symbol: '🧪', screen: null },
    { name: 'Globe', symbol: '🌐', screen: null },
  ]
  
  return (
    <div style={{
      position: 'fixed',
      left: 20,
      top: '50%',
      transform: 'translateY(-50%)',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      padding: 12,
      background: 'rgba(30, 30, 30, 0.8)',
      backdropFilter: 'blur(10px)',
      borderRadius: 16,
      border: '1px solid rgba(255, 68, 68, 0.3)',
      zIndex: 1000
    }}>
      {icons.map((icon) => (
        <button
          key={icon.name}
          title={icon.name}
          onClick={() => icon.screen && setScreen(icon.screen)}
          style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            border: currentScreen === icon.screen ? '1px solid #ff4444' : 'none',
            background: currentScreen === icon.screen 
              ? 'rgba(255, 68, 68, 0.3)' 
              : 'rgba(255, 255, 255, 0.1)',
            color: '#fff',
            fontSize: 20,
            cursor: icon.screen ? 'pointer' : 'default',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            if (icon.screen) {
              e.currentTarget.style.background = 'rgba(255, 68, 68, 0.3)'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = currentScreen === icon.screen 
              ? 'rgba(255, 68, 68, 0.3)' 
              : 'rgba(255, 255, 255, 0.1)'
          }}
        >
          {icon.symbol}
        </button>
      ))}
    </div>
  )
}

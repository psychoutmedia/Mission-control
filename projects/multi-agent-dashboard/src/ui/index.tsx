import useStore from '../stores/useStore'
import SignInScreen from './screens/SignInScreen'
import AgentSelectScreen from './screens/AgentSelectScreen'
import ConfigPanel from './screens/ConfigPanel'
import Sidebar from './components/Sidebar'
import GatewayStatus from './components/GatewayStatus'

export default function UI() {
  const { currentScreen } = useStore()
  
  return (
    <>
      {/* Sidebar */}
      <Sidebar />
      
      {/* Screens */}
      {currentScreen === 'signin' && <SignInScreen />}
      {currentScreen === 'agent-select' && <AgentSelectScreen />}
      {currentScreen === 'agent-config' && <ConfigPanel />}
      
      {/* Gateway Status */}
      <GatewayStatus />
      
      {/* Status bar */}
      <div style={{
        position: 'fixed',
        bottom: 20,
        left: 260,
        color: '#666',
        fontSize: 12,
        fontFamily: 'monospace'
      }}>
        {new Date().toISOString().slice(0, 10)} · d8e8cd9
      </div>
    </>
  )
}

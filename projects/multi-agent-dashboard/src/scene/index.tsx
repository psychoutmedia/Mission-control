import Floor from './Floor'
import Zones from './Zones'
import StaticObjects from './StaticObjects'
import Agent from '../agents/Agent'
import useStore from '../stores/useStore'

export default function Scene() {
  const { activeAgents } = useStore()
  
  return (
    <>
      <color attach="background" args={['#0d0d0d']} />
      <fog attach="fog" args={['#0d0d0d', 50, 150]} />
      
      {/* Invisible plane for catching pointer events */}
      <mesh 
        rotation={[-Math.PI / 2, 0, 0]} 
        position={[0, 0, 0]} 
        visible={false}
      >
        <planeGeometry args={[500, 500]} />
        <meshBasicMaterial />
      </mesh>
      
      <Floor />
      <Zones />
      <StaticObjects />
      
      {/* Render all active agents from store */}
      {activeAgents.map((agent) => (
        <Agent
          key={agent.id}
          name={agent.name}
          position={[Math.random() * 4, 0, 2 + Math.random() * 2]}
          color={agent.color}
          id={agent.id}
        />
      ))}
    </>
  )
}

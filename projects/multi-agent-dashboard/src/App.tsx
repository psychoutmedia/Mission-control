import { Canvas } from '@react-three/fiber'
import { OrthographicCamera, Environment, ContactShadows } from '@react-three/drei'
import Scene from './scene'
import UI from './ui'

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* Three.js Canvas */}
      <Canvas shadows style={{ background: '#0a0a0a' }}>
        <OrthographicCamera 
          makeDefault 
          position={[20, 20, 20]} 
          zoom={25} 
          near={0.1} 
          far={1000}
          onUpdate={c => c.lookAt(0, 0, 0)}
        />
        
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight 
          position={[10, 20, 10]} 
          intensity={1.2} 
          castShadow 
          shadow-mapSize={[2048, 2048]}
          shadow-bias={-0.0001}
        />
        <pointLight position={[-10, 10, -10]} intensity={0.5} color="#ff4444" />
        <pointLight position={[10, 10, 10]} intensity={0.3} color="#4444ff" />
        
        {/* Environment for reflections */}
        <Environment preset="city" />
        
        {/* Contact shadows for grounding */}
        <ContactShadows 
          position={[0, 0, 0]} 
          opacity={0.5} 
          scale={50} 
          blur={2} 
          far={10} 
        />
        
        <Scene />
      </Canvas>
      
      {/* UI Overlay */}
      <UI />
    </div>
  )
}

export default App

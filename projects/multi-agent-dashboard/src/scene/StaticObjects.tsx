import { Text } from '@react-three/drei'
import { useState } from 'react'
import useStore from '../stores/useStore'

export default function StaticObjects() {
  const { setScreen } = useStore()
  const [hovered, setHovered] = useState(false)
  
  return (
    <group>
      {/* Company Sign Billboard */}
      <group 
        position={[12, 0, -12]}
        onPointerEnter={(e) => {
          e.stopPropagation()
          setHovered(true)
          document.body.style.cursor = 'pointer'
        }}
        onPointerLeave={(e) => {
          e.stopPropagation()
          setHovered(false)
          document.body.style.cursor = 'auto'
        }}
        onClick={(e) => {
          e.stopPropagation()
          setScreen('agent-select')
        }}
      >
        {/* Pole */}
        <mesh position={[0, 3, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 6]} />
          <meshStandardMaterial color="#444" />
        </mesh>
        
        {/* Sign board */}
        <mesh position={[0, 6.5, 0]} castShadow>
          <boxGeometry args={[6, 1.5, 0.1]} />
          <meshStandardMaterial color={hovered ? '#ff5555' : '#ffffff'} />
        </mesh>
        
        {/* Sign text */}
        <Text
          position={[0, 6.5, 0.06]}
          fontSize={0.6}
          color="#ff3333"
          anchorX="center"
          anchorY="middle"
        >
          MY Company Inc.
        </Text>
        
        {/* Red logo */}
        <mesh position={[2.5, 6.5, 0.06]}>
          <circleGeometry args={[0.4, 32]} />
          <meshStandardMaterial color="#ff3333" />
        </mesh>
        
        {/* Click prompt */}
        <Text
          position={[0, 5.2, 0]}
          fontSize={0.2}
          color={hovered ? '#ff6666' : '#888'}
          anchorX="center"
          anchorY="middle"
        >
          {hovered ? 'Click to Recruit Agents' : ''}
        </Text>
      </group>
      
      {/* Anvil (Crafting Station) */}
      <group position={[0, 0, 0]}>
        {/* Base */}
        <mesh position={[0, 0.3, 0]} castShadow>
          <boxGeometry args={[2, 0.6, 1.5]} />
          <meshStandardMaterial color="#2a2a2a" />
        </mesh>
        
        {/* Top */}
        <mesh position={[0, 0.8, 0]} castShadow>
          <boxGeometry args={[2.5, 0.4, 1.8]} />
          <meshStandardMaterial color="#3a3a3a" />
        </mesh>
        
        {/* Anvil horn */}
        <mesh position={[1.4, 0.8, 0]} rotation={[0, 0, -0.3]} castShadow>
          <boxGeometry args={[1, 0.4, 1.4]} />
          <meshStandardMaterial color="#3a3a3a" />
        </mesh>
        
        {/* Label */}
        <Text
          position={[0, 1.3, 0]}
          fontSize={0.3}
          color="#666"
          anchorX="center"
          anchorY="middle"
        >
          Anvil
        </Text>
      </group>
      
      {/* Development Stack/Folders */}
      <group position={[-8, 0, -2]}>
        {/* Stack of folders */}
        <mesh position={[0, 0.3, 0]} castShadow>
          <boxGeometry args={[1, 0.6, 0.8]} />
          <meshStandardMaterial color="#6b4c9a" />
        </mesh>
        <mesh position={[0, 0.7, -0.1]} castShadow>
          <boxGeometry args={[1.1, 0.5, 0.85]} />
          <meshStandardMaterial color="#8058c8" />
        </mesh>
        <mesh position={[0, 1.15, -0.15]} castShadow>
          <boxGeometry args={[1.15, 0.45, 0.9]} />
          <meshStandardMaterial color="#9b6fe0" />
        </mesh>
        
        {/* Gear icon on top */}
        <mesh position={[0, 1.6, -0.15]}>
          <torusGeometry args={[0.3, 0.1, 8, 16]} />
          <meshStandardMaterial color="#444" />
        </mesh>
      </group>
      
      {/* Conference Table */}
      <group position={[10, 0, 10]}>
        {/* Table top */}
        <mesh position={[0, 0.9, 0]} castShadow>
          <boxGeometry args={[8, 0.15, 4]} />
          <meshStandardMaterial color="#3d2817" roughness={0.3} metalness={0.1} />
        </mesh>
        
        {/* Table legs */}
        <mesh position={[-3.5, 0.45, -1.5]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 0.9, 8]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[3.5, 0.45, -1.5]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 0.9, 8]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[-3.5, 0.45, 1.5]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 0.9, 8]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[3.5, 0.45, 1.5]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 0.9, 8]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        
        {/* Center support */}
        <mesh position={[0, 0.4, 0]}>
          <boxGeometry args={[6, 0.8, 2]} />
          <meshStandardMaterial color="#2d1f12" />
        </mesh>
        
        {/* Label */}
        <Text
          position={[0, 1.2, 0]}
          fontSize={0.25}
          color="#888"
          anchorX="center"
          anchorY="middle"
        >
          Conference Table
        </Text>
      </group>
    </group>
  )
}

import { useState } from 'react'
import { Text } from '@react-three/drei'
import useStore from '../stores/useStore'

export default function Zones() {
  const zoneColor = '#ff3333'
  const hoverColor = '#ff6666'
  const [hoveredZone, setHoveredZone] = useState<string | null>(null)
  const { setSelectedZone } = useStore()
  
  return (
    <group>
      {/* App Development Zone */}
      <group 
        position={[-10, 0.01, -5]}
        onPointerEnter={() => setHoveredZone('development')}
        onPointerLeave={() => setHoveredZone(null)}
        onClick={() => setSelectedZone('development')}
      >
        {/* Zone boundary lines */}
        <lineLoop>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={5}
              array={new Float32Array([
                0, 0, 0,
                15, 0, 0,
                15, 0, 10,
                0, 0, 10,
                0, 0, 0
              ])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color={hoveredZone === 'development' ? hoverColor : zoneColor} linewidth={2} />
        </lineLoop>
        
        {/* Zone fill on hover */}
        {hoveredZone === 'development' && (
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[7.5, 0.02, 5]}>
            <planeGeometry args={[15, 10]} />
            <meshBasicMaterial color={zoneColor} opacity={0.1} transparent />
          </mesh>
        )}
        
        {/* Zone label */}
        <Text
          position={[7.5, 0.1, 5]}
          fontSize={1}
          color={hoveredZone === 'development' ? hoverColor : zoneColor}
          anchorX="center"
          anchorY="middle"
          rotation={[-Math.PI / 2, 0, 0]}
        >
          App Development
        </Text>
      </group>
      
      {/* Mac Mini Zone */}
      <group 
        position={[-10, 0.01, 8]}
        onPointerEnter={() => setHoveredZone('macmini')}
        onPointerLeave={() => setHoveredZone(null)}
        onClick={() => setSelectedZone('macmini')}
      >
        <lineLoop>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={5}
              array={new Float32Array([
                0, 0, 0,
                15, 0, 0,
                15, 0, 8,
                0, 0, 8,
                0, 0, 0
              ])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color={hoveredZone === 'macmini' ? hoverColor : zoneColor} linewidth={2} />
        </lineLoop>
        
        {/* Zone fill on hover */}
        {hoveredZone === 'macmini' && (
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[7.5, 0.02, 4]}>
            <planeGeometry args={[15, 8]} />
            <meshBasicMaterial color={zoneColor} opacity={0.1} transparent />
          </mesh>
        )}
        
        <Text
          position={[7.5, 0.1, 4]}
          fontSize={0.8}
          color={hoveredZone === 'macmini' ? hoverColor : zoneColor}
          anchorX="center"
          anchorY="middle"
          rotation={[-Math.PI / 2, 0, 0]}
        >
          Mac Mini 127.0.0.1
        </Text>
      </group>
      
      {/* Conference Room Zone */}
      <group 
        position={[5, 0.01, 5]}
        onPointerEnter={() => setHoveredZone('conference')}
        onPointerLeave={() => setHoveredZone(null)}
        onClick={() => setSelectedZone('conference')}
      >
        <lineLoop>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={5}
              array={new Float32Array([
                0, 0, 0,
                12, 0, 0,
                12, 0, 10,
                0, 0, 10,
                0, 0, 0
              ])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color={hoveredZone === 'conference' ? hoverColor : zoneColor} linewidth={2} />
        </lineLoop>
        
        {/* Zone fill on hover */}
        {hoveredZone === 'conference' && (
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[6, 0.02, 5]}>
            <planeGeometry args={[12, 10]} />
            <meshBasicMaterial color={zoneColor} opacity={0.1} transparent />
          </mesh>
        )}
        
        <Text
          position={[6, 0.1, 5]}
          fontSize={0.8}
          color={hoveredZone === 'conference' ? hoverColor : zoneColor}
          anchorX="center"
          anchorY="middle"
          rotation={[-Math.PI / 2, 0, 0]}
        >
          Conference Room
        </Text>
      </group>
    </group>
  )
}

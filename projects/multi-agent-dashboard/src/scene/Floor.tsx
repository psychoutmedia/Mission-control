export default function Floor() {
  return (
    <group>
      {/* Main floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      
      {/* Grid lines */}
      <gridHelper 
        args={[100, 50, '#2a2a2a', '#1a1a1a']} 
        position={[0, 0, 0]} 
      />
      
      {/* Secondary grid for depth effect */}
      <gridHelper 
        args={[100, 25, '#333333', '#151515']} 
        position={[0, -0.02, 0]} 
      />
    </group>
  )
}

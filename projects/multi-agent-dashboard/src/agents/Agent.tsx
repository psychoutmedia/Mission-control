import { useRef, useState, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Text, Float, MeshDistortMaterial } from '@react-three/drei'
import * as THREE from 'three'
import useStore, { AgentStatus } from '../stores/useStore'

interface AgentProps {
  name: string
  position: [number, number, number]
  color: string
  id?: string
}

const statusColors: Record<AgentStatus, string> = {
  idle: '#00ff00',
  working: '#ffaa00',
  error: '#ff4444',
  disconnected: '#666666'
}

const TABLE_BOUNDS = {
  xMin: 6,
  xMax: 14,
  zMin: 8,
  zMax: 12,
  radius: 1
}

const ZONES = {
  dev: { xMin: -10, xMax: 0, zMin: -5, zMax: 5 },
  macMini: { xMin: -10, xMax: 0, zMin: 8, zMax: 16 },
  conference: { xMin: 5, xMax: 14, zMin: 5, zMax: 14 }
}

function isCollidingWithTable(pos: THREE.Vector3): boolean {
  return (
    pos.x > TABLE_BOUNDS.xMin - TABLE_BOUNDS.radius &&
    pos.x < TABLE_BOUNDS.xMax + TABLE_BOUNDS.radius &&
    pos.z > TABLE_BOUNDS.zMin - TABLE_BOUNDS.radius &&
    pos.z < TABLE_BOUNDS.zMax + TABLE_BOUNDS.radius
  )
}

function getRandomZoneTarget() {
  const zoneKeys = Object.keys(ZONES) as Array<keyof typeof ZONES>
  const zoneKey = zoneKeys[Math.floor(Math.random() * zoneKeys.length)]
  const zone = ZONES[zoneKey]
  
  let attempts = 0
  let target: [number, number, number] = [0, 0, 0]
  
  do {
    target = [
      zone.xMin + Math.random() * (zone.xMax - zone.xMin),
      0,
      zone.zMin + Math.random() * (zone.zMax - zone.zMin)
    ] as [number, number, number]
    attempts++
  } while (
    isCollidingWithTable(new THREE.Vector3(...target)) && 
    attempts < 10
  )
  
  return target
}

export default function Agent({ name, position: startPos, color, id }: AgentProps) {
  const groupRef = useRef<THREE.Group>(null)
  const [position, setPosition] = useState(new THREE.Vector3(...startPos))
  const [targetPosition, setTargetPosition] = useState<[number, number, number] | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [hovered, setHovered] = useState(false)
  const [isWalking, setIsWalking] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [messageTimer, setMessageTimer] = useState<number>(0)
  const { selectAgent, activeAgents } = useStore()
  const { camera, raycaster, pointer } = useThree()
  
  const agentData = activeAgents.find(a => a.id === id)
  const status: AgentStatus = agentData?.status || 'idle'
  
  // Show latest message from agent's message list
  useEffect(() => {
    if (agentData?.messages && agentData.messages.length > 0) {
      const latest = agentData.messages[agentData.messages.length - 1]
      setMessage(latest.message)
      setMessageTimer(Date.now())
    }
  }, [agentData?.messages])
  
  // Clear message after 5 seconds
  useFrame(() => {
    if (messageTimer && Date.now() - messageTimer > 5000) {
      setMessage(null)
      setMessageTimer(0)
    }
  })
  
  useEffect(() => {
    if (status === 'idle' && !targetPosition && !isDragging) {
      const timeout = setTimeout(() => {
        setTargetPosition(getRandomZoneTarget())
      }, 2000 + Math.random() * 3000)
      
      return () => clearTimeout(timeout)
    }
  }, [status, targetPosition, isDragging])
  
  useFrame((_, delta) => {
    if (!groupRef.current) return
    
    const walkSpeed = 1.5
    
    if (isDragging) {
      const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)
      raycaster.setFromCamera(pointer, camera)
      const targetPoint = new THREE.Vector3()
      raycaster.ray.intersectPlane(plane, targetPoint)
      
      if (targetPoint) {
        const nextPos = new THREE.Vector3(targetPoint.x, 0, targetPoint.z)
        if (!isCollidingWithTable(nextPos)) {
          position.copy(nextPos)
          setPosition(position.clone())
        }
        setIsWalking(true)
        setTargetPosition(null)
      }
    }
    else if (targetPosition && status === 'idle') {
      const target = new THREE.Vector3(...targetPosition)
      const direction = target.clone().sub(position).normalize()
      const distance = position.distanceTo(target)
      
      if (distance > 0.2) {
        const nextPos = position.clone().add(direction.multiplyScalar(walkSpeed * delta))
        
        if (isCollidingWithTable(nextPos)) {
          setIsWalking(false)
          setTargetPosition(null)
        } else {
          position.copy(nextPos)
          setPosition(position.clone())
          setIsWalking(true)
        }
      } else {
        setIsWalking(false)
        setTargetPosition(null)
      }
    } else {
      setIsWalking(false)
    }
    
    groupRef.current.position.copy(position)
    
    if (isWalking && !isDragging && targetPosition) {
      const target = new THREE.Vector3(...targetPosition)
      const direction = target.clone().sub(position).normalize()
      if (direction.length() > 0.1) {
        const angle = Math.atan2(direction.x, direction.z)
        groupRef.current.rotation.y = angle
      }
    }
  })
  
  useEffect(() => {
    const handlePointerUp = () => {
      setIsDragging(false)
    }
    
    window.addEventListener('pointerup', handlePointerUp)
    return () => window.removeEventListener('pointerup', handlePointerUp)
  }, [])
  
  const floatIntensity = status === 'working' ? 0.3 : (isWalking ? 0.05 : 0.1)
  const floatSpeed = status === 'working' ? 4 : (isWalking ? 3 : 1.5)
  
  return (
    <group 
      ref={groupRef} 
      position={startPos}
      onPointerEnter={() => {
        setHovered(true)
        document.body.style.cursor = 'grab'
      }}
      onPointerLeave={() => {
        setHovered(false)
        document.body.style.cursor = 'auto'
      }}
      onPointerDown={(e: any) => {
        e.stopPropagation()
        setIsDragging(true)
        if (agentData) {
          selectAgent(agentData)
        }
      }}
    >
      {/* Chat bubble */}
      {message && (
        <group position={[0, 2.5, 0]}>
          <mesh>
            <planeGeometry args={[Math.min(message.length * 0.15 + 0.5, 3), 0.4]} />
            <meshBasicMaterial color="#333" transparent opacity={0.9} />
          </mesh>
          <Text
            position={[0, 0, 0.01]}
            fontSize={0.12}
            color="#fff"
            anchorX="center"
            anchorY="middle"
            maxWidth={2.8}
          >
            {message}
          </Text>
        </group>
      )}
      
      <Float 
        speed={floatSpeed} 
        rotationIntensity={status === 'working' ? 0.2 : 0.05} 
        floatIntensity={floatIntensity}
      >
        <group>
          <mesh position={[0, 0.6, 0]} castShadow>
            <capsuleGeometry args={[0.25, 0.5, 8, 16]} />
            <MeshDistortMaterial
              color={color}
              emissive={status === 'working' ? color : hovered ? color : '#000'}
              emissiveIntensity={status === 'working' ? 0.2 : hovered ? 0.1 : 0}
              distort={status === 'working' ? 0.15 : 0}
              speed={status === 'working' ? 2 : 0.5}
              roughness={0.4}
              metalness={0.6}
            />
          </mesh>
          
          <mesh position={[0, 1.1, 0]} castShadow>
            <sphereGeometry args={[0.2, 16, 16]} />
            <meshStandardMaterial color={color} roughness={0.3} metalness={0.7} />
          </mesh>
          
          <mesh 
            position={[0, 0.7, -0.2]} 
            rotation={[0.2, 0, isWalking ? Math.sin(Date.now() * 0.01) * 0.1 : 0]} 
            castShadow
          >
            <boxGeometry args={[0.4, 0.8, 0.05]} />
            <meshStandardMaterial color={color} side={THREE.DoubleSide} roughness={0.5} metalness={0.3} />
          </mesh>
          
          <mesh position={[0, 1.5, 0]}>
            <sphereGeometry args={[0.1, 16, 16]} />
            <meshStandardMaterial 
              color={statusColors[status]} 
              emissive={statusColors[status]} 
              emissiveIntensity={0.5}
              toneMapped={false}
            />
          </mesh>
        </group>
      </Float>
      
      <Text
        position={[0, 1.9, 0]}
        fontSize={0.25}
        color={hovered ? '#ffffff' : color}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="#000000"
      >
        {name}
      </Text>
      
      {status === 'working' && agentData?.currentTask && (
        <Text
          position={[0, 2.2, 0]}
          fontSize={0.15}
          color="#ffaa00"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.01}
          outlineColor="#000000"
        >
          ● {agentData.currentTask}
        </Text>
      )}
      
      {isWalking && status === 'idle' && (
        <Text position={[0, 0.1, 0.3]} fontSize={0.1} color="#888888" anchorX="center" anchorY="middle">
          ●
        </Text>
      )}
    </group>
  )
}

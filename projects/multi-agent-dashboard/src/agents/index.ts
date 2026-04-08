export { default as Agent } from './Agent'

export interface AgentType {
  id: string
  name: string
  color: string
  type: 'claude' | 'codex' | 'gemini' | 'qwen' | 'cursor' | 'molty'
  description: string
  capeColor: string
}

export const AVAILABLE_AGENTS: AgentType[] = [
  {
    id: 'claude',
    name: 'Claude',
    color: '#ff4444',
    type: 'claude',
    description: 'Anthropic\'s Claude AI',
    capeColor: '#ff4444'
  },
  {
    id: 'codex',
    name: 'Codex',
    color: '#ffffff',
    type: 'codex',
    description: 'OpenAI Codex',
    capeColor: '#ffffff'
  },
  {
    id: 'gemini',
    name: 'Gemini',
    color: '#9b6bf4',
    type: 'gemini',
    description: 'Google Gemini',
    capeColor: '#9b6bf4'
  },
  {
    id: 'qwen',
    name: 'Qwen',
    color: '#7c3aed',
    type: 'qwen',
    description: 'Alibaba Qwen',
    capeColor: '#7c3aed'
  },
  {
    id: 'cursor',
    name: 'Cursor',
    color: '#6b7280',
    type: 'cursor',
    description: 'Cursor AI Editor',
    capeColor: '#374151'
  },
  {
    id: 'molty',
    name: 'Molty',
    color: '#ef4444',
    type: 'molty',
    description: 'Custom Agent',
    capeColor: '#dc2626'
  }
]

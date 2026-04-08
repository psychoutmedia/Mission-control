// Gateway WebSocket client for multi-agent dashboard

export interface GatewayMessage {
  type: 'status' | 'output' | 'session_list' | 'session_send' | 'error' | 'message'
  payload: any
  sessionKey?: string
  timestamp: string
}

export interface AgentSession {
  sessionKey: string
  label: string
  status: 'active' | 'idle' | 'busy' | 'error'
  lastSeen: string
  channel?: string
}

export interface ChatMessage {
  from: string
  fromLabel: string
  to: string
  message: string
  timestamp: string
}

type GatewayCallback = (message: GatewayMessage) => void

class GatewayClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 2000
  private callbacks: Set<GatewayCallback> = new Set()
  private isConnecting = false
  private messageHandlers: Map<string, (response: any) => void> = new Map()

  constructor(url = 'ws://127.0.0.1:18789') {
    this.url = url
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
        resolve()
        return
      }

      this.isConnecting = true

      try {
        this.ws = new WebSocket(this.url)

        const timeout = setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false
            this.ws?.close()
            reject(new Error('Connection timeout'))
          }
        }, 8000)

        this.ws.onopen = () => {
          clearTimeout(timeout)
          this.isConnecting = false
          this.reconnectAttempts = 0
          console.log('[Gateway] Connected to', this.url)
          this.notify({ type: 'status', payload: { connected: true }, timestamp: new Date().toISOString() })
          resolve()
        }

        this.ws.onclose = () => {
          this.isConnecting = false
          console.log('[Gateway] Disconnected')
          this.notify({ type: 'status', payload: { connected: false }, timestamp: new Date().toISOString() })
          this.attemptReconnect()
        }

        this.ws.onerror = (error) => {
          this.isConnecting = false
          console.error('[Gateway] Error:', error)
          this.notify({ type: 'error', payload: error, timestamp: new Date().toISOString() })
          reject(error)
        }

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            
            // Handle request_id responses
            if (message.requestId && this.messageHandlers.has(message.requestId)) {
              const handler = this.messageHandlers.get(message.requestId)!
              handler(message)
              this.messageHandlers.delete(message.requestId)
              return
            }
            
            this.notify(message)
          } catch (e) {
            // Handle raw messages
            if (event.data === 'ack') {
              this.notify({ type: 'status', payload: { connected: true }, timestamp: new Date().toISOString() })
            }
          }
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  private generateRequestId(): string {
    return `req-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[Gateway] Max reconnect attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`[Gateway] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      this.connect().catch(() => {})
    }, this.reconnectDelay)
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe(callback: GatewayCallback) {
    this.callbacks.add(callback)
    return () => this.callbacks.delete(callback)
  }

  private notify(message: GatewayMessage) {
    this.callbacks.forEach(cb => cb(message))
  }

  // Send raw command and wait for response
  send(command: any, timeoutMs = 5000): Promise<any> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState !== WebSocket.OPEN) {
        reject(new Error('Not connected'))
        return
      }

      const requestId = this.generateRequestId()
      const wrappedCommand = { ...command, requestId }
      
      const timeout = setTimeout(() => {
        this.messageHandlers.delete(requestId)
        reject(new Error('Request timeout'))
      }, timeoutMs)

      this.messageHandlers.set(requestId, (response) => {
        clearTimeout(timeout)
        resolve(response)
      })

      this.ws.send(JSON.stringify(wrappedCommand))
    })
  }

  // Register a session
  async register(label: string, type = 'dashboard'): Promise<string> {
    try {
      const response = await this.send({
        action: 'session_register',
        label,
        type
      })
      return response.sessionKey || response.payload?.sessionKey || label
    } catch (e) {
      console.warn('[Gateway] Register failed, using local key:', e)
      return `${type}-${Date.now()}`
    }
  }

  // Get list of all sessions
  async getSessions(): Promise<AgentSession[]> {
    try {
      const response = await this.send({ action: 'session_list' })
      return response.payload?.sessions || response.sessions || []
    } catch (e) {
      console.warn('[Gateway] getSessions failed:', e)
      return []
    }
  }

  // Send a message to another session
  async sendMessage(toSessionKey: string, message: string, fromLabel: string): Promise<void> {
    try {
      await this.send({
        action: 'session_send',
        to: toSessionKey,
        message,
        from: fromLabel
      })
    } catch (e) {
      console.warn('[Gateway] sendMessage failed:', e)
      throw e
    }
  }

  // Broadcast a message to all sessions
  async broadcast(message: string, fromLabel: string): Promise<void> {
    try {
      await this.send({
        action: 'broadcast',
        message,
        from: fromLabel
      })
    } catch (e) {
      console.warn('[Gateway] broadcast failed:', e)
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Singleton
let gatewayInstance: GatewayClient | null = null

export function getGateway(url?: string): GatewayClient {
  if (!gatewayInstance) {
    gatewayInstance = new GatewayClient(url)
  }
  return gatewayInstance
}

export function resetGateway() {
  if (gatewayInstance) {
    gatewayInstance.disconnect()
    gatewayInstance = null
  }
}

export default GatewayClient

/// <reference types="vite/client" />

declare module '*.tsx' {
  import React from 'react'
  const Component: React.ComponentType
  export default Component
}

declare module '*.ts' {
  const content: any
  export default content
}

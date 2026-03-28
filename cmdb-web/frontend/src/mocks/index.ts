export async function initMocks() {
  if (typeof window === 'undefined') {
    // 在 Node.js 环境中（如 Playwright 测试）
    const { server } = await import('../../mock/server')
    server.listen()
  } else {
    // 在浏览器环境中
    const { worker } = await import('./browser')
    worker.start({
      onUnhandledRequest: 'bypass',
    })
  }
}

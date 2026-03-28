// global-setup.ts - 空的全局设置文件，用于避免 MSW 在 Node.js 环境中的兼容性问题
// MSW server 现在在每个测试文件中通过 fixtures 启动

export default async function globalSetup() {
  console.log('Global setup initialized')
  // 不再在这里启动 MSW server，避免与 Firefox 的兼容性问题
}

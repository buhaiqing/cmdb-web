#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const reportPath = join(__dirname, '../tests/e2e/playwright-report/index.html')
const junitPath = join(__dirname, '../tests/e2e/playwright-report/junit.xml')

console.log('='.repeat(60))
console.log('E2E 测试执行分析报告')
console.log('='.repeat(60))
console.log()

// 读取 JUnit XML 报告
try {
  const junitContent = readFileSync(junitPath, 'utf-8')
  
  // 解析测试结果
  const testsuitesMatch = junitContent.match(/<testsuites[^>]*>/)
  const testsMatch = junitContent.match(/tests="(\d+)"/)
  const failuresMatch = junitContent.match(/failures="(\d+)"/)
  const skippedMatch = junitContent.match(/skipped="(\d+)"/)
  const timeMatch = junitContent.match(/time="([\d.]+)"/)
  
  const totalTests = testsMatch ? parseInt(testsMatch[1]) : 0
  const totalFailures = failuresMatch ? parseInt(failuresMatch[1]) : 0
  const totalSkipped = skippedMatch ? parseInt(skippedMatch[1]) : 0
  const totalTime = timeMatch ? parseFloat(timeMatch[1]) : 0
  const totalPassed = totalTests - totalFailures - totalSkipped
  
  console.log('📊 测试执行概览')
  console.log('-'.repeat(60))
  console.log(`总测试数：    ${totalTests}`)
  console.log(`✅ 通过：      ${totalPassed} (${((totalPassed/totalTests)*100).toFixed(1)}%)`)
  console.log(`❌ 失败：      ${totalFailures} (${((totalFailures/totalTests)*100).toFixed(1)}%)`)
  console.log(`⏭️  跳过：      ${totalSkipped}`)
  console.log(`⏱️  执行时间：  ${totalTime.toFixed(2)}秒`)
  console.log()
  
  // 解析失败的测试
  const testcases = junitContent.match(/<testcase[^>]*>[\s\S]*?<\/testcase>/g) || []
  const failedTests = []
  
  testcases.forEach(testcase => {
    if (testcase.includes('<failure')) {
      const nameMatch = testcase.match(/name="([^"]+)"/)
      const classnameMatch = testcase.match(/classname="([^"]+)"/)
      const failureMatch = testcase.match(/<failure[^>]*>([\s\S]*?)<\/failure>/)
      
      if (nameMatch && classnameMatch) {
        failedTests.push({
          name: nameMatch[1],
          classname: classnameMatch[1],
          message: failureMatch ? failureMatch[1].trim() : '未知错误'
        })
      }
    }
  })
  
  if (failedTests.length > 0) {
    console.log('❌ 失败测试详情')
    console.log('-'.repeat(60))
    failedTests.forEach((test, index) => {
      console.log(`${index + 1}. ${test.name}`)
      console.log(`   类别：${test.classname}`)
      console.log(`   错误：${test.message.substring(0, 100)}...`)
      console.log()
    })
  }
  
  // 按模块统计
  console.log('📁 按模块统计')
  console.log('-'.repeat(60))
  const moduleStats = {}
  testcases.forEach(testcase => {
    const classnameMatch = testcase.match(/classname="([^"]+)"/)
    if (classnameMatch) {
      const module = classnameMatch[1].split('.').pop() || 'unknown'
      if (!moduleStats[module]) {
        moduleStats[
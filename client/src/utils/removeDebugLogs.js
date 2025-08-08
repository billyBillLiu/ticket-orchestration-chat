#!/usr/bin/env node

/**
 * Utility script to remove debug console logs from the codebase
 * Run this when you're ready to clean up the debug logging
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Patterns to match debug console logs
const debugPatterns = [
  /console\.log\(['"`]🔍.*?['"`].*?\);/g,
  /console\.log\(['"`]🔄.*?['"`].*?\);/g,
  /console\.log\(['"`]🔧.*?['"`].*?\);/g,
  /console\.log\(['"`]✅.*?['"`].*?\);/g,
  /console\.log\(['"`]❌.*?['"`].*?\);/g,
  /console\.log\(['"`]🚪.*?['"`].*?\);/g,
  /console\.log\(['"`]⏰.*?['"`].*?\);/g,
  /console\.log\(['"`]🚀.*?['"`].*?\);/g,
  /console\.log\(['"`]📦.*?['"`].*?\);/g,
  /console\.log\(['"`]⏳.*?['"`].*?\);/g,
];

function removeDebugLogs(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  
  debugPatterns.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) {
      console.log(`Removing debug logs from ${filePath}:`, matches.length, 'matches');
      content = content.replace(pattern, '');
      modified = true;
    }
  });
  
  if (modified) {
    fs.writeFileSync(filePath, content);
    console.log(`✅ Updated ${filePath}`);
  }
}

// Find all TypeScript/JavaScript files
const files = glob.sync('client/src/**/*.{ts,tsx,js,jsx}');
files.forEach(removeDebugLogs);

console.log('🎉 Debug logs removal complete!'); 
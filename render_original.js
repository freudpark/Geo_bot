
const nodeHtmlToImage = require('node-html-to-image')
const fs = require('fs')

const html = fs.readFileSync('original_glass.html', 'utf8')

nodeHtmlToImage({
  output: './original_glass_card.png',
  html: html,
  puppeteerArgs: {
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  }
}).then(() => console.log('Original Glass Card created!'))

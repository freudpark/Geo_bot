
const nodeHtmlToImage = require('node-html-to-image')
const fs = require('fs')

const html = fs.readFileSync('final_ko_glass.html', 'utf8')

nodeHtmlToImage({
  output: './final_ko_glass_card.png',
  html: html,
  puppeteerArgs: {
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  }
}).then(() => console.log('Final KO Glass Card created!'))

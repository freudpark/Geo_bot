
const nodeHtmlToImage = require('node-html-to-image')
const fs = require('fs')

const html = fs.readFileSync('temp_3d.html', 'utf8')

nodeHtmlToImage({
  output: './alert_card_3d.png',
  html: html,
  transparent: true,
  puppeteerArgs: {
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--force-device-scale-factor=2'] 
  }
}).then(() => console.log('3D Image created successfully!'))

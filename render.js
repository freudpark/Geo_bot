
const nodeHtmlToImage = require('node-html-to-image')
const fs = require('fs')

const html = fs.readFileSync('temp.html', 'utf8')

nodeHtmlToImage({
  output: './alert_card_sample.png',
  html: html
}).then(() => console.log('The image was created successfully!'))

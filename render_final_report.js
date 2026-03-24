
    const nodeHtmlToImage = require('node-html-to-image')
    const fs = require('fs')
    const html = fs.readFileSync('final_report.html', 'utf8')
    nodeHtmlToImage({
      output: './final_report_card.png',
      html: html,
      puppeteerArgs: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
    }).then(() => console.log('Final Report Card created!'))
    
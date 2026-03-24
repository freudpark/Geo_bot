
        const nodeHtmlToImage = require('node-html-to-image')
        const fs = require('fs')
        const html = fs.readFileSync('alert_card.html', 'utf8')
        nodeHtmlToImage({
          output: 'alert_card_final.png',
          html: html,
          puppeteerArgs: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
        }).then(() => console.log('Report Card Image Generated.'))
        

                const nodeHtmlToImage = require('node-html-to-image');
                const fs = require('fs');
                nodeHtmlToImage({
                  output: 'alert_card_final.png',
                  html: fs.readFileSync('alert_card.html', 'utf8'),
                  puppeteerArgs: { args: ['--no-sandbox'] }
                }).then(() => console.log('Done'));
                
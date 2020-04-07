var synthetics = require('Synthetics');
const log = require('SyntheticsLogger');
const fs = require('fs');

//async function used to grab urls from page
//fetch hrefs from DOM
const grabURLs = async function(page) {
    const urls = await page.evaluate(() => {
        const urlsElements = document.getElementsByTagName('a');
        let urls = new Set();
        for(i in urlsElements) {
            url = String(urlsElements[i].href).trim();
            if(url != null && url.length > 0 && (url.startsWith('http') || url.startsWith('https'))) {
                urls.add(url);
            }
        }
        return [...urls];
    });
    return urls;
}

const webCrawlerBlueprint = async function () {
    // INSERT URL here
    let urls = ["https://www.amazon.com/"];

    //set contains the explored urls
    const explored = new Set(urls);

    let page = await synthetics.getPage();

    //maximum number of links that would be followed
    const limit = 10;

    let count = 0;

    while(count < limit && urls.length > 0) {
        let nav_url = urls.shift();

        log.info("Trying to open page with url " + nav_url);

        let response;

        try {
            response = await page.goto(nav_url, {waitUntil: ['load', 'networkidle0'], timeout: 30000});
            if(!response) {
                throw "Failed to get network response";
            }
        } catch(ex) {
            synthetics.addExecutionError('Unable open page with url ' + nav_url, ex);
            throw ex;
        }

        //response.ok() only whitelists status codes in the range 200-299
        //please update the condition here if necessary
        //example: response.status() >= 200 && response.status() < 400
        if(!response.ok()) {
            log.info("current count is " + (++count));
            log.info("failed to request " + response.url());
            try {
                await synthetics.takeScreenshot('load', 'failed');
            } catch(ex) {
                synthetics.addExecutionError('Unable to capture screenshot.', ex);
            }
            throw("failed to request " + response.url());
        } else {
            log.info("current count is " + (++count));
            log.info(response.url() + " is alive");
            try {
                await synthetics.takeScreenshot('load', 'Succeeded');
            } catch(ex) {
                synthetics.addExecutionError('Unable to capture screenshot.', ex);
            }
        }

        try {
            let nextURL = await grabURLs(page);

            nextURL.forEach(element => {
                if(!explored.has(element)) {
                    urls.push(element);
                    explored.add(element);
                }
            });
        } catch(ex) {
            synthetics.addExecutionError('Unable to grab urls on page ' + response.url(), ex);
        }

        //Broken link checker blueprint just uses one page to test availability of several urls
        //Reset the page in-between to force a network event in case of a single page app
        try {
            await page.goto('about:blank',{waitUntil: ['load', 'networkidle0'], timeout: 30000} );
        } catch(ex) {
            synthetics.addExecutionError('Unable to open a blank page ', ex);
        }

    }
};

exports.handler = async () => {
    return await webCrawlerBlueprint();
};

// INSERT `dynatrace-canary-exporter.js` HERE

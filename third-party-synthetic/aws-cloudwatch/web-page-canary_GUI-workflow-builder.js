var synthetics = require('Synthetics');
const log = require('SyntheticsLogger');

const flowBuilderBlueprint = async function () {
    // INSERT URL here
    let url = "https://www.dynatrace.com/";

    let page = await synthetics.getPage();

    // Navigate to the initial url
    await synthetics.executeStep('navigateToUrl', async function (timeoutInMillis = 30000) {
        await page.goto(url, {waitUntil: ['load', 'networkidle0'], timeout: timeoutInMillis});
    });

    // Execute customer steps
    await synthetics.executeStep('customerActions', async function () {
        await Promise.all([
          page.waitForNavigation({ timeout: 30000 }),
          await page.click("nav [href='/trial/']")
        ]);
        try {
            await synthetics.takeScreenshot("redirection", 'result');
        } catch(ex) {
            synthetics.addExecutionError('Unable to capture screenshot.', ex);
        }


    });
};

exports.handler = async () => {
    return await flowBuilderBlueprint();
};

// INSERT `web-page-canary_dt-exporter.js` HERE
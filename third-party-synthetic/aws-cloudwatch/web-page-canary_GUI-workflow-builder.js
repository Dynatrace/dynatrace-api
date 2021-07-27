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
    await synthetics.executeStep('click free trial', async function (timeoutInMillis = 30000) {
        const freeTrial = 'Free trial';
        const links = await page.$x("//a[contains(., '" + freeTrial + "')]");

        if (links.length == 0) {
           log.info(`'${freeTrial}' link not found`);
        }
        const link = links[0];
        await Promise.all([
           page.waitForNavigation({ timeout: 30000 }),
           page.evaluate(el => el.click(), link)
        ]);
    });
};

exports.handler = async () => {
    return await flowBuilderBlueprint();
};

// INSERT `dynatrace-canary-exporter.js` HERE

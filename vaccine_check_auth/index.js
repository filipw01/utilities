const chromium = require('chrome-aws-lambda');
const AWS = require('aws-sdk');
require('dotenv').config()

AWS.config.update({
    region: 'eu-central-1'
})

const {USERNAME, PASSWORD, USER_ID} = process.env

const docClient = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context, callback) => {
    let browser;
    let result;

    try {
        browser = await chromium.puppeteer.launch({
            args: chromium.args,
            defaultViewport: chromium.defaultViewport,
            executablePath: await chromium.executablePath,
            headless: chromium.headless,
            ignoreHTTPSErrors: true,
        });
        const page = await browser.newPage();
        await page.goto('https://pacjent.erejestracja.ezdrowie.gov.pl/')
        await page.waitForSelector('.jOjgbJ')
        await page.click('.jOjgbJ')
        await page.waitForSelector('.margin-sides-zero > div')
        await page.click('.margin-sides-zero > div')
        await page.waitForSelector('#loginForm\\:login')
        await page.type('#loginForm\\:login', USERNAME)
        await page.type('#loginForm\\:hasło', PASSWORD)
        await page.setRequestInterception(true);
        let csrfToken = null
        page.on('request', request => {
            if (!csrfToken && request.url() === `https://pacjent.erejestracja.ezdrowie.gov.pl/api/patient/${USER_ID}`) {
                csrfToken = request.headers()['x-csrf-token']
            }
            request.continue()
        });
        await page.waitForSelector('#loginForm\\:loginButton')
        await page.click('#loginForm\\:loginButton')
        await page.waitForSelector('.hwdWZj')

        const sessionId = (await page.cookies())[0].value
        const SECONDS_IN_12_HOURS = 60 * 60 * 12
        docClient.put({
            TableName: 'vaccineCheck',
            Item: {
                ttl: Math.floor(Date.now() / 1000) + SECONDS_IN_12_HOURS,
                csrfToken,
                sessionId,
            }
        }, function (err, data) {
            if (err) {
                throw new Error(`Unable to add item. Error JSON: ${JSON.stringify(err, null, 2)}`);
            } else {
                result = "Added item"
                console.log("Added item:", JSON.stringify(data, null, 2));
            }
        })
    } catch (error) {
        return callback(error);
    } finally {
        if (browser !== null) {
            await browser.close();
        }
    }

    return callback(null, result);
}


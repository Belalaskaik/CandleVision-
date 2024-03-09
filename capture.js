const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();

  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8000/beginner', { waitUntil: 'networkidle2', timeout: 60000 }); // Timeout set to 60 seconds

  // Customize the selector to match the TradingView chart you want to capture
  const chartSelector = '.tradingview-widget-container';

  // Wait for the chart to load
  await page.waitForSelector(chartSelector);

  // Take screenshot of the chart element
  const chart = await page.$(chartSelector);
  await chart.screenshot({path: './static/screenshots/screenshot.png'});

  await browser.close();
})();

const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Set a higher resolution for the viewport
  await page.setViewport({ width: 3840, height: 2160, deviceScaleFactor: 1.5 }); // Increase deviceScaleFactor to zoom in

  await page.goto('https://fastapi-app-04xj.onrender.com', { waitUntil: 'networkidle2', timeout: 60000 });

  const chartSelector = '.tradingview-widget-container1';
  await page.waitForSelector(chartSelector);

  const chart = await page.$(chartSelector);
  await chart.screenshot({path: './static/screenshots/screenshot.png'});

  await browser.close();
})(); 

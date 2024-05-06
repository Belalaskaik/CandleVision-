// document.addEventListener('DOMContentLoaded', function() {
//     new TradingView.widget({
//       "container_id": "tradingview_9d2b5",
//       "autosize": false,  // Since you're specifying dimensions
//       "width": 1000,      // Fixed width as desired
//       "height": 500,      // Fixed height as desired
//       "symbol": "NASDAQ:AAPL",
//       "interval": "D",
//       "timezone": "Etc/UTC",
//       "theme": "light",
//       "style": "1",
//       "toolbar_bg": "#f1f3f6",
//       "withdateranges": true,
//       "allow_symbol_change": true,
//       "save_image": false,
//       "hide_volume": true,  // This will hide the volume on the chart
//       "show_popup_button": true,
//       "popup_width": "1000",
//       "popup_height": "650"
//     });
//   });

  document.getElementById('detectButton').addEventListener('click', async function() {
    try {
      // Take Screenshot
      let screenshotResponse = await fetch("/screenshot");
      let screenshotData = await screenshotResponse.json();
      if (screenshotData.message !== "Screenshot taken successfully") {
        throw new Error('Screenshot capture failed.');
      }

      // Crop Screenshot
      const filename = "screenshot.png";
      let cropResponse = await fetch(`/crop-screenshot/${filename}`, { method: 'POST' });
      let cropData = await cropResponse.json();
      // Detect objects
      let detectResponse = await fetch('/detect/', { method: 'POST' });
      let detectData = await detectResponse.json();
      if (detectResponse.ok && detectData.image) {
        document.getElementById('screenshotDisplay').src = `data:image/jpeg;base64,${detectData.image}`;

        if (detectData.patterns && detectData.patterns.length > 0) {
          // Join all detected patterns into a single string
          let detectedPatternName = detectData.patterns.join(', ');
          console.log(detectedPatternName)

          // Call the send-sms endpoint if detections were made
          let smsResponse = await fetch('/send-sms/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
              detected_pattern_name: detectedPatternName
            })
          });

          if (!smsResponse.ok) {
            const errorData = await smsResponse.json();
            console.error('SMS Notification Error:', errorData);
            throw new Error('SMS notification failed: ' + JSON.stringify(errorData));
          }

          const responseData = await smsResponse.json();
          console.log('SMS Response:', responseData);
          alert(`SMS sent! Message SID: ${responseData.sid}`);
        } else {
          console.log("No patterns detected.");
        }
      } else {
        throw new Error('Detection failed: ' + detectData.detail);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error: ' + error.message);
    }
  });



function fetchStockData(companyName) {
  const searchUrl = `/api/stock/search/${companyName}`;

  fetch(searchUrl)
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          displayErrorMessage(data.error);
          return;
      }
      fetchStockPriceChange(data.symbol);
  })
  .catch(error => {
      console.error('Error:', error);
      displayErrorMessage('Network error, please try again later.');
  });
}


async function checkStockTrend(symbol) {
  try {
    const response = await fetch(`/api/stock/${symbol}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Failed to fetch stock data");

    const dollar = document.getElementById("dollar");
    const ropeContainer = document.querySelector(".rope-container");
    const bearPosition = ropeContainer.offsetWidth - document.querySelector('.bear').offsetWidth;
    const bullPosition = document.querySelector('.bull').offsetWidth;

    if (data.trend === "bullish") {
      // Move towards the bull, stop at bull's right edge
      let targetPosition = bullPosition;
      dollar.style.transform = `translateX(${targetPosition - ropeContainer.offsetWidth / 2}px)`;
    } else if (data.trend === "bearish") {
      // Move towards the bear, stop at bear's left edge
      let targetPosition = bearPosition;
      dollar.style.transform = `translateX(${targetPosition - ropeContainer.offsetWidth / 2}px)`;
    } else {
      // Stay in the middle if neutral
      dollar.style.transform = "translateX(0px)";
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error: ' + error.message);
  }
}

function updateWidget(interval) {
  // Locate the container where the TradingView widget is to be embedded
  const container = document.getElementById('tradingview-widget');
  
  // Clear the container to remove the previous widget instance
  container.innerHTML = '';

  // Create a new script element for the TradingView widget
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.async = true;
  script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';

  // Create a configuration object with all required properties
  const config = {
      "width": 800,
      "height": 600,
      "symbol": "AMEX:SPY",
      "interval": interval, // Set interval dynamically based on user selection
      "timezone": "Etc/UTC",
      "theme": "light",
      "style": "1",
      "locale": "en",
      "hide_top_toolbar": false,
      "enable_publishing": false,
      "allow_symbol_change": false,
      "save_image": true,
      "calendar": false,
      "hide_volume": true,
      "container_id": "tradingview-widget",
      "support_host": "https://www.tradingview.com"
  };

  // Append configuration data as JSON within the script
  script.innerHTML = JSON.stringify(config);

  // Append the newly created script to the container
  container.appendChild(script);
}

// Call this function to initially load the widget with a default interval
updateWidget('H');  // Set default interval as 5 minutes

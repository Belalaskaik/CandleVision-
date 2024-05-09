import requests

def capture_element_screenshot(url, css_selector, api_key, output_file):
    """
    Captures a screenshot of a specific element on a webpage using the ApiFlash API.

    Args:
    url (str): The URL of the webpage to capture.
    css_selector (str): The CSS selector of the element to capture.
    api_key (str): Your ApiFlash API key.
    output_file (str): The path to save the output image file.
    """
    params = {
        'access_key': API_KEY,
        'url': url,
        'element': css_selector,
        'response_type': 'image',
        'format': 'jpeg'  # You can choose png, jpeg, etc.
    }
    
    response = requests.get("https://api.apiflash.com/v1/urltoimage", params=params)
    
    if response.status_code == 200:
        # Write the image content to an output file
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print("Screenshot saved to", output_file)
    else:
        print("Failed to capture screenshot:", response.status_code, response.text)

# Usage example
if __name__ == "__main__":
    # Replace 'your_api_key_here' with your actual ApiFlash API key
    API_KEY = 'af7837dbba2f473d9c8aa5b62ec673c0'
    URL = 'https://fastapi-app-04xj.onrender.com/'
    CSS_SELECTOR = '#tradingview-widget'  # Adjust this to your target element
    OUTPUT_FILE = 'element_screenshot.png'

    capture_element_screenshot(URL, CSS_SELECTOR, API_KEY, OUTPUT_FILE)

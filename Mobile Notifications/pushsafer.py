import http.client
import urllib.parse

def send_pushsafer_notification(private_key, message, title, icon, sound, vibration, picture):
    """
    Sends a notification using the Pushsafer service.

    Parameters:
    private_key (str): Your Pushsafer private or alias key.
    message (str): The message text to be sent.
    title (str): The title of the message.
    icon (str): The icon number (1-98).
    sound (str): The sound number (0-28).
    vibration (str): The vibration number (0-3).
    picture (str): The picture data URL with Base64-encoded string.

    Returns:
    None
    """
    # Establish a secure HTTPS connection to Pushsafer
    conn = http.client.HTTPSConnection("pushsafer.com:443")
    
    # Prepare the payload with the notification parameters
    payload = urllib.parse.urlencode({
        "k": private_key,                # Your Private or Alias Key
        "m": message,                    # Message Text
        "t": title,                      # Title of message
        "i": icon,                       # Icon number 1-98
        "s": sound,                      # Sound number 0-28
        "v": vibration,                  # Vibration number 0-3
        "p": picture,                    # Picture Data URL with Base64-encoded string
    })
    
    # Send the POST request to the Pushsafer API
    conn.request("POST", "/api", payload, { "Content-type": "application/x-www-form-urlencoded" })
    
    # Get the response from the server
    response = conn.getresponse()
    
    # Print the status and reason of the response
    print(response.status, response.reason)
    
    # Read and print the response data
    data = response.read()
    print(data)

# Example usage:
if __name__ == "__main__":
    send_pushsafer_notification(
        private_key="UGjIlhTTfcfjwmK6XJWM",  # Replace with your actual private key
        message="Test message",              # The message text
        title="Test title",                  # The title of the message
        icon="1",                            # The icon number
        sound="1",                           # The sound number
        vibration="1",                       # The vibration number
        picture=""                           # The picture data URL (optional)
    )
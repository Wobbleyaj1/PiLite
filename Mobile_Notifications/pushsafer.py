import http.client
import urllib.parse
import time

class PushsaferNotification:
    def __init__(self, private_key):
        """
        Initializes the PushsaferNotification class with the provided private key.

        Parameters:
        private_key (str): Your Pushsafer private or alias key.
        """
        self.private_key = private_key
        self.last_notification_time = 0  # Initialize the last notification time

    def send_notification(self, message, title, icon, sound, vibration, picture):
        """
        Sends a notification using the Pushsafer service.

        Parameters:
        message (str): The message text to be sent.
        title (str): The title of the message.
        icon (str): The icon number (1-98).
        sound (str): The sound number (0-28).
        vibration (str): The vibration number (0-3).
        picture (str): The picture data URL with Base64-encoded string.

        Returns:
        None
        """
        current_time = time.time()
        if current_time - self.last_notification_time >= 5:
            # Establish a secure HTTPS connection to Pushsafer
            conn = http.client.HTTPSConnection("pushsafer.com:443")
            
            # Prepare the payload with the notification parameters
            payload = urllib.parse.urlencode({
                "k": self.private_key,         # Your Private or Alias Key
                "m": message,                  # Message Text
                "t": title,                    # Title of message
                "i": icon,                     # Icon number 1-98
                "s": sound,                    # Sound number 0-28
                "v": vibration,                # Vibration number 0-3
                "p": picture,                  # Picture Data URL with Base64-encoded string
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
            
            # Update the last notification time
            self.last_notification_time = current_time
        else:
            print("Notification not sent due to delay")

# Example usage:
if __name__ == "__main__":
    notifier = PushsaferNotification(private_key='Private Key')  # Replace with your actual private key
    notifier.send_notification(
        message="You Left Your Lights On",  # The message text
        title="PiLite",                     # The title of the message
        icon="24",                          # The icon number
        sound="10",                         # The sound number
        vibration="1",                      # The vibration number
        picture=""                          # The picture data URL (optional)
    )
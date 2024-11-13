import json
from datetime import datetime
import pytz 

UTC = pytz.utc 

def main():
    pass

def unserialize_http(response: dict) -> bytes:
    """
    Unserializes an HTTP response from a dictionary.

    Args:
        response: A dictionary containing:
            * response_code: The HTTP status code (e.g., 200, 400).
            * body: The body of the HTTP response (text or binary).
            * headers (optional): Additional HTTP headers.
            * cookies (optional): cookies to set. list of tuples (key, value, exp)

    Returns:
        The HTTP response as bytes.

    Raises:
        ValueError: If the input dictionary is missing required keys.
    """
    
    http_headers = f"HTTP/1.1 {response['response_code']}\r\n"
    if "headers" in response.keys():
        for key, value in response["headers"].items():
            http_headers += f"{key}: {value}\r\n"
    
    if "cookies" in response.keys():
        for cookie in response["cookies"]:
            expiration_date = datetime.strptime(cookie[2], "%Y-%m-%d %H:%M:%S")
            formatted_expiration = expiration_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
            http_headers += f"Set-Cookie: {cookie[0]}={cookie[1]};expires={formatted_expiration};path=/\r\n"
    
    http_headers += f"Date: {datetime.now(UTC).strftime('%Y:%m:%d %H:%M:%S %Z %z')}\r\n"
    http_headers += f"Content-Length: {len(response['body'])}\r\n\r\n"

    http_response = http_headers.encode('utf-8')

    if isinstance(response['body'], str):
        http_response += response['body'].encode('utf-8')
    else:
        http_response += response['body']
    
    return http_response


if __name__ == "__main__":
    main()
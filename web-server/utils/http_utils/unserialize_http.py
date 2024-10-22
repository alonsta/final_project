import json
import datetime
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

    Returns:
        The HTTP response as bytes.

    Raises:
        ValueError: If the input dictionary is missing required keys.
    """
    
    http_headers = f"HTTP/1.1 {response['response_code']}\r\n"
    
    for key, value in response["headers"].items():
        http_headers += f"{key}: {value}\r\n"
    
    http_headers += f"Date: {datetime.datetime.now(UTC).strftime('%Y:%m:%d %H:%M:%S %Z %z')}\r\n"
    http_headers += f"Content-Length: {len(response['body'])}\r\n\r\n"

    http_response = http_headers.encode('utf-8')

    if isinstance(response['body'], str):
        http_response += response['body'].encode('utf-8')
    else:
        http_response += response['body']
    
    return http_response


if __name__ == "__main__":
    main()
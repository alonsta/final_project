import json
import datetime
import pytz 

UTC = pytz.utc 

def main():
    pass

def unserialize_http(dict: json) -> str:
    """
    Unserializes an HTTP response from a dictionary.

    Args:
        dict: A dictionary containing:
            * response_code: The HTTP status code (e.g., 200).
            * body: The body of the HTTP response.
            * headers (optional): Additional HTTP headers.

    Returns:
        The HTTP response as a string.

    Raises:
        ValueError: If the input dictionary is missing required keys.
    """

    http_string = f"HTTP/1.1 {dict['response_code']}\r\n"
    for key, value in dict["headers"].items():
        http_string += f"{key}: {value}\r\n"
    http_string += f"Date: {datetime.datetime.now(UTC).strftime('%Y:%m:%d %H:%M:%S %Z %z')}\r\n"
    http_string += f"Content-Length: {len(dict['body'].encode())}\r\n\r\n"
    http_string += dict["body"]
    
    return http_string



if __name__ == "__main__":
    main()
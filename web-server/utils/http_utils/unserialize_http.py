import json
import datetime
import pytz 

UTC = pytz.utc 

def main():
    pass

def unserialize_http(dict: json) -> str:
    """
    Args: dict with response_code, body, and any extra headers in a dict called headers.
    
    Returns: http response in str format.
    
    no need for Content-length and Date headers.
    """
    http_string = f"HTTP/1.1 {dict["response_code"]}\r\n"
    for key, value in dict["headers"].items():
        http_string += f"{key}: {value}\r\n"
    http_string += f"Date: {datetime.datetime.now(UTC).strftime('%Y:%m:%d %H:%M:%S %Z %z')}\r\n"
    http_string += f"Content-Length: {len(dict["body"].encode())}\r\n\r\n"
    http_string += dict["body"]
    
    return http_string



if __name__ == "__main__":
    main()
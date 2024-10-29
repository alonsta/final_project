import json

def main():
    pass

def signup(info, response):
    print(info, response)
    if True:
        response["body"] = json.dumps({"success": "yup. its true"})
        response["response_code"] = "200 OK"
    return response

if __name__ == "__main__":
    main()
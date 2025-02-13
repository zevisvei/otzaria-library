import requests


BASE_URL = "https://www.call2all.co.il/ym/api/"


def send_to_yemot(content: str, token: str, path: str):
    url = f"{BASE_URL}UploadTextFile"
    data = {
        "token": token,
        "what": f"{path}/{get_file_num(token, path) + 1}.tts",
        "contents": content
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        send_tzintuk(token, "upadtes")
    return response.status_code


def get_file_num(token: str, path: str) -> int:
    url = f"{BASE_URL}GetIVR2DirStats"
    data = {
        "token": token,
        "path": path
    }
    response = requests.get(url, params=data).json()
    max_file = response["maxFile"]["name"]
    return int(max_file.split(".")[0])


def send_tzintuk(token: str, list_name: str):
    url = f"{BASE_URL}RunTzintuk"
    data = {
        "token": token,
        "phones": f"tzl:{list_name}"
    }
    response = requests.get(url, params=data)
    return response.status_code

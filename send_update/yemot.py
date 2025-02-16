import requests


BASE_URL = "https://www.call2all.co.il/ym/api/"


def split_content(content: str) -> list[str]:
    all_partes = []
    start = 0
    chunk_size = 2000
    while start < len(content):
        all_partes.append(content[start:start + chunk_size])
        start += chunk_size
    return all_partes


def send_to_yemot(content: str, token: str, path: str, tzintuk_list_name: str) -> int:
    url = f"{BASE_URL}UploadTextFile"
    num = get_file_num(token, path)
    all_partes = split_content(content)
    for chunk in all_partes[-1::-1]:
        num += 1
        file_name = str(num).zfill(3)
        data = {
            "token": token,
            "what": f"{path}/{file_name}.tts",
            "contents": chunk
        }
        response = requests.post(url, data=data)
    if response.status_code == 200:
        send_tzintuk(token, tzintuk_list_name)
    return response.status_code


def get_file_num(token: str, path: str) -> int:
    url = f"{BASE_URL}GetIVR2DirStats"
    data = {
        "token": token,
        "path": path
    }
    response = requests.get(url, params=data).json()
    try:
        max_file = response["maxFile"]["name"]
        return int(max_file.split(".")[0])
    except:
        return -1


def send_tzintuk(token: str, list_name: str) -> int:
    url = f"{BASE_URL}RunTzintuk"
    data = {
        "token": token,
        "phones": f"tzl:{list_name}"
    }
    response = requests.get(url, params=data)
    return response.status_code

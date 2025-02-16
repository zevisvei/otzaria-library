import requests


BASE_URL = "https://www.call2all.co.il/ym/api/"


def split_content(content: str) -> list[str]:
    all_partes = []
    start = 0
    chunk_size = 2000
    while len(content) - start > chunk_size:
        part = content[start:content.rfind(" ", start, start + chunk_size)]
        all_partes.append(part.strip())
        start += len(part)
    all_partes.append(content[start:].strip())
    return all_partes


def split_and_send(content: dict, date_yemot: str, token: str, path: str, tzintuk_list_name: str):
    num = get_file_num(token, path)
    for key, value in content.items():
        all_partes = split_content(value)
        for chunk in all_partes[-1::-1]:
            num += 1
            file_name = str(num).zfill(3)
            send_to_yemot(chunk, token, path, file_name)
        send_to_yemot(key, token, path, f"{file_name}-Title")
    send_to_yemot(date_yemot, token, path, str(num + 1).zfill(3))
    send_tzintuk(token, tzintuk_list_name)


def send_to_yemot(content: str, token: str, path: str, file_name: str) -> int:
    url = f"{BASE_URL}UploadTextFile"
    data = {
        "token": token,
        "what": f"{path}/{file_name}.tts",
        "contents": content
    }
    response = requests.post(url, data=data)
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

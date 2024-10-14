import asyncio
import json

from aiohttp import ClientSession

from data_class.data_request import GetResponseModel

# class DictResultRequest(TypedDict):
#     name_uspd: str
#     host: str
#     status_connect: bool
#     status_conf: bool
#     result: str | list
#     error: list
#     command: str
#     api: str
#     time_uspd_utc: str
#     statr_ver_fw: str


# class DictGetResponse(TypedDict):
#     status: bool
#     data: str
#     error: list


class BaseRequest:
    def __init__(self, session: ClientSession, host: str, login_in: str, pass_in: str):
        self.session = session
        self.host = host
        self.login_in = login_in
        self.pass_in = pass_in

    @staticmethod
    def create_heders() -> dict:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9',
        }
        return headers

    @staticmethod
    def create_heders_with_auth(accessToken: str, content_type: str = 'application/json') -> dict:
        headers = {
            'Content-Type': content_type,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Authorization': f'Bearer {accessToken}',
        }
        return headers

    @staticmethod
    def create_heders_with_auth_waviot(content_type: str = 'application/json') -> dict:
        headers = {
            'Content-Type': content_type,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        return headers

    @staticmethod
    def set_default_result() -> GetResponseModel:
        result = GetResponseModel(
            status=False,
        )
        return result

    async def get_request(self, api: str, accessToken: str) -> GetResponseModel:
        headers = self.create_heders_with_auth(accessToken)
        result = self.set_default_result()
        url = f'http://{self.host}/api/v1/{api}'

        try:
            resp = await asyncio.wait_for(
                self.session.get(url, headers=headers),
                timeout=120,
            )
            result.data = await resp.text()
            if resp.ok and resp.status < 400:
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result

    async def get_request_waviot(self, api: str) -> GetResponseModel:
        headers = self.create_heders_with_auth_waviot()
        result = self.set_default_result()
        url = f'http://{self.host}/{api}'

        try:
            resp = await asyncio.wait_for(
                self.session.get(url, headers=headers),
                timeout=120,
            )
            result.data = await resp.text()
            if resp.ok and resp.status < 400:
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result

    async def get_request_with_params(self, api: str, accessToken: str, params: str) -> GetResponseModel:
        headers = self.create_heders_with_auth(accessToken)
        result = self.set_default_result()
        url = f'http://{self.host}/api/v1/{api}?{params}'

        try:
            resp = await asyncio.wait_for(
                self.session.get(url, headers=headers),
                timeout=120,
            )
            result.data = await resp.text()
            if resp.ok and resp.status < 400:
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result

    async def get_request_with_params_waviot(self, api: str, params: str) -> GetResponseModel:
        headers = self.create_heders_with_auth_waviot()
        result = self.set_default_result()
        url = f'http://{self.host}/{api}?{params}'

        try:
            resp = await asyncio.wait_for(
                self.session.get(url, headers=headers),
                timeout=120,
            )
            result.data = await resp.text()
            if resp.ok and resp.status < 400:
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result

    async def get_auth(self) -> GetResponseModel:
        result = self.set_default_result()
        url = f'http://{self.host}/api/v1/authentication'
        headers = self.create_heders()
        auth_strategy = json.dumps({'strategy': 'local', 'login': self.login_in, 'password': self.pass_in})

        try:
            resp = await asyncio.wait_for(
                self.session.post(url, data=auth_strategy, headers=headers),
                timeout=120,
            )
            if resp.ok and resp.status < 400:
                result.data = json.loads(await resp.text())['accessToken']
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result

    async def get_auth_waviot(self) -> GetResponseModel:
        result = self.set_default_result()
        url = f'http://{self.host}/auth'
        # headers = self.create_heders()
        auth_strategy = {'login': self.login_in, 'password': self.pass_in}

        try:
            resp = await asyncio.wait_for(
                self.session.post(url, json=auth_strategy),
                timeout=120,
            )
            if resp.ok and resp.status < 400:
                result.data = json.loads(await resp.text())
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result

    async def post_request(self, api: str, accessToken: str, data_in: dict) -> GetResponseModel:
        result = self.set_default_result()
        headers = self.create_heders_with_auth(accessToken)
        url = f'http://{self.host}/api/v1/{api}'
        # headers = self.create_heders()
        data_payload = json.dumps(data_in)

        try:
            resp = await asyncio.wait_for(
                self.session.post(url, data=data_payload, headers=headers),
                timeout=120,
            )
            result.data = await resp.text()
            if resp.ok and resp.status < 400:
                result.status = True
        except Exception as ex:
            result.error = ex.args
        return result


# async def main():
#     cookiejar = CookieJar(unsafe=True)
#     async with ClientSession(cookie_jar=cookiejar) as session:
#         con = BaseRequest(
#             session,
#             '192.1.1.220:6380',
#             'admin',
#             'admin',
#         )
#         await con.get_auth()
#         print(1)


# asyncio.run(main())

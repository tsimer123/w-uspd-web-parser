import asyncio

from aiohttp import ClientSession, CookieJar
import logging

from config import user_agent

class WorkItem:
    def __init__(self, url: str):
        # def __init__(self, url: str, arch_profile_request: str, arch_day_request: str, request_depth: str, task_id: int):
        self.url = url
        # self.request_depth = request_depth
        # self.arch_profile_request = arch_profile_request
        # self.arch_day_request = arch_day_request
        # self.task_id = task_id


async def get_local_id(url: str, session: ClientSession, params: str):
    try:
        headers = {"Content-Type": "application/json", "User-Agent": user_agent,}
        response = await asyncio.wait_for(
            session.get(f"http://{url}/gateway/localid",
                         headers=headers,
                ),
            timeout=30,
        )        
        return await response.json() 
        
    except Exception as e:
        logging.exception(f"Error get {params} {url}: {e.args}")

# http://10.25.0.9/gateway/messages?id=12375&from=1725736852&to=1726168852&types=0,1&limit=512

async def get_mesages(url: str, session: ClientSession, params: dict):
    try:
        headers = {"Content-Type": "application/json", "User-Agent": user_agent,}
        response = await asyncio.wait_for(
            session.get(f"http://{url}/gateway/messages?id={params['id']}&from={params['from']}&to={params['to']}&types={params['types']}&limit={params['limit']}",
                         headers=headers,
                ),
            timeout=30,
        )        
        return await response.json()
        
    except Exception as e:
        logging.exception(f"Error get {params} {url}: {e.args}")


async def get_data(work_item: WorkItem):    

    cookiejar = CookieJar(unsafe=True)
    async with ClientSession(cookie_jar=cookiejar) as session:
        response = await asyncio.wait_for(session.post(f"http://{work_item.url}/auth", json={"login": "admin", "password": "admin"}), timeout=30,)

        local_id = await get_local_id(work_item.url, session, "arch_profile_request")

        param_messages = {
        "id": str(local_id['id']),
        "from": '1725736852',
        "to": '1726168852',
        "types": '0,1',
        "limit": '512',
        }
        
        messages = await get_mesages(work_item.url, session, param_messages)

        print(1)
    


async def main():

    work_item = WorkItem(url='10.25.0.9')
    await get_data(work_item)

asyncio.run(main())
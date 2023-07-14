import aiohttp


group_id = '175107791'
# user_id = '664932461'
access_token = '19f58d0119f58d0119f58d01971ae70203119f519f58d017a1121e94612b41098d8fb2e'
v = '5.131'

async def vk_check_membership(link_vk: str) -> bool:
    user_id = await get_user_vk(link_vk)
    url = f'https://api.vk.com/method/groups.isMember?group_id={group_id}&user_id={user_id}&v={v}&access_token={access_token}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response = await r.json()
    if response['response'] == 1:
        return True
    else:
        return False
    
async def get_user_vk(link: str) -> str:
    if 'vk.com' in link.lower() or 'vk.ru' in link.lower():
        link = link.split('/')[-1]
    url = f'https://api.vk.com/method/users.get?user_id={link}&v={v}&access_token={access_token}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response = await r.json()
    try:
        uid = response['response'][0]['id']
    except IndexError:
        uid = 1
    return uid
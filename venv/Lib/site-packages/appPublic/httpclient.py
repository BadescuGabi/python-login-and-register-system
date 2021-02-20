import asyncio
import aiohttp
import re

RESPONSE_BIN = 0
RESPONSE_TEXT = 1
RESPONSE_JSON = 2
RESPONSE_FILE = 3

class HttpClient:
	def __init__(self,coding='utf-8'):
		self.coding = coding
		self.session = None
		self.cookies = {}

	async def close(self):
		await self.session.close()

	def url2domain(self,url):
		parts = url.split('/')[:3]
		pre = '/'.join(parts)
		return pre
		
	def setCookie(self,url,cookies):
		name = self.url2domain(url)
		self.cookies[name] = cookies

	def getCookies(self,url):
		name = url2domain(url)
		return self.cookies.get(name,None)

	def getsession(self,url):
		if self.session is None:
			jar = aiohttp.CookieJar(unsafe=True)
			self.session = aiohttp.ClientSession(cookie_jar=jar)
		return self.session
				
	async def handleResp(self,url,resp,resp_type):
		if resp.cookies is not None:
			self.setCookie(url,resp.cookies)

		if resp_type == RESPONSE_BIN:
			return await resp.read()
		if resp_type == RESPONSE_JSON:
			return await resp.json()
		# default resp_type == RESPONSE_TEXT:
		return await resp.text(self.coding)

	def grapCookie(self,url):
		session = self.getsession(url)
		domain = self.url2domain(url)
		filtered = session.cookie_jar.filter_cookies(domain)
		return filtered
		print(f'=====domain={domain},cookies={fltered},type={type(fltered)}===')

	async def get(self,url,
					params={},headers={},resp_type=RESPONSE_TEXT):
		session = self.getsession(url)
		resp = await session.get(url,params=params,headers=headers)
		if resp.status==200:
			return await self.handleResp(url,resp,resp_type)
		return None

	async def post(self,url,
					data=b'',headers={},cookies=None,
					resp_type=RESPONSE_TEXT):
		session = self.getsession(url)
		resp = await session.post(url,data=data,
						headers=headers,cookies=cookies)
		if resp.status==200:
			return await self.handleResp(url,resp,resp_type)
		print(f'**ERROR**{url} response code={resp.status}')
		return None

if __name__ == '__main__':
	async def gbaidu(hc):
		r = await hc.get('https://www.baidu.com')
		print(r)
		await hc.close()
	loop = asyncio.get_event_loop()
	hc = HttpClient()
	loop.run_until_complete(gbaidu(hc))


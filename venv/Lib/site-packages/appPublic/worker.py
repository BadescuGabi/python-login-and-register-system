import random
import asyncio
from functools import wraps

def asyncCall(func):
	@wraps(func)
	def wraped_func(*args,**kw):
		task =  asyncio.ensure_future(func(*args,**kw))
		asyncio.gather(task)
	return wraped_func

class Worker:
	def __init__(self,maxtask=50):
		self.semaphore = asyncio.Semaphore(maxtask)

	async def __call__(self,callee,*args,**kw):
		async with self.semaphore:
			return await callee(*args,**kw)

	async def run(self,cmd):
		async with self.semaphore:
			proc = await asyncio.create_subprocess_shell(cmd,
				stdout=asyncio.subprocess.PIPE,
				stderr=asyncio.subprocess.PIPE)

			stdout, stderr = await proc.comunicate()
			return stdout, stderr

if __name__ == '__main__':
	async def hello(cnt,greeting):
		t = random.randint(1,10)
		await asyncio.sleep(t)
		print(cnt,'cost ',t,'seconds to',greeting)

	
	async def run():
		w = Worker()
		tasks = [ w(hello,i,'hello world') for i in range(1000) ]
		await asyncio.wait(tasks)

	loop = asyncio.get_event_loop()
	loop.run_until_complete(run())
	

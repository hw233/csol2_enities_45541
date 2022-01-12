import BigWorld
from bwdebug import *

class WatchDog:

	class Pair:

		def __init__(self, first=None, second=None):
			self.first = first
			self.second = second

	def __init__(self):
		self._objects = {}

	def watch(self, key):
		""""""
		self._objects[key] = self.Pair(BigWorld.time())

	def release(self, key):
		""""""
		obj = self._objects.get(key)
		if obj:
			obj.second = BigWorld.time()
		else:
			WARNING_MSG("Can't find watch key: %s" % key)

	def remove(self, key):
		""""""
		if key in self._objects:
			del self._objects[key]

	def clear(self):
		""""""
		self._objects.clear()

	def report(self, start=0, end=0, sort=0, reverse=False):
		"""while end is 0, it means to the end of objects list."""
		if end == 0:
			end = len(self._objects)
		subjects = self._objects.items()[start:end]

		now = BigWorld.time()
		output = []
		for (key, obj) in subjects:
			if obj.second is None:
				output.append((key, now - obj.first, " NOT END"))
			else:
				output.append((key, obj.second - obj.first, ""))
		output.sort(key=lambda v: v[sort], reverse=reverse)

		content = "\n%s\n" % ("="*50)
		content += "| WatchDog report(%i/%i):\n" % (len(subjects), len(self._objects))
		content += "| Expected range:(%i-%i)\n|\n" % (start, end)

		fmt = "| %i Key [%s], cost %.2f%s"
		content += "\n".join(fmt % (i+1, v[0], v[1], v[2]) for i, v in enumerate(output))
		content += "\n"

		content += "| WatchDog report end\n"
		content += "="*50
		print content

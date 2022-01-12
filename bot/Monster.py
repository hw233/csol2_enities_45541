import BigWorld
class Monster( BigWorld.Entity ):
	def hasFlag(self, flag):
		flag = 1 << flag
		return (self.flags & flag) == flag
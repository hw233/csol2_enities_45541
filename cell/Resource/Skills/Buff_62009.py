# -*- coding:gb18030 -*-


from bwdebug import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_62009( Buff_Normal ):
	"""
	攻守兼备，将物理防御的%转化为攻击力
	"""
	def __init__( self ):
		Buff_Normal.__init__( self )
		self.param1 = 0		# 防御值换算比率
		self.improveValue = 0	# 攻击力提高值
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.param1 = float( data["Param1"] if len( data["Param1"] ) > 0 else 0 ) / 100.0
		
	def addToDict( self ):
		"""
		"""
		return { "param":self.improveValue }
		
	def createFromDict( self, data ):
		"""
		"""
		buffInstance = Buff_62009()
		buffInstance.__dict__.update( self.__dict__ )
		buffInstance.improveValue = data["param"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		buffInstance.setUID( uid )
		return buffInstance
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		self.improveValue = int( receiver.armor * self.param1 )
		receiver.damage_min_value += self.improveValue
		receiver.calcDamageMin()
		receiver.damage_max_value += self.improveValue
		receiver.calcDamageMax()

	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		self.improveValue = int( receiver.armor * self.param1 )
		receiver.damage_min_value += self.improveValue
		receiver.damage_max_value += self.improveValue
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.damage_min_value -= self.improveValue
		receiver.calcDamageMin()
		receiver.damage_max_value -= self.improveValue
		receiver.calcDamageMax()
		
		
# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_Normal import Buff_Normal
import time
from Function import newUID

class Buff_23008( Buff_Normal ):
	"""
	将一段时间内受到伤害的一定百分比转化为物理防御力。
	"""
	def __init__( self ):
		Buff_Normal.__init__( self )
		self.transferTime = 0		# 转换伤害为防御力持续时间
		self.transferPercent = 0	# 转换伤害比例
		self.transferBeginTime = 0	# 转换伤害为防御力开始时间
		self.transferValue = 0		# 转换的防御值
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.transferTime = float( data["Param1"] if len( data["Param1"] ) > 0 else 0 )
		self.transferPercent = float( data["Param2"] if len( data["Param2"] ) > 0 else 0 ) / 100
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		self.transferBeginTime = time.time()
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )

	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		self.transferBeginTime = time.time()
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeVictimAfterDamage( buffData[ "skill" ].getUID() )
		receiver.armor_value -= self.transferValue
		receiver.calcArmor()
		# 由于buff挂接到receiver身上时，使用的还会是同一个服务器的buff实例，因此重置以下值
		self.transferBeginTime = 0	# 转换伤害为防御力开始时间
		self.transferValue = 0		# 转换的防御值
		
	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		受到伤害时的触发
		"""
		if time.time() - self.transferBeginTime > self.transferTime:
			return
			
		defendValue = int( damage * self.transferPercent )
		receiver.armor_value += defendValue
		receiver.calcArmor()
		self.transferValue += defendValue
		
	def addToDict( self ):
		"""
		"""
		return { "param":{"transferValue":self.transferValue, "transferBeginTime":self.transferBeginTime}, "uid":self.getUID() }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Buff_23008()
		obj.__dict__.update( self.__dict__ )
		paramDict = data["param"]
		obj.transferValue = paramDict["transferValue"]
		obj.transferBeginTime = paramDict["transferBeginTime"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj
		
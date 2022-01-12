# -*-coding:gb18030-*-

from bwdebug import *
from Buff_Normal import Buff_Normal
from Function import newUID
import csdefine

class Buff_107020( Buff_Normal ):
	"""
	宠物技能专用buff重伤
	
	在之后的a秒内，每秒受到此次攻击伤害b%的伤害。加强性格则获得
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0
		self.parentDamage = 0
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.param1 = float( data["Param1"] if data["Param1"] > 0 else 0 ) / 100
		
	def doLoop( self, receiver, buffData ):
		"""
		"""
		damage = self.parentDamage * self.param1
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_FLAG_BUFF, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_FLAG_BUFF, damage )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def addToDict( self ):
		"""
		"""
		return { "param":self.parentDamage }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Buff_107020()
		obj.__dict__.update( self.__dict__ )
		obj.parentDamage = data["param"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj
		
	def adapt( self, damage ):
		"""
		buff适应所挂载技能，需要用外部数据做一些初始化生成一个新的buff实例
		"""
		return self.createFromDict( {"param":damage,"uid":newUID()} )
		
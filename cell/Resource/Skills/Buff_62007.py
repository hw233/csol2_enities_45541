# -*- coding:gb18030 -*-


import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_62007( Buff_Normal ):
	"""
	身体增大%，物理攻击提升%，法术攻击力提升%
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# 变大的倍率
		self._p4 = 0		# 物理法术攻击力提升%
		self.NPCOldModelScale = 1.0
		
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] )
		self._p4 = ( int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  / 100.0 ) * csconst.FLOAT_ZIP_PERCENT
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.damage_min_percent += self._p4
		receiver.calcDamageMin()
		receiver.damage_max_percent += self._p4
		receiver.calcDamageMax()
		receiver.magic_damage_percent += self._p4
		receiver.calcMagicDamage()
		self.NPCOldModelScale = receiver.modelScale
		receiver.modelScale = self._p1

	def doReload( self, receiver, buffData ):
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.damage_min_percent += self._p4
		receiver.damage_max_percent += self._p4
		receiver.magic_damage_percent += self._p4
		self.NPCOldModelScale = receiver.modelScale
		receiver.modelScale = self._p1
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.damage_min_percent -= self._p4
		receiver.calcDamageMin()
		receiver.damage_max_percent -= self._p4
		receiver.calcDamageMax()
		receiver.magic_damage_percent -= self._p4
		receiver.modelScale = self.NPCOldModelScale
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self.NPCOldModelScale }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_62007()
		obj.__dict__.update( self.__dict__ )

		obj.NPCOldModelScale = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
# -*- coding:gb18030 -*-


import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_299034( Buff_Normal ):
	"""
	参数为正数表示“增加”，负数则表示“减小”
	Buff的功能：
	移动速度增加/减小
	物理法术防御力增加/减小
	物理法术攻击力增加/减小
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# 移动速度增加/减小	
		self._p2 = 0		# 物理法术防御力增加/减小
		self._p3 = 0		# 物理法术攻击力增加/减小
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100		# 移动速度改变百分比
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100		# 物理法术防御力增加/减小百分比
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  * 100		# 物理法术攻击力增加/减小百分比
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.move_speed_percent += self._p1								# 移动速度
		receiver.calcMoveSpeed()
		
		receiver.armor_percent += self._p2									# 物理防御
		receiver.calcArmor()
		receiver.magic_armor_percent += self._p2							# 法术防御
		receiver.calcMagicArmor()
		
		receiver.damage_min_percent += self._p3								# 物理攻击力
		receiver.calcDamageMin()
		receiver.damage_max_percent += self._p3
		receiver.calcDamageMax()
		receiver.magic_damage_percent += self._p3							# 法术攻击力
		receiver.calcMagicDamage()

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.move_speed_percent -= self._p1
		receiver.armor_percent += self._p2									# 物理防御
		receiver.magic_armor_percent += self._p2							# 法术防御
		receiver.damage_min_percent += self._p3
		receiver.damage_max_percent += self._p3
		receiver.magic_damage_percent += self._p3
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.move_speed_percent -= self._p1	
		receiver.calcMoveSpeed()
		
		receiver.armor_percent -= self._p2									# 物理防御
		receiver.calcArmor()
		receiver.magic_armor_percent -= self._p2							# 法术防御
		receiver.calcMagicArmor()
		
		receiver.damage_min_percent -= self._p3
		receiver.calcDamageMin()
		receiver.damage_max_percent -= self._p3
		receiver.calcDamageMax()
		receiver.magic_damage_percent -= self._p3
		receiver.calcMagicDamage()
		
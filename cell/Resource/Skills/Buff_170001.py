# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst

class Buff_170001( Buff_Normal ):
	"""
	劈伤BUFF
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( float( dict["Param1"] )* csconst.FLOAT_ZIP_PERCENT )			# 降低物理攻击力%数值
		self.param2 = int( float( dict["Param2"] )* csconst.FLOAT_ZIP_PERCENT )			# 降低法术攻击力%数值

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
		receiver.damage_min_percent -= self.param1
		receiver.calcDamageMin()
		receiver.damage_max_percent -= self.param2
		receiver.calcDamageMax()

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.damage_min_percent += self.param1
		receiver.calcDamageMin()
		receiver.damage_max_percent += self.param2
		receiver.calcDamageMax()
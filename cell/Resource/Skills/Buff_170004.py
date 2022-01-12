# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst

class Buff_170004( Buff_Normal ):
	"""
	咒伤BUFF
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
		self.param1 = int( float( dict["Param1"] )* csconst.FLOAT_ZIP_PERCENT ) 			# 物理暴击几率降低%
		self.param2 = int( float( dict["Param2"] )* csconst.FLOAT_ZIP_PERCENT ) 			# 法术暴击几率降低%

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
		receiver.double_hit_probability_percent -= self.param1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_percent -= self.param2
		receiver.calcMagicDoubleHitProbability()

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
		receiver.double_hit_probability_percent += self.param1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_percent += self.param2
		receiver.calcMagicDoubleHitProbability()

# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst

class Buff_65010( Buff_Normal ):
	"""
	加暴击加闪避buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._param1 = 0
		self._param2 = 0
		self._param3 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict["Param1"] != "":
			self._param1 = int( float( dict["Param1"] )* csconst.FLOAT_ZIP_PERCENT ) # 物理暴击几率加%
		if dict["Param2"] != "":
			self._param2 = int( float( dict["Param2"] )* csconst.FLOAT_ZIP_PERCENT ) # 法术暴击几率加%
		if  dict["Param3"] != "":
			self._param3 = int( float( dict["Param3"] )* csconst.FLOAT_ZIP_PERCENT ) # 闪避几率加%

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
		receiver.double_hit_probability_percent += self._param1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_percent += self._param2
		receiver.calcMagicDoubleHitProbability()
		receiver.dodge_probability_percent += self._param3
		receiver.calcDodgeProbability()

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
		receiver.double_hit_probability_percent += self._param1
		receiver.magic_double_hit_probability_percent += self._param2
		receiver.dodge_probability_percent += self._param3

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
		receiver.double_hit_probability_percent -= self._param1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_percent -= self._param2
		receiver.calcMagicDoubleHitProbability()
		receiver.dodge_probability_percent -= self._param3
		receiver.calcDodgeProbability()
# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst

class Buff_170003( Buff_Normal ):
	"""
	砍伤BUFF
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
		self.param1 = int( float( dict["Param1"] )* csconst.FLOAT_ZIP_PERCENT )			# 被物理暴击几率提升%
		self.param2 = int( float( dict["Param2"] )* csconst.FLOAT_ZIP_PERCENT )			# 被法术暴击几率提升%

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
		receiver.be_double_hit_probability += self.param1
		receiver.be_magic_double_hit_probability += self.param2

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
		receiver.be_double_hit_probability -= self.param1
		receiver.be_magic_double_hit_probability -= self.param2

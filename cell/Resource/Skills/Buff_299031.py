# -*- coding: gb18030 -*-
#
# $Id: Buffer_299031.py,edit by wuxo 2011-11-26

"""
视频播放BUFFER
"""

import BigWorld
import csconst
import csstatus
import ECBExtend
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_299031( Buff_Normal ):
	"""
	视频播放BUFFER，处理视频播放完成后的一些客户端操作
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = None
		self._p2 = []
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = eval(str( dict[ "Param1" ] ))
		p2 = str( dict[ "Param2" ] )
		monsters = p2.split(";")
		for i in monsters:
			self._p2.append(eval(i))
		
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
		receiver.setTemp( "playCamera_eventID", self._p1[1] )
		receiver.addTimer(self._p1[0],0,ECBExtend.DELAY_PLAYCAMERA_TIMER_CBID)
		#创建怪物
		for i in self._p2 :
			for j in xrange(i[2] ):# 召怪的个数
				receiver.createObjectNearPlanes( i[0], i[1], receiver.direction, {} )
		

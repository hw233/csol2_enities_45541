# -*- coding: gb18030 -*-
#
# $Id: Buff_Radiancy.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_Radiancy( Buff_Normal ):
	"""
	光环buff大类，此类仅用于被继承。
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._radius = 0
		self._relationState = 0
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._radius = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 ) 		# 光环影响半径
		self._relationState = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 		# 光环效果作用对象
		
	def getRadius( self ):
		"""
		获得光环半径
		"""
		return self._radius
		
	def getRelationState( self ):
		"""
		获得光环会对何种关系产生影响
		"""
		return self._relationState
		
	def getReceivers( self, caster ):
		"""
		获得能接收光环buff的entity
		
		@param caster : 光环buff的主体entity
		@param relationFlag : 受术者条件，定义在csdefine中
		"""
		entities = caster.entitiesInRangeExt( self._radius, None, caster.position )
		newEntities = []
		for e in entities:
			if caster.queryRelation( e ) == self._relationState:
				newEntities.append( e )
		return newEntities
		
		
	def isCasterEntity( self, receiver, buffData ):
		"""
		判断是否是buff主体
		"""
		id = buffData["caster"]
		if id == receiver.id:
			return True
		return False
		
		
	def doBeginCaster( self, caster, buffData ):
		"""
		virtual method.
		
		如果是主体buff，则做主体buff的事情
		debuff效果，如果receiver是主体，则不会受影响
		"""
		# 如果是光环buff则必定有self._radius参数，光环影响范围半径
		receivers = self.getReceivers( caster )
		for receiver in receivers:	# 给符合条件的entity加上buff
			buffIndexList = receiver.findBuffsByBuffID( self.getBuffID() )
			if len( buffIndexList ) == 0:
				self.receive( caster, receiver )
				continue
			for index in buffIndexList:
				buff = receiver.getBuff( index )
				if buff[ "skill" ].getLevel() == self.getLevel():	# 如果receiver身上的buff级别与自己一样，那么不给receiver发送
					continue
				else:
					self.receive( caster, receiver )
					break
					
					
	def doBeginReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		如果是非主体buff，则做非主体buff的事情
		"""
		pass
		
		
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
		if self.isCasterEntity( receiver, buffData ):
			self.doBeginCaster( receiver, buffData )
		else:
			self.doBeginReceiver( receiver, buffData )
			
			
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
		if self.isCasterEntity( receiver, buffData ):	# 仅对主体entity有效
			self.doBeginCaster()
			
			
	def doLoopCaster( self, caster, buffData ):
		"""
		virtual method.
		
		如果是主体buff，则做主体buff的事情
		debuff效果，如果receiver是主体，则不会受影响。
		"""
		# 如果是光环buff则必定有self._radius参数，光环影响范围半径
		receivers = self.getReceivers( caster )
		for receiver in receivers:	# 给符合条件的entity加上buff
			buffIndexList = receiver.findBuffsByBuffID( self.getBuffID() )
			if len( buffIndexList ) == 0:
				self.receive( caster, receiver )
				continue
			for index in buffIndexList:
				buff = receiver.getBuff( index )
				if buff[ "skill" ].getLevel() == self.getLevel():	# 如果receiver身上的buff级别与自己一样，那么不给receiver发送
					continue
				else:
					self.receive( caster, receiver )
					break
					
					
	def doLoopReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		如果是非主体buff，则做非主体buff的事情
		"""
		pass
		
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		# debuff效果，如果主体是receiver，则receiver将不会受影响，判断是否有新的receiver进入光环影响范围。
		if self.isCasterEntity( receiver, buffData ):
			self.doLoopCaster( receiver, buffData )
		else:
			self.doLoopReceiver( receiver, buffData )
			
		return Buff_Normal.doLoop( self, receiver, buffData )	
#$Log: not supported by cvs2svn $
#
#
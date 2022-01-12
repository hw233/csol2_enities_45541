# -*- coding: gb18030 -*-
#
# $Id: Buff_7004.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from Buff_Radiancy import Buff_Radiancy

class Buff_7004( Buff_Radiancy ):
	"""
	愈合之光，通过光环效果使周围己方单体获得缓慢恢复的效果
	"""
	def __init__( self ):
		"""
		"""
		Buff_Radiancy.__init__( self )
		self._p3 = 0
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Radiancy.init( self, dict )
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 ) 		# 受到治疗的值
		
		
	def doBeginCaster( self, caster, buffData ):
		"""
		virtual method.
		
		如果是主体buff，则做主体buff的事情
		debuff效果，如果receiver是主体，则不会受影响
		"""
		Buff_Radiancy.doBeginCaster( self, caster, buffData )
		caster.addHP( self._p3 )
		
		
	def doBeginReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		如果是非主体buff，则做非主体buff的事情
		"""
		Buff_Radiancy.doBeginReceiver( self, receiver, buffData )
		receiver.addHP( self._p3 )
		
		
	def doLoopCaster( self, receiver, buffData ):
		"""
		virtual method.
		
		如果是主体buff，则做主体buff的事情
		"""
		Buff_Radiancy.doLoopCaster( self, receiver, buffData )
		receiver.addHP( self._p3 )
		
		
	def doLoopReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		如果是非主体buff，则做非主体buff的事情
		"""
		Buff_Radiancy.doLoopReceiver( self, receiver, buffData )
		id = buffData["caster"]
		skillID = buffData["skill"].getID()
		if not BigWorld.entities.has_key( id ):
			receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
			return
		caster = BigWorld.entities[ id ]
		if receiver.distanceBB( caster ) > self.getRadius():	# 不在距离之内
			receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
			return
		buffIndexList = receiver.findBuffsByBuffID( self.getBuffID() )
		if len( buffIndexList ) == 0:	# 主体已卸下buff
			receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
			return
		for index in buffIndexList:
			buff = receiver.getBuff( index )
			if buff["skill"].getLevel() == self.getLevel():
				changeHP = receiver.addHP( self._p3 )
				caster.doCasterOnCure( receiver, changeHP )		# 治疗目标时触发
				receiver.doReceiverOnCure( caster, changeHP )   	# 被治疗时触发
				return
		receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
		return
		
#$Log: not supported by cvs2svn $
#
#
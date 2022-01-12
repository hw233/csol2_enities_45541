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
	����֮�⣬ͨ���⻷Ч��ʹ��Χ���������û����ָ���Ч��
	"""
	def __init__( self ):
		"""
		"""
		Buff_Radiancy.__init__( self )
		self._p3 = 0
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Radiancy.init( self, dict )
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 ) 		# �ܵ����Ƶ�ֵ
		
		
	def doBeginCaster( self, caster, buffData ):
		"""
		virtual method.
		
		���������buff����������buff������
		debuffЧ�������receiver�����壬�򲻻���Ӱ��
		"""
		Buff_Radiancy.doBeginCaster( self, caster, buffData )
		caster.addHP( self._p3 )
		
		
	def doBeginReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		����Ƿ�����buff������������buff������
		"""
		Buff_Radiancy.doBeginReceiver( self, receiver, buffData )
		receiver.addHP( self._p3 )
		
		
	def doLoopCaster( self, receiver, buffData ):
		"""
		virtual method.
		
		���������buff����������buff������
		"""
		Buff_Radiancy.doLoopCaster( self, receiver, buffData )
		receiver.addHP( self._p3 )
		
		
	def doLoopReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		����Ƿ�����buff������������buff������
		"""
		Buff_Radiancy.doLoopReceiver( self, receiver, buffData )
		id = buffData["caster"]
		skillID = buffData["skill"].getID()
		if not BigWorld.entities.has_key( id ):
			receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
			return
		caster = BigWorld.entities[ id ]
		if receiver.distanceBB( caster ) > self.getRadius():	# ���ھ���֮��
			receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
			return
		buffIndexList = receiver.findBuffsByBuffID( self.getBuffID() )
		if len( buffIndexList ) == 0:	# ������ж��buff
			receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
			return
		for index in buffIndexList:
			buff = receiver.getBuff( index )
			if buff["skill"].getLevel() == self.getLevel():
				changeHP = receiver.addHP( self._p3 )
				caster.doCasterOnCure( receiver, changeHP )		# ����Ŀ��ʱ����
				receiver.doReceiverOnCure( caster, changeHP )   	# ������ʱ����
				return
		receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
		return
		
#$Log: not supported by cvs2svn $
#
#
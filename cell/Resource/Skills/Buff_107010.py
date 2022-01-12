# -*- coding: gb18030 -*-
#
# $Id: Buff_107010.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Radiancy import Buff_Radiancy


class Buff_107010( Buff_Radiancy ):
	"""
	ɱ���⻷��ÿ3���ܵ�1�������˺���
	"""
	def __init__( self ):
		"""
		"""
		Buff_Radiancy.__init__( self )
		self._p3 = 0		# �����˺�ֵ
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Radiancy.init( self, dict )
		
		# dict[ "param1" ].asInt,buffӰ��ķ�Χ�뾶
		# dict[ "param2" ].asInt,buff�����˺�
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  		# ��д����ʱ��ע��
		
		
	def doBeginReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		����Ƿ�����buff������������buff������
		"""
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_PHYSICS, int( self._p3 ) )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage )
		
		
	def doLoopReceiver( self, receiver, buffData ):
		"""
		virtual method.
		����Ƿ�����buff������������buff������
		�����������buff��Ӱ�죬��ж��buff
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
				damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_PHYSICS, int( self._p3 ) )
				receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
				receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage )
				return
		receiver.removeBuffByID( skillID, [csdefine.BUFF_INTERRUPT_NONE] )
		return
		
		
#$Log: not supported by cvs2svn $
#
#
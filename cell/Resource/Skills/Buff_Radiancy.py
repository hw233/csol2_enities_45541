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
	�⻷buff���࣬��������ڱ��̳С�
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._radius = 0
		self._relationState = 0
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._radius = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 ) 		# �⻷Ӱ��뾶
		self._relationState = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 		# �⻷Ч�����ö���
		
	def getRadius( self ):
		"""
		��ù⻷�뾶
		"""
		return self._radius
		
	def getRelationState( self ):
		"""
		��ù⻷��Ժ��ֹ�ϵ����Ӱ��
		"""
		return self._relationState
		
	def getReceivers( self, caster ):
		"""
		����ܽ��չ⻷buff��entity
		
		@param caster : �⻷buff������entity
		@param relationFlag : ������������������csdefine��
		"""
		entities = caster.entitiesInRangeExt( self._radius, None, caster.position )
		newEntities = []
		for e in entities:
			if caster.queryRelation( e ) == self._relationState:
				newEntities.append( e )
		return newEntities
		
		
	def isCasterEntity( self, receiver, buffData ):
		"""
		�ж��Ƿ���buff����
		"""
		id = buffData["caster"]
		if id == receiver.id:
			return True
		return False
		
		
	def doBeginCaster( self, caster, buffData ):
		"""
		virtual method.
		
		���������buff����������buff������
		debuffЧ�������receiver�����壬�򲻻���Ӱ��
		"""
		# ����ǹ⻷buff��ض���self._radius�������⻷Ӱ�췶Χ�뾶
		receivers = self.getReceivers( caster )
		for receiver in receivers:	# ������������entity����buff
			buffIndexList = receiver.findBuffsByBuffID( self.getBuffID() )
			if len( buffIndexList ) == 0:
				self.receive( caster, receiver )
				continue
			for index in buffIndexList:
				buff = receiver.getBuff( index )
				if buff[ "skill" ].getLevel() == self.getLevel():	# ���receiver���ϵ�buff�������Լ�һ������ô����receiver����
					continue
				else:
					self.receive( caster, receiver )
					break
					
					
	def doBeginReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		����Ƿ�����buff������������buff������
		"""
		pass
		
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���
		
		@param receiver: Ч��ҪӰ���ʵ��
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
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		if self.isCasterEntity( receiver, buffData ):	# ��������entity��Ч
			self.doBeginCaster()
			
			
	def doLoopCaster( self, caster, buffData ):
		"""
		virtual method.
		
		���������buff����������buff������
		debuffЧ�������receiver�����壬�򲻻���Ӱ�졣
		"""
		# ����ǹ⻷buff��ض���self._radius�������⻷Ӱ�췶Χ�뾶
		receivers = self.getReceivers( caster )
		for receiver in receivers:	# ������������entity����buff
			buffIndexList = receiver.findBuffsByBuffID( self.getBuffID() )
			if len( buffIndexList ) == 0:
				self.receive( caster, receiver )
				continue
			for index in buffIndexList:
				buff = receiver.getBuff( index )
				if buff[ "skill" ].getLevel() == self.getLevel():	# ���receiver���ϵ�buff�������Լ�һ������ô����receiver����
					continue
				else:
					self.receive( caster, receiver )
					break
					
					
	def doLoopReceiver( self, receiver, buffData ):
		"""
		virtual method.
		
		����Ƿ�����buff������������buff������
		"""
		pass
		
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		# debuffЧ�������������receiver����receiver��������Ӱ�죬�ж��Ƿ����µ�receiver����⻷Ӱ�췶Χ��
		if self.isCasterEntity( receiver, buffData ):
			self.doLoopCaster( receiver, buffData )
		else:
			self.doLoopReceiver( receiver, buffData )
			
		return Buff_Normal.doLoop( self, receiver, buffData )	
#$Log: not supported by cvs2svn $
#
#
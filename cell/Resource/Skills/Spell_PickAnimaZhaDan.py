# -*- coding: gb18030 -*-
from Spell_BuffNormal import *

class Spell_PickAnimaZhaDan( Spell ):
	"""
	ʰȡ�����淨ը��Ч��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.destroyAnimaRange = 0.0 # ���ٶ��Χ������
		self.isResertCount = False #�Ƿ����ü�����
	
	def init( self, data ):
		"""
		��ȡ��������
		@param data: ��������
		@type  data: python dict
		"""
		Spell.init( self, data )
		self.destroyAnimaRange = float( data[ "param1" ] )
		self.isResertCount = bool( data[ "param2" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		self.receiveLinkBuff( caster, receiver )
		if self.destroyAnimaRange:
			desList = receiver.entitiesInRangeExt( self.destroyAnimaRange, "TrapPickAnima", receiver.position )
			for trap in desList:
				trap.destroy()
				
		if self.isResertCount:
			receiver.getCurrentSpaceCell().resertAddition( receiver.planesID, receiver )
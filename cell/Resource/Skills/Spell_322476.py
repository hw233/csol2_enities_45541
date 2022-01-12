# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_Magic import Spell_Magic

class Spell_322476( Spell_Magic ):
	"""
	Ϳ����
	
	������ж��صļ������Ŀ����������ѪЧ����
	��ʹ�Է����������µ�DEBUFF�����綾���ü���Ч����ÿ5������һ�ζԷ�������ֵ���������˺���
	"""
	def __init__( self ):
		Spell_Magic.__init__( self )
		self.param1 = 0		# Ӱ��ļ��ܣ��˼��ܲ�����buff���ܱ�Ӱ��
		self.bleedingBuffID = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Magic.init( self, data )
		self.param1 = int( data["param1"] if len( data["param1"] ) > 0 else 0 )
		self.bleedingBuffID = int( data["param2"] if len( data["param2"] ) > 0 else 0 )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		������Ѫ�����������Ѫbuff���ܽ��վ綾buff
		"""
		buffIndexs = receiver.findBuffsByBuffID( self.bleedingBuffID )
		if not buffIndexs:
			return
		haveBleedingBuff = False
		for index in buffIndexs:
			buff = receiver.getBuff( index )
			if buff["skill"].getID() / 100000 != self.param1:	# ȥ��buff index��ȥ�����ܼ���
				continue
			haveBleedingBuff = True
			
		if not haveBleedingBuff:
			return
		# ����buff��receive()���Զ��ж�receiver�Ƿ�ΪrealEntity
		# ��Ѫbuff�;綾buff��ͬһ��buff��ţ����ڹ��򣺼���ߵ�buff���滻����͵�buff
		Spell_Magic.receiveLinkBuff( self, caster, receiver )
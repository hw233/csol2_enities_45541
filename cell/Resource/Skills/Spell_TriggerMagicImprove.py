# -*- coding: gb18030 -*-

#edit by wuxo 2012-2-9

from Spell_MagicImprove import Spell_MagicImprove


class Spell_TriggerMagicImprove(Spell_MagicImprove):
	def __init__( self ) :
		Spell_MagicImprove.__init__( self )
		self._triggerSpellID = 0	#�����ļ���ID
		self._triggerTime    = 0	#��ǰ���ܴ��ڴ�����ʹ��״̬��ĸ���ܴ������������д��	
		self._parentID       = 0         #ĸ����ID
		
	def init( self, dictData ):
		"""
		��ȡ��������
		@param dictData:	��������
		@type dictData:	python dictData
		"""
		Spell_MagicImprove.init( self, dictData )
		
		if dictData["param2"] != "":
			self._parentID = int( dictData["param2"] )	
		
		if dictData["param3"] != "":
			self._triggerSpellID = int( dictData["param3"] )
		
		if dictData["param4"] != "":
			self._triggerTime  = float( dictData["param4"] ) #�����ļ��ܳ���ʱ��
		
		
		
	def cast( self, caster, target ):
		"""
		��ʽ��һ��Ŀ���λ��ʩ��
		"""
		Spell_MagicImprove.cast( self, caster, target )
		
		if self._parentID == 0:
			self._parentID = self.getID()
		caster.addTriggerSpell(self._parentID, self._triggerSpellID)
		
		
	def getTriggerTime(self):
		"""
		��õ�ǰ���ܣ������������ڿ��ͷ�״̬��ʱ��
		"""
		return self._triggerTime
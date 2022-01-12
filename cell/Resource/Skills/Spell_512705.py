# -*- coding: gb18030 -*-
#
# $Id: Spell_512705.py,v 1.4 2008-07-15 04:06:26 kebiao Exp $

"""
"""

from SpellBase import *
from Spell_Magic import Spell_Magic
import random
import csdefine
import csconst
import Const

class Spell_512705( Spell_Magic ):
	"""
	������	��������������ɶ����˺�������30%����ȡ���Է����ϵ�һ������BUFF
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF
		
	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._dispelRate = int( dict.get( "param1" , 0 ) )			# ����ɢ����
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
				
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_Magic.onArrive( self, caster, target )
		receiver = target.getObject()
		if not receiver:
			return
			
		#��Ϊ�ü���Ϊ���弼�� ���Դ˴���ô���ǶԵ� caster is real
		# �� Spell_Magic.onArrive( self, caster, receiver ) ���ܵ��� receiverΪreal ����Ҫ��ô��
		Spell_Magic.receive( self, caster, receiver ) 
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if random.randint(0,100) > self._dispelRate:
			return
		# ��ɢĿ�����ϵ�buff

		for index, buff in enumerate( receiver.getBuffs() ):
			skill = buff["skill"]
			if skill.getEffectState() == csdefine.SKILL_EFFECT_STATE_BENIGN and skill.getLevel() < self.getLevel():# ֻ����ɢ���Լ�����׵�BUFF
				receiver.removeBuff( index, self._triggerBuffInterruptCode )
				break
			
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/05/28 05:59:47  kebiao
# �޸�BUFF�������ʽ
#
# Revision 1.2  2007/12/26 09:03:57  kebiao
# no message
#
# Revision 1.1  2007/12/26 03:54:24  kebiao
# no message
#
#
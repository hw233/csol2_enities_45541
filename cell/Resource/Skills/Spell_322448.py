# -*- coding: gb18030 -*-

#

import BigWorld
import csdefine
import csstatus
import random
from SpellBase import *

class Spell_322448( Spell ):
	"""
	ϵͳ����
	"�ü���ͬʱ���ڶ�Ŀ���DEBUFF�Ͷ������BUFF����ͨBUFF���ܲ�������Ҫ��ͬʱ�������ж����ȶ�Ŀ���DEBUFFʩ�ųɹ���Ŀ���ô�DEBUFF�������ܲ����������BUFF
�˴����ͷ�����DEBUFF104006��������������BUFF004005�������е�BUFF��"

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		self.receiveLinkBuff( caster, receiver )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		buff = self._buffLink[0]
		# �в����������жϻ���
		if not self.canLinkBuff( caster, receiver, buff ): return

		buff.getBuff().receive( caster, receiver )
		self._buffLink[1].getBuff().receive( caster, caster )
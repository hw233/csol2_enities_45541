# -*- coding: gb18030 -*-
#
# $Id: Spell_EffectVehicle.py,v 1.1 2008-09-04 06:43:35 yangkai Exp $

"""
"""
from SpellBase import Spell
import csstatus

class Spell_EffectVehicle( Spell ):
	"""
	�������Ч���ļ���,�������װ��buff
	������ٻ����첽�ԣ����зֿ����ٻ����ܺ���Ч���ļ���
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
		# ����Ҽ�һ�����ר��buff
		self.receiveLinkBuff( caster, receiver )

# $Log: not supported by cvs2svn $

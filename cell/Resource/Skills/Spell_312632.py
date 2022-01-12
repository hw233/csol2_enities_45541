# -*- coding: gb18030 -*-
#
from bwdebug import *
import BigWorld
import csconst
from Spell_ElemDamage import Spell_ElemDamage
import time
import csdefine

class Spell_312632( Spell_ElemDamage ):
	"""
	�ü��ܿɲο����͵ļ��ܷ�β321206/��ɱ311127�����еķ�ɱ����������ƣ���֮ͬ���ڷ�ɱ�����������˺���
	�˼�������ȫԪ���˺����������ɫ������������
	�˼��������漰�ġ��Ļ���ա�״̬��������ļ��ܡ���������е�DEBUFF��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ElemDamage.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ElemDamage.init( self, dict )

	def calcElemDamage( self, caster, receiver, attackdamage = 0 ):
		"""
		virtual method.
		����Ԫ���˺�
		"""
		# �˺�x(1+DEBUFF������ʱ��/DEBUFF��ʱ��)
		damageMult = 1
		indexs = receiver.findBuffsByBuffID( 107017 )
		if len( indexs ):
			index = indexs[0]
			buff = receiver.getBuff( index )
			endTime = buff["persistent"]
			nowTime = time.time()
			skill = buff["skill"]
			totalTime = float( skill._persistent )
			damageMult = max( 1.0, 1 + ( ( totalTime - ( endTime - nowTime  ) ) / totalTime ) )
			receiver.removeAllBuffByBuffID( skill.getBuffID(), [ csdefine.BUFF_INTERRUPT_NONE ] )

		elemEffect = caster.queryTemp( "ELEM_ATTACK_EFFECT", "" )
		if elemEffect == "huo":		# ��Ԫ�ع���Ч��
			return [ self._huo_damage * damageMult + attackdamage, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult ]
		elif elemEffect == "xuan":	# ��Ԫ�ع���Ч��
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult + attackdamage, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult ]
		elif elemEffect == "lei":	# ��Ԫ�ع���Ч��
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult + attackdamage, \
					self._bing_damage * damageMult ]
		elif elemEffect == "bing":	# ��Ԫ�ع���Ч��
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult + attackdamage ]
		else:
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult ]

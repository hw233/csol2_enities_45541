# -*- coding:gb18030 -*-

from Spell_PhysSkill import Spell_PhysSkill
import csconst
import random

class Spell_PhysSkillImprove( Spell_PhysSkill ):
	"""
	��������������������ס����˺������ļ�����
	param1���÷������������ס����˺�����������10;0;150;0;0��ʹ�÷ֺŸ�����10��ʾ10%��0��ʾû������������
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkill.__init__( self )
		self.physPercent = 0
		self.huoPercent = 0
		self.xuanPerent = 0
		self.leiPercent = 0
		self.bingPercent = 0
		
	def init( self, data ):
		"""
		"""
		Spell_PhysSkill.init( self, data )
		percentParam = data["param1"] if len( data["param1"] ) > 0 else "0;0;0;0;0"
		percentList = [ int( param )/ 100.0 for param in percentParam.split( ";" ) ]
		self.physPercent = percentList[0]
		self.huoPercent = percentList[1]
		self.xuanPerent = percentList[2]
		self.leiPercent = percentList[3]
		self.bingPercent = percentList[4]
		
	def calcElemDamage( self, caster, receiver, attackdamage = 0 ):
		"""
		virtual method.
		����Ԫ���˺�
		"""
		elemEffect = caster.queryTemp( "ELEM_ATTACK_EFFECT", "" )
		if elemEffect == "huo":		# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage + attackdamage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]
		elif elemEffect == "xuan":	# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage + attackdamage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]
		elif elemEffect == "lei":	# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage + attackdamage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]
		elif elemEffect == "bing":	# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage + attackdamage ]
		else:
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		��ʽ1�����ܹ��������ܹ�ʽ�еĻ���ֵ��=���ܱ���Ĺ�����+��ɫ����������
		�����ܹ�ʽ�о��ǣ������ܱ���Ĺ�����+��ɫ����������*��1+���������ӳɣ�+����������ֵ
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		extra = random.randint( int( source.damage_min*(1+self.physPercent) ), int( source.damage_max*(1+self.physPercent) ) )
		base = random.randint( self._effect_min, self._effect_max )
		return self.calcProperty( base, extra, dynPercent + source.skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.skill_extra_value )


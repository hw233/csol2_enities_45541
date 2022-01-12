# -*- coding: gb18030 -*-
#
from SpellBase.Spell import Spell
from gbref import rds
import Const

class Spell_322398002( Spell ):
	"""
	�ڱ��Ŀͻ��˼���
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def interrupt( self, caster, reason ):
		"""
		�ڱ�������ֹ
		"""
		if hasattr( caster, "set_righthandFDict" ):
			caster.set_righthandFDict()
		if hasattr( caster, "set_lefthandFDict" ):
			caster.set_lefthandFDict()

		Spell.interrupt( self, caster, reason )

	def intonate( self, caster, intonateTime, targetObject ):
		"""
		�����ڱ���������������Ч����
		"""
		# ��������ģ����ʾС��ͷģ��
		model = caster.getModel()
		if model:
			if hasattr( model, "right_hand" ):
				cModel = rds.effectMgr.createModel( [Const.CHUTOU_MODEL_PATH] )
				model.right_hand = cModel
			if hasattr( model, "left_hand" ) and model.left_hand:
				model.left_hand = None
			if hasattr( model, "left_shield" ) and model.left_shield:
				model.left_shield = None

		Spell.intonate( self, caster, intonateTime, targetObject )

	def cast( self, caster, targetObject ):
		"""
		�ڱ������ͷ�Ч��
		"""
		if hasattr( caster, "set_righthandFDict" ):
			caster.set_righthandFDict()
		if hasattr( caster, "set_lefthandFDict" ):
			caster.set_lefthandFDict()
		Spell.cast( self, caster, targetObject )



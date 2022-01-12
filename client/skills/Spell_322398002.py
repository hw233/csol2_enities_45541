# -*- coding: gb18030 -*-
#
from SpellBase.Spell import Spell
from gbref import rds
import Const

class Spell_322398002( Spell ):
	"""
	挖宝的客户端技能
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def interrupt( self, caster, reason ):
		"""
		挖宝技能终止
		"""
		if hasattr( caster, "set_righthandFDict" ):
			caster.set_righthandFDict()
		if hasattr( caster, "set_lefthandFDict" ):
			caster.set_lefthandFDict()

		Spell.interrupt( self, caster, reason )

	def intonate( self, caster, intonateTime, targetObject ):
		"""
		播放挖宝技能吟唱动作和效果。
		"""
		# 隐藏武器模型显示小锄头模型
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
		挖宝技能释放效果
		"""
		if hasattr( caster, "set_righthandFDict" ):
			caster.set_righthandFDict()
		if hasattr( caster, "set_lefthandFDict" ):
			caster.set_lefthandFDict()
		Spell.cast( self, caster, targetObject )



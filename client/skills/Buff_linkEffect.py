# -*- coding: gb18030 -*-

import BigWorld
import Const
import Define
import Math
from bwdebug import *
from SpellBase import *
from gbref import rds
from Function import Functor

class Buff_linkEffect( Buff ):
	"""
	���߹�ЧBuff�ͻ��˽ű���ֻ��Բ�����ʵ�壩
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def playEffect( self, caster, target ):
		"""
		����buffЧ��
		"""
		skillID = self.getEffectID() * 1000
		if hasattr( caster, "isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( self.playLinkEffects, caster, target, skillID ) )
		else:
			self.playLinkEffects( caster, target, skillID )

		# buff����Ч����һ��������BUFF����������
		self.pose.buffCast( target, skillID )

	def playLinkEffects( self, caster, target, skillID ):
		"""
		���߹�ЧbuffЧ��
		"""
		target.buffEffect[skillID] = {}
		# ��Ч
		weaponType = 0
		casterID = 0
		cModel = None
		tModel = None
		cType = Define.TYPE_PARTICLE_PLAYER
		tType = Define.TYPE_PARTICLE_PLAYER
		if caster:
			weaponType = caster.weaponType
			casterID = caster.id
		dict = rds.spellEffect.getCastEffect( skillID, casterID, weaponType )
		if dict:
			if caster:
				pyModel = BigWorld.Model( Const.EMPTY_MODEL_PATH_1 )	# ��BoundingBox�ϴ�Ŀ�ģ�����ԭ�е�ʵ��ģ��
				caster.addModel( pyModel )
				caster.linkEffectModel = pyModel
				pyModel.position = caster.position + Math.Vector3( 0, 1, 0 )
				pyModel.yaw = caster.yaw
				cModel = pyModel
				cType = caster.getParticleType()
			if target:
				tModel = target.getModel()
				tType = target.getParticleType()

			effect = rds.skillEffect.createEffect( dict, cModel, tModel, cType, tType )
			if effect:
				effect.start()
				target.buffEffect[skillID]["buff_effect"] = effect

			if effect.__class__.__name__ == "LinkEffect":
				caster.linkEffect.append( effect )
				target.linkEffect.append( effect )

		# ����
		soundNames = rds.spellEffect.getSpellCastSound( skillID )
		target.buffEffect[skillID]["buff_sound"] = soundNames
		for name in soundNames:
			rds.skillEffect.playSound( target, name )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		caster.delModel( caster.linkEffectModel )
		caster.linkEffectModel = None

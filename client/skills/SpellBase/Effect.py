# -*- coding: gb18030 -*-
#
# $Id: Effect.py,v 1.21 2008-08-26 08:00:56 yangkai Exp $

import math
import Language
from bwdebug import *
import BigWorld
import csdefine
import Pixie
import Math
import utils
import csol
from gbref import rds
from Sound import soundMgr
from Function import *
import weakref
import Define
import time
import Const
import skills
import csconst

SOURCE_MATRIX_SWARM = 13 #����Ч��������ʵ������WOW������֮��Ч����action

EFFECT_LIFE_TIME = 0.3												#�ܻ��й�Ч���ʱ��
EFFECT_LIMIT_COUNT = 2												#�ܻ��й�Ч��������


class Effect:
	"""
	Ч��
	"""
	_instance = None
	def __init__( self ):
		assert Effect._instance is None, "instance already exist in"

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = Effect()
		return self._instance

	def makeEffect( self, dict, caster, target ):
		"""
		Return the Effect type instance
		@param dict		:	������������
		@type dict		:	python dict
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	ʩչ����
		"""
		cModel = None
		tModel = None
		cType = Define.TYPE_PARTICLE_PLAYER
		tType = Define.TYPE_PARTICLE_PLAYER
		if caster:
			cModel = caster.getModel()
			cType = caster.getParticleType()
		if target:
			tModel = target.getModel()
			tType = target.getParticleType()

		return self.createEffect( dict, cModel, tModel, cType, tType )

	def createEffect( self, dict, cModel, tModel, cType, tType ):
		"""
		Return the Effect type instance
		@param dict		:	������������
		@type dict		:	python dict
		@param cModel	:	ʩչģ��
		@type cModel	:	PyModel
		@param tModel	:	Ŀ��ģ��
		@type tModel	:	PyModel
		@param cType	:	ʩչ��������
		@type cType		:	int
		@param tType	:	Ŀ����������
		@type tType		:	int
		"""
		return createSuitableEffect( dict, cModel, tModel, cType, tType )

	def createEffectByID( self, effectID, cModel, tModel, cType, tType ):
		"""
		Return the Effect type instance
		@param effectID	:	��������ID
		@type effectID	:	string
		@param cModel	:	ʩչģ��
		@type cModel	:	PyModel
		@param tModel	:	Ŀ��ģ��
		@type tModel	:	PyModel
		@param cType	:	ʩչ��������
		@type cType		:	int
		@param tType	:	Ŀ����������
		@type tType		:	int
		"""
		dict = rds.spellEffect.getEffectConfigDict( effectID )
		if len( dict ) == 0: return
		return self.createEffect( dict, cModel, tModel, cType, tType )

	def playBeginEffects( self, caster, targetObject, skillID ):
		"""
		Play the BeginEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	ʩչ����
		@type  target	:	һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@param 	:	����ID
		@type skillID	:	Int
		"""
		# ����
		soundNames = rds.spellEffect.getSpellStartSound( skillID )
		voiceNames = ()
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			gender = caster.getGender()
			if gender == csdefine.GENDER_MALE:
				voiceNames = rds.spellEffect.getSpellStartVoice_Man( skillID )	# all voiceNames������������ by����
			else:
				voiceNames = rds.spellEffect.getSpellStartVoice_Female( skillID )
			soundNames += voiceNames
		caster.allEffects[ "beginSound" ] = soundNames
		for name in soundNames:
			self.playSound( caster, name )
		# ��Ч
		dict = rds.spellEffect.getStartEffect( skillID, caster.id, caster.weaponType )
		if dict is None: return
		if targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION:
			#do some thing
			sk = skills.getSkill( skillID )		# CSOL-1724λ�ù�Ч������ʼ��Ч֧��
			if sk and sk.isTargetPositionSkill():
				effect = self.makeEffect( dict, caster, caster )
				if effect is None: return
				effect.start()
			else:
				effect = self.makeEffect( dict, caster, None )
				if effect is None: return
				if effect.__class__.__name__ == "PositionEffect":
					pos = targetObject.getObject()
					effect.setPosition( pos )
					effect.start()
				if effect.__class__.__name__ == "HomerParaParPosEffect":
					pos = targetObject.getObject()
					effect.onTargetPos( pos )
					effect.start()
		else:
			effect = self.makeEffect( dict, caster, targetObject.getObject() )
			if effect is None: return
			effect.start()
		caster.allEffects[ "begin" ] = effect

	def stopBeginEffects( self, caster ):
		"""
		Play the BeginEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		"""
		# ֹͣ��ʼ��Ч
		effect = caster.allEffects.get( "begin" )
		if effect:
			effect.stop()
			caster.allEffects.pop( "begin" )

		# ֹͣ��ʼ��Ч
		soundNames = caster.allEffects.get( "beginSound" )
		if soundNames:
			for name in soundNames:
				self.stopSound( caster, name )
			caster.allEffects.pop( "beginSound" )

	def playLoopEffects( self, caster, targetObject, skillID ):
		"""
		Play the LoopEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		# ����
		soundNames = rds.spellEffect.getSpellLoopSound( skillID )
		voiceNames = ()
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			gender = caster.getGender()
			if gender == csdefine.GENDER_MALE:
				voiceNames = rds.spellEffect.getSpellLoopVoice_Man( skillID )	# all voiceNames������������ by����
			else:
				voiceNames = rds.spellEffect.getSpellLoopVoice_Female( skillID )
			soundNames += voiceNames
		caster.allEffects["loopSound"] = soundNames
		for name in soundNames:
			self.playSound( caster, name )

		# ��Ч
		dict = rds.spellEffect.getLoopEffect( skillID, caster.id, caster.weaponType )
		if dict is None: return
		if targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION:
			#do some thing
			sk = skills.getSkill( skillID )		# CSOL-1724λ�ù�Ч������ʼ��Ч֧��
			if sk and sk.isTargetPositionSkill():
				effect = self.makeEffect( dict, caster, caster )
				if effect is None: return
				effect.start()
			else:
				effect = self.makeEffect( dict, caster, None )
				if effect is None: return
				if effect.__class__.__name__ == "PositionEffect":
					pos = targetObject.getObject()
					effect.setPosition( pos )
					effect.start()
				if effect.__class__.__name__ == "HomerParaParPosEffect":
					pos = targetObject.getObject()
					effect.onTargetPos( pos )
					effect.start()
		else:
			effect = self.makeEffect( dict, caster, targetObject.getObject() )
			if effect is None: return
			effect.start()
		caster.allEffects[ "loop" ] = effect

	def stopLoopEffects( self, caster ):
		"""
		Play the BeginEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		# ֹͣѭ����Ч
		effect = caster.allEffects.get( "loop" )
		if effect:
			effect.stop()
			caster.allEffects.pop( "loop" )
		# ֹͣѭ����Ч
		soundNames = caster.allEffects.get( "loopSound" )
		if soundNames:
			for name in soundNames:
				self.stopSound( caster, name )
			caster.allEffects.pop( "loopSound" )

	def playLinkEffect( self, caster, targetObject, skillID ):
		"""
		�������߹�Ч
		"""
		self.stopBeginEffects( caster )
		self.stopLoopEffects( caster )
		self.playCastSounds( caster, skillID )
		self.onAttackSound( caster )
		caster.allEffects = {}
		targetModels = []
		if targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITYPACKET:
			for target in targetObject.getObject():
				model = target.getModel()
				if model:
					targetModels.append( model )
		elif targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY:
			model = targetObject.getObject().getModel()
			if model: targetModels =  [ model ]
		else:
			targetModels = []
		dict = rds.spellEffect.getCastEffect( skillID, caster.id, caster.weaponType )
		if dict is None: return
		cModel = None
		tModel = None
		if caster: cModel = caster.getModel()
		type = caster.getParticleType()
		effect = self.createEffect( dict, cModel, targetModels, caster, type, type )
		if effect is None: return
		effect.start()

	def playCastEffects( self, caster, targetObject, skillID ):
		"""
		Play the CastEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		self.stopBeginEffects( caster )
		self.stopLoopEffects( caster )
		self.playCastSounds( caster, skillID )
		self.onAttackSound( caster )
		caster.allEffects = {}
		if targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION:
			#do some thing
			dict = rds.spellEffect.getCastEffect( skillID, caster.id, caster.weaponType )
			if dict is None: return
			effect = self.makeEffect( dict, caster, None )
			if effect is None: return
			if effect.__class__.__name__ == "PositionEffect":
				pos = targetObject.getObject()
				effect.setPosition( pos )
				effect.start()
			if effect.__class__.__name__ == "HomerParaParPosEffect":
				pos = targetObject.getObject()
				effect.onTargetPos( pos )
				effect.start()
		elif targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITYPACKET:
			for target in targetObject.getObject():
				self.startCastEffects( caster, target, skillID )
		elif targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY:
			self.startCastEffects( caster, targetObject.getObject(), skillID )

	def startCastEffects( self, caster, target, skillID ):
		"""
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		dict = rds.spellEffect.getCastEffect( skillID, caster.id, caster.weaponType )
		if dict is None: return
		effect = self.makeEffect( dict, caster, target )
		if effect is None: return
		if effect.__class__.__name__ in Const.HOMER_EFFECT_LIST:
			isShow = self.playBangOnEffects( caster, target, skillID )
			effect.setBangOnEffect( isShow )
		effect.start()

		sk = skills.getSkill( skillID )
		if sk and sk.isHomingSkill():
			caster.homingEffect = effect
		if  sk and sk.isMoveSpell():
			caster.movingEffect = effect
		else:
			caster.castEffect  = effect
		if effect.__class__.__name__ == "LinkEffect":
			caster.linkEffect.append( effect )
			target.linkEffect.append( effect )

	def stopCastEffects( self, caster ):
		if caster is None: return
		if not caster.inWorld: return
		if caster.castEffect:
			caster.castEffect.stop()
		for sound in caster.castSounds[:]:
			if sound is None:continue
			sound.stop()
			caster.castSounds.remove( sound )
		caster.castSounds = []

	def stopHomingEffects( self, caster ):
		"""
		��ֹ�ͷŹ�Ч
		@param caster	:	ʩչentity
		@type caster	:	entity
		"""
		if caster is None: return
		if not caster.inWorld: return
		if caster.homingEffect:
			caster.homingEffect.stop()

	def stopMovingEffects( self, caster ):
		"""
		��ֹ�ͷŹ�Ч
		@param caster	:	ʩչentity
		@type caster	:	entity
		"""
		if caster is None: return
		if not caster.inWorld: return
		if caster.movingEffect:
			caster.movingEffect.end()

	def playBuffEffects( self, caster, target, skillID ):
		"""
		����buffЧ��
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	BUffID
		@type skillID	:	Int
		"""
		target.buffEffect[skillID] = {}
		# ��Ч
		weaponType = 0
		casterID = 0
		if hasattr(caster,"weaponType"): weaponType = caster.weaponType
		if hasattr( caster,"id" ): casterID = caster.id
		dict = rds.spellEffect.getCastEffect( skillID, casterID, weaponType )
		if dict:
			effect = self.makeEffect( dict, caster, target )
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
			self.playSound( target, name )


	def stopBuffEffects( self, caster, target, skillID ):
		"""
		Play the BeginEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	BUffID
		@type skillID	:	Int
		"""
		buffEffect = target.buffEffect.get( skillID )
		if buffEffect:
			soundNames = buffEffect.get( "buff_sound" )
			if soundNames:
				for name in soundNames:
					self.stopSound( target, name )
			buffEffect = buffEffect.get( "buff_effect" )
			if buffEffect:
				buffEffect.stop()
			target.buffEffect.pop( skillID )

	def playHitEffects( self, caster, target, skillID ):
		"""
		Play the HitEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		# ����
		self.playHitSounds( caster, target, skillID )
		# ��Ч
		weaponType = 0
		casterID = 0
		if caster:
			weaponType = caster.weaponType
			casterID = caster.id

		dict = rds.spellEffect.getHitEffect( skillID, casterID, weaponType )
		if dict is None: return

		effectID = rds.spellEffect.getHitEffectID( skillID, weaponType )
		if effectID == "": return

		if not hasattr( target, "currHitEffectIDList" ):
			target.currHitEffectIDList = [ ( effectID, time.time() ) ]
		else:
			for i in target.currHitEffectIDList:
				if effectID == i[0]:
					if time.time() - i[1] > EFFECT_LIFE_TIME:
						target.currHitEffectIDList.remove( i )
						break
					else:
						return
			target.currHitEffectIDList.append( ( effectID, time.time() ) )

		effect = self.makeEffect( dict, caster, target )
		if effect is None: return

		if not hasattr( target, "currHitEffectList" ):
			target.currHitEffectList = [ ( effect, time.time() ) ]
		else:
			for i in target.currHitEffectList[:]:
				if time.time() - i[1] > EFFECT_LIFE_TIME:
					target.currHitEffectList.remove( i )
			target.currHitEffectList.append( ( effect, time.time() ) )
		if len( target.currHitEffectList ) > EFFECT_LIMIT_COUNT: return
		#��ʱ�Ų����ܻ���Ч
		effect.start()

	def playBangOnEffects( self, caster, target, skillID ):
		"""
		Play the BangOnEffects
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		weaponType = 0
		casterID = 0
		if caster:
			weaponType = caster.weaponType
			casterID = caster.id

		dict = rds.spellEffect.getCastEffect( skillID, casterID, weaponType )
		if dict is None: return False

		effectID = rds.spellEffect.getCastEffectID( skillID, weaponType )
		if effectID == "": return False

		if target is None: return False
		if not hasattr( target, "currBangOnEffectIDList" ):
			target.currBangOnEffectIDList = [ ( effectID, time.time() ) ]
		else:
			for i in target.currBangOnEffectIDList:
				if effectID == i[0]:
					if time.time() - i[1] > EFFECT_LIFE_TIME:
						target.currBangOnEffectIDList.remove( i )
						break
					else:
						return False
			target.currBangOnEffectIDList.append( ( effectID, time.time() ) )

		effect = self.makeEffect( dict, caster, target )
		if effect is None: return False

		if not hasattr( target, "currBangOnEffectList" ):
			target.currBangOnEffectList = [ ( effect, time.time() ) ]
		else:
			for i in target.currBangOnEffectList[:]:
				if time.time() - i[1] > EFFECT_LIFE_TIME:
					target.currBangOnEffectList.remove( i )
			target.currBangOnEffectList.append( ( effect, time.time() ) )
		if len( target.currBangOnEffectList ) > EFFECT_LIMIT_COUNT: return False
		return True

	def playSound( self, entity, soundName ):
		"""
		��������
		@param entity	:	�������ŵ�λ��
		@type entity	:	entity
		@param soundName:	�����ļ���Ӧ���ֶ���
		@type soundName	:	string
		"""
		if entity is None: return
		model = entity.getModel()
		if model is None: return
		soundMgr.playVocality( soundName, model )

	def stopSound( self, entity, soundName ):
		"""
		��������
		@param entity	:	�������ŵ�λ��
		@type entity	:	entity
		@param soundName:	�����ļ���Ӧ���ֶ���
		@type soundName	:	string
		"""
		soundMgr.stopVocality( soundName, entity.getModel() )

	def playCastSounds( self, caster, skillID ):
		"""
		������ͨ��������ʱ������
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		voiceNames = ()
		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			weaponType = caster.weaponType
			soundNames = rds.spellEffect.getNormalCastSound( weaponType )
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				gender = caster.getGender()
				if gender == csdefine.GENDER_MALE:
					voiceNames = rds.spellEffect.getNormalCastVoice_Man( weaponType )	# all voiceNames������������ by����
				else:
					voiceNames = rds.spellEffect.getNormalCastVoice_Female( weaponType )
				soundNames += voiceNames
		else:
			soundNames = rds.spellEffect.getSpellCastSound( skillID )
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				gender = caster.getGender()
				if gender == csdefine.GENDER_MALE:
					voiceNames = rds.spellEffect.getSpellCastVoice_Man( skillID )	# all voiceNames������������ by����
				else:
					voiceNames = rds.spellEffect.getSpellCastVoice_Female( skillID )
				soundNames += voiceNames
		model = caster.getModel()
		if model is None: return
		for name in soundNames:
			for sound in caster.castSounds[:]:
				if sound.name == name.split("/")[-1]:
					sound.stop()
					caster.castSounds.remove( sound )
			sound = soundMgr.playVocality( name, model )
			if sound is None:
				ERROR_MSG( "cast sound name(%s) error in skill(%s)." % ( name, skillID ) )
				continue
			caster.castSounds.append( sound )

	def playCameraEffects( self, caster, target, skillID ):
		"""
		���������Ч��
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		cameraEffectID = rds.spellEffect.getCameraEffectID( skillID )
		if cameraEffectID == 0: return

		type = rds.spellEffect.getCameraEffectType( cameraEffectID )
		if type == Define.CAMERA_SHAKE_NONE: return

		player = BigWorld.player()
		if player is None: return
		if not player.inWorld: return

		if type == Define.CAMERA_SHAKE_ONE_TYPE:
			if player.id == target.id:
				self.playCameraEffect( cameraEffectID )
		elif type == Define.CAMERA_SHAKE_AREA_TYPE:
			if player.position.flatDistTo( target.position ) <= Const.CAMERA_AREA_EFFECT_RADAIS:
				self.playCameraEffect( cameraEffectID )
		else:
			return

	def playCameraEffect( self, cameraEffectID ):
		"""
		����һ������ͷ��Ч��
		@type cameraEffectID	:	Int
		@param cameraEffectID	:	����ͷЧ��ID
		"""
		lastTime = rds.spellEffect.getCameraEffectLastTime( cameraEffectID )
		rangeShake = rds.spellEffect.getCameraEffectRangeShake( cameraEffectID )
		centerShake = rds.spellEffect.getCameraEffectCenterShake( cameraEffectID )
		rds.effectMgr.cameraShake( lastTime, rangeShake, centerShake )

	def playHitSounds( self, caster, target, skillID ):
		"""
		�����ܻ�ʱ������
		@param caster	:	ʩչentity
		@type caster	:	entity
		@param target	:	����entity
		@type target	:	entity
		@param skillID	:	����ID
		@type skillID	:	Int
		"""
		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			weaponType = caster.weaponType
			armorType = target.armorType
			soundName = rds.spellEffect.getNormalHitSound( weaponType, armorType )
			self.playSound( target, soundName )
		else:
			soundNames = rds.spellEffect.getSpellHitSound( skillID )
			for name in soundNames:
				self.playSound( target, name )

	def onAttackSound( self, caster ):
		"""
		������Ч by����
		"""
		if not caster.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnAttackSound( caster.modelNumber )	# ��ȡ������Ч
		if len( soundNames ) <= 0 :
			print "get monster AttackSound null"
			return
		soundName = random.choice( soundNames )
		caster.playSound( soundName )	# ���Ź�����Ч

	def interrupt( self, caster ):
		"""
		ֹͣ��Ч
		"""
		self.stopBeginEffects( caster )
		self.stopLoopEffects( caster )
		self.stopCastEffects( caster )
		caster.allEffects = {}

# ------------------------------------------------------------------------------------------------
# ��Ч���ͻ���
# ------------------------------------------------------------------------------------------------
class EffectBase:
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		self.dict = dict										# Ч�����ݶ�
		self.cModel = cModel									# Ч����ʼģ��
		self.tModel = tModel									# Ч������ģ��
		self.isPlaying = False									# ��ǰ����״̬
		self.visible = True										# ��ǰ��ʾ״̬
		self.sound = dict.get( "particle_sound", "" )			# ������������
		self.delayTime = dict.get( "particle_delaytime", 0.0 )	# �ӳٲ���ʱ��
		self.scale = dict.get( "particle_scale", 0.0 )			# ��Ч/��ͼ���ű���
		if not self.scale: self.scale = 1.0						# Ĭ�����ű���1.0
		self.scale = self.scale * scale
		pl = str( dict.get( "particle_lasttime", "0.0" )).split(";")
		self.lastTime = 0.0
		self.fadeOutTime = 2.0
		if len( pl ) > 0 and pl[ 0 ] != "":
			self.lastTime = float( pl[ 0 ] )	# ��������ʱ��
		if len( pl ) > 1 and pl[ 1 ] != "":
			self.fadeOutTime = float( pl[ 1 ] )	# ɾ��ʱ����ʱ��
		flora = dict.get( "particle_flora", "" ).split( ";" )
		self.flora = 0			# �Ƿ����ײ
		self.floraOnce = 0		# ֻ��ײһ��
		if len( flora ) > 0 and flora[0] != "":
			self.flora = int( flora[0] )
		if len( flora ) > 1 and flora[1] != "":
			self.floraOnce = int( flora[1] )
		floraDatas = dict.get( "particle_floraData", "" ).split( ";" )
		self.floraDis = 1.0		# ����ײ��Χ
		self.floraSpeed = 4.0	# �ݻζ��ٶ�
		self.floraTime = 4.0	# �ݻζ�ʱ��
		self.floraForce = 3.0	# ����ײ����
		if len( floraDatas ) > 0:
			try:
				self.floraDis = float( floraDatas[0] )
				self.floraSpeed = float( floraDatas[1] )
				self.floraTime = float( floraDatas[2] )
				self.floraForce = float( floraDatas[3] )
			except:
				pass
		self.cType = cType
		self.tType = tType

	def start( self ):
		"""
		��ʼ���Ź�Ч����
		"""
		self.isPlaying = True
		BigWorld.callback( self.delayTime, self.playAc )		# ���ӳ�ʱ��󲥷Ÿ����ӹ�Ч

	def playAc( self ):
		"""
		���Ź�Ч����
		"""
		if not self.isPlaying: return
		self.play()
		if self.lastTime == 0: return
		BigWorld.callback( self.lastTime, self.stop )			# �ڳ���ʱ���ֹͣ�����ӹ�Ч

	def play( self ):
		"""
		Virtual Method
		���Ź�Ч����
		"""
		self.playParticleSound()

	def stop( self ):
		"""
		Virtual Method
		ֹͣ��Ч����
		"""
		self.isPlaying = False
		self.fadeOut()
		BigWorld.callback( self.fadeOutTime, self.detach )

	def end( self ):
		"""
		ĳ����������µ���ֹ��Ч
		add by wuxo 2012-4-28
		"""
		pass

	def fadeOut( self ):
		"""
		Virtual Method
		������Ч����
		"""
		self.visible = False

	def fadeIn( self ):
		"""
		Virtual Method
		�����Ч����
		"""
		self.visible = True

	def detach( self ):
		"""
		Virtual Method
		�Ƴ���ЧЧ��
		"""
		self.stopParticleSound()

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return Define.TYPE_PARTICLE_PLAYER

	def getPlaySoundModel( self ):
		"""
		���ز��Ź�Ч����������ģ��
		"""
		return self.cModel

	def playParticleSound( self ):
		"""
		���Ź�Ч��������
		"""
		model = self.getPlaySoundModel()
		if model is None: return
		soundMgr.playVocality( self.sound, model )

	def stopParticleSound( self ):
		"""
		ֹͣ��Ч��������
		"""
		model = self.getPlaySoundModel()
		if model is None: return
		soundMgr.stopVocality( self.sound, model )

	def openFloraCollision( self, model ):
		"""
		��������ײ
		"""
		if model is None: return
		if not self.flora: return
		model.floraCollision = True
		model.floraCollisionDis = self.floraDis
		model.floraCollisionSpeed = self.floraSpeed
		model.floraCollisionTime = self.floraTime
		model.floraCollisionForce = self.floraForce
		functor = Functor( self.closeFloraCollision, model )
		if self.floraOnce:	# ֻ��һ����ײ
			BigWorld.callback( 0.01, functor )

	def closeFloraCollision( self, model ):
		"""
		�رղ���ײ
		"""
		if model is None: return
		model.floraCollision = False

# ------------------------------------------------------------------------------------------------
# �������Ч������
# ------------------------------------------------------------------------------------------------
class CameraEffect( EffectBase ):
	"""
	�������Ч��
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.cameraEffectID = dict.get("particle_cameraEffectID", 0 )   #�����Ч��ID

	def play( self ):
		"""
		������Ч��
		"""
		rds.skillEffect.playCameraEffect( self.cameraEffectID )

		EffectBase.play( self )

	def stop( self ):
		"""
		ֹͣ��Ч��
		"""
		rds.skillEffect.playCameraEffect( 0 )

		EffectBase.stop( self )

# ------------------------------------------------------------------------------------------------
# λ�ù�Ч����
# ------------------------------------------------------------------------------------------------
class PositionEffect( EffectBase ):
	"""
	ָ��λ�ò��Ź�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.position = dict.get( "particle_position", Math.Vector3() )		 		# ����λ��
		self.effectIDs = dict.get( "particle_posEffectIDs", "" ).split(";" )		# ���Ź�ЧID
		self.childEffects = []														# ���Ź�ЧID�б�
		self.model = None

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return self.cType

	def setPosition( self, pos ):
		"""
		���ö�̬λ��
		@param		pos		: λ��
		@type		pos		: Vector3
		"""
		self.position = pos

	def play( self ):
		"""
		���Ź�Ч
		"""
		rds.effectMgr.addModelBGWithPos( self.position, [Const.EMPTY_MODEL_PATH ], self.__onLoadModel )

		EffectBase.play( self )

	def __onLoadModel( self, model ):
		"""
		����ģ�ͻص�����
		@param		model		: ��Ч���ͷ�Դ
		@type		model		: model
		"""
		self.model = model

		for id in self.effectIDs:
			type = self.getType()
			effect = rds.skillEffect.createEffectByID( id, model, model, type, type )
			if effect is None: continue
			effect.start()
			self.childEffects.append( effect )

	def stop( self ):
		"""
		ж�ع�Ч
		"""
		for effect in self.childEffects:
			effect.stop()

		EffectBase.stop( self )

	def detach( self ):
		"""
		ж��ģ��
		"""
		player = BigWorld.player()
		if player is None: return

		if self.model in list( player.models ):
			player.delModel( self.model )

		EffectBase.detach( self )

# ------------------------------------------------------------------------------------------------
# λ����ͼ��Ч����
# ------------------------------------------------------------------------------------------------
class PictureEffect( EffectBase ):
	"""
	λ�ò�����ͼ��Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param sect			:	����Ч����������
		@type sect			:	sect
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		pictureDatas = dict.get("particle_picture","" ).split( ";" )
		self.picture = ""
		self.pictureColor = Math.Vector3( 1.0, 1.0, 1.0 )
		self.pictureFadeInTime = 0.0
		self.pictureFadeOutTime = 0.0
		if len( pictureDatas ) > 0 and pictureDatas[0] != "":	# ������ͼ·��
			self.picture = pictureDatas[0]
		if len( pictureDatas ) > 1 and pictureDatas[1] != "":	# ������ɫ��Ĭ��Ϊ��ɫ
			self.pictureColor = Math.Vector3( eval( pictureDatas[1] ) )
		if len( pictureDatas ) > 2 and pictureDatas[2] != "":	# ��������ʱ��
			self.pictureFadeInTime = float( pictureDatas[2] )
		if len( pictureDatas ) > 3 and pictureDatas[3] != "":	# ��������ʱ��
			self.pictureFadeOutTime = float( pictureDatas[3] )
		self.position = dict.get("particle_position",Math.Vector3() )
		self.index = BigWorld.decalTextureIndex( self.picture )
		self.animationRange = dict.get("particle_animationRange",Math.Vector2() )
		self.isTgaAnimation = dict.get("particle_isTgaAnimation",0)
		self.calIndex = -1
		self.tgaScale = 1
		self.lastSingleTime = 0
		self.quit = 0

	def getPosition( self ):
		"""
		���ز���Ч����λ��
		Virtual Method
		"""
		return self.position

	def setPosition( self, pos ):
		"""
		"""
		self.position = pos

	def getDir( self ):
		"""
		������ͼ�ĳ���
		Virtual Method
		"""
		return Math.Vector3()

	def play( self ):
		"""
		���Ź�Ч
		"""
		EffectBase.play( self )

		self.position = self.getPosition()
		self.pos1 = self.position + (0,2,0)
		self.pos2 = self.position + (0,-2,0)
		self.calIndex = BigWorld.addDecal( self.pos1, self.pos2, self.scale, self.index, self.getDir(), self.pictureColor, self.pictureFadeInTime )
		if self.isTgaAnimation:
			self.lastSingleTime = abs(self.animationRange[0] - self.animationRange[1]) *0.01
			lastTime = self.lastSingleTime
			self.tgaScale = self.animationRange[0]
			self.reduce( self.calIndex )

	def reduce( self, calIndex ) :
		"""
		��С
		"""
	  	BigWorld.deleteDecal( calIndex )
	  	if self.quit != 1:
	  		calIndex = BigWorld.addDecal( self.pos1, self.pos2, self.tgaScale, self.index, self.getDir(), self.pictureColor, self.pictureFadeInTime )
	  		self.tgaScale = self.tgaScale - 0.25
		  	Fun1 = Functor( self.reduce, calIndex )
		  	Fun2 = Functor( self.enlarge, calIndex )
		 	if self.tgaScale > self.animationRange[1]:
		 		BigWorld.callback( 0.01, Fun1 )
		 	else:
		 		BigWorld.callback( 0.01, Fun2 )

	def enlarge( self,calIndex ) :
		"""
		�Ŵ�
		"""
		BigWorld.deleteDecal( calIndex )
		if self.quit != 1:
	  		calIndex = BigWorld.addDecal( self.pos1, self.pos2, self.tgaScale, self.index, self.getDir(), self.pictureColor, self.pictureFadeInTime )
	  		self.tgaScale += 0.25
		  	Fun1 = Functor( self.reduce, calIndex )
		  	Fun2 = Functor( self.enlarge, calIndex )
		 	if self.tgaScale < self.animationRange[0]:
		 		BigWorld.callback( 0.01, Fun2 )
		 	else:
		 		BigWorld.callback( 0.01, Fun1 )

	def detach( self ):
		"""
		ж����Ч
		"""
		if self.isTgaAnimation:
			self.quit = 1
		BigWorld.deleteDecal( self.calIndex, self.pictureFadeOutTime )
		EffectBase.detach( self )

# ------------------------------------------------------------------------------------------------
# ����λ����ͼ��Ч����
# ------------------------------------------------------------------------------------------------
class SelfPictureEffect( PictureEffect ):
	"""
	����λ�ò�����ͼ��Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param sect			:	����Ч����������
		@type sect			:	sect
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		PictureEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getPosition( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		return self.cModel.position

	def getDir( self ):
		"""
		������ͼ�ĳ���
		Virtual Method
		"""
		yaw = self.cModel.yaw
		return Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )

# ------------------------------------------------------------------------------------------------
# Ŀ��λ����ͼ��Ч����
# ------------------------------------------------------------------------------------------------
class TargetPictureEffect( PictureEffect ):
	"""
	Ŀ��λ�ò�����ͼ��Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param sect			:	����Ч����������
		@type sect			:	sect
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		PictureEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getPosition( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		return self.tModel.position

	def getDir( self ):
		"""
		������ͼ�ĳ���
		Virtual Method
		"""
		yaw = self.tModel.yaw
		return Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )

	def getPlaySoundModel( self ):
		"""
		"""
		return self.tModel

# ------------------------------------------------------------------------------------------------
# ��������
# ------------------------------------------------------------------------------------------------
class ParticleEffect( EffectBase ):
	"""
	����Ч��
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.isStatic = dict.get( "particle_static", 0 )			# �Ƿ�̬Ч��
		self.particleSource = dict.get( "particle_source", "" )		# ���������ļ�
		self.hardPoint = dict.get( "particle_hardpoint", "" )		# ���ŵİ󶨵�
		self.part = dict.get( "particle_part", "" )					# ����ģ�ͱ���
		self.staticModel = None										# ��̬ģ��
		self.particle = None
		self.floraModel = None

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def play( self ):
		"""
		���Ź�Ч
		"""
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return

		if self.isStatic:
			rds.effectMgr.addModelBGInPos( model, self.hardPoint, [ Const.EMPTY_MODEL_PATH ], self.__onLoadModel )
		else:
			if self.flora:
				self.floraModel = BigWorld.Model( Const.EMPTY_MODEL_PATH )
				rds.effectMgr.attachObject( model, self.hardPoint, self.floraModel )
			rds.effectMgr.createParticleBG( model, self.hardPoint, self.particleSource, self.__onLoadParticle, type = self.getType(), scale = self.scale )

		EffectBase.play( self )

	def fadeOut( self ):
		"""
		������Ч
		"""
		EffectBase.fadeOut( self )
		rds.effectMgr.fadeOutParticle( self.particle )	# ��Ч������ʧ��ʽ

	def fadeIn( self ):
		"""
		�����Ч
		"""
		EffectBase.fadeIn( self )
		rds.effectMgr.fadeInParticle( self.particle )

	def __onLoadModel( self, model ):
		"""
		����ģ�ͻص�
		@param model		:	��Ч���ͷ�Դ
		@type model			:	pyModel
		"""
		self.staticModel = model
		if self.getModel():
			model.scale = self.getModel().scale

		if not self.isPlaying:
			self.stop()
			return

		if not self.visible: self.fadeOut()

		rds.effectMgr.createParticleBG( model, "HP_root", self.particleSource, self.__onLoadParticle, type = self.getType(), scale = self.scale )

	def __onLoadParticle( self, particle ):
		"""
		�ص��������������ں��̴߳�������֮��ص�
		���ǵ��첽�����⣬�����ʱ�����Ѿ��յ�ֹͣ����Ϣ
		������Ч
		@param particle		:	�ͷŵĹ�Ч
		@type particle		:	pyMetaParticle
		"""
		self.particle = particle

		self.openFloraCollision( self.floraModel )
		self.openFloraCollision( self.staticModel )

		if not self.isPlaying:
			self.stop()
			return

		if not self.visible: self.fadeOut()

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )

		if self.isStatic:
			player = BigWorld.player()
			if not player.inWorld: return
			if self.staticModel and ( self.staticModel in list( player.models ) ):
				player.delModel( self.staticModel )
				self.closeFloraCollision( self.staticModel )
		else:
			rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.particle )
			if self.floraModel:
				self.closeFloraCollision( self.floraModel )
				rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.floraModel )

		# �Ƴ����ģ������
		del self.staticModel
		self.staticModel = None
		del self.particle
		self.particle = None
		del self.floraModel
		self.floraModel = None

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getModel()

# ------------------------------------------------------------------------------------------------
# ������������
# ------------------------------------------------------------------------------------------------
class SelfParticleEffect( ParticleEffect ):
	"""
	�ͷ�Դ����Ч��
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		ParticleEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return self.cType

# ------------------------------------------------------------------------------------------------
# ����Ŀ������
# ------------------------------------------------------------------------------------------------
class TargetParticleEffect( ParticleEffect ):
	"""
	Ŀ��Դ����Ч��
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		ParticleEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.tModel, self.part )
		return self.tModel

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return self.tType

# ------------------------------------------------------------------------------------------------
# ��������
# ------------------------------------------------------------------------------------------------
class LoftEffect( EffectBase ):
	"""
	����Ч��
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# ���������ļ�
		self.hardPoint = dict.get( "particle_hardpoint", "" )		# ���ŵİ󶨵�
		self.part = dict.get( "particle_part", "" )					# ����ģ�ͱ���
		self.particle = None
		self.floraModel = None

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return self.cType

	def play( self ):
		"""
		���ŵ���
		"""
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return

		if self.flora:
			self.floraModel = BigWorld.Model( Const.EMPTY_MODEL_PATH )
			rds.effectMgr.attachObject( model, self.hardPoint, self.floraModel )
		rds.effectMgr.createParticleBG( model, self.hardPoint, self.particleSource, self.__onLoadParticle, type = self.getType(), scale = self.scale )
		EffectBase.play( self )

	def fadeOut( self ):
		"""
		������Ч
		"""
		EffectBase.fadeOut( self )
		if self.particle:
			system = self.particle.system(0)
			if system:
				system.renderer.stop()

	def fadeIn( self ):
		"""
		�����Ч
		"""
		EffectBase.fadeIn( self )
		if self.particle:
			self.particle.system(0).renderer.start()

	def __onLoadParticle( self, particle ):
		"""
		�ص��������������ں��̴߳�������֮��ص�
		���ǵ��첽�����⣬�����ʱ�����Ѿ��յ�ֹͣ����Ϣ
		������Ч
		@param particle		:	�ͷŵĹ�Ч
		@type particle		:	pyMetaParticle
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

		self.openFloraCollision( self.floraModel )

		if self.particle:
			self.particle.system(0).renderer.start()

		if not self.visible:
			self.particle.system(0).renderer.stop()

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )
		rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.particle )
		if self.floraModel:
			self.closeFloraCollision( self.floraModel )
			rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.floraModel )
		# �Ƴ����ģ������
		del self.particle
		self.particle = None
		del self.floraModel
		self.floraModel = None

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getModel()

# ------------------------------------------------------------------------------------------------
# ������������
# ------------------------------------------------------------------------------------------------
class SelfLoftEffect( LoftEffect ):
	"""
	�������൶���Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		LoftEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

# ------------------------------------------------------------------------------------------------
# ģ������
# ------------------------------------------------------------------------------------------------
class ModelEffect( EffectBase ):
	"""
	ģ�͹�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = dict.get( "particle_msource", "" )					# ģ������
		self.hardPoint = dict.get( "particle_hardpoint", "" )					# ���ŵİ󶨵�
		self.isStatic = dict.get( "particle_static", 0 )						# �Ƿ�̬
		self.part = dict.get( "particle_part", "" )								# ����ģ�ͱ���
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )	# ģ�͸�������
		self.modelFadeInTime = dict.get( "particle_modelfadeintime", 0.0 )		# ģ�ͽ���ʱ��
		self.modelFadeTime = dict.get( "particle_modelfadetime", 0.0 )			# ģ�ͽ���ʱ��
		self.model = None

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def play( self ):
		"""
		���Ź�Ч
		"""
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return

		if self.isStatic:
			rds.effectMgr.addModelBGInPos( model, self.hardPoint, [ self.modelSource ], self.__onLoadModel )
		else:
			rds.effectMgr.createModelBG( [self.modelSource], self.__onLoadModel )

		EffectBase.play( self )

	def __onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		self.model = model
		model.scale = ( self.scale, self.scale, self.scale )							# ����ģ��

		if not self.isPlaying:
			self.stop()
			return

		# ����ģ�͵ĳ���
		if self.cModel and self.tModel:
			yaw = utils.yawFromPos( self.cModel.position, self.tModel.position )
			if self.model: self.model.yaw = yaw

		if not self.isStatic:
			rds.effectMgr.attachObject( self.getModel(), self.hardPoint, model )		# ���ͷ��߼���ģ�͹�Ч
		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( model, self.modelFadeInTime )					# ����ģ��
		if model.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( model, Const.MODEL_ACTION_PLAY )					# ����

		self.openFloraCollision( model )

		if not self.visible:  self.fadeOut()

		for effectID in self.attachEffects:											# �ں��̴߳���ģ�͵ĸ��ӹ�Ч
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# ��ȡ��������
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.cModel, self.cType, self.tType )	# ����Ч��ʵ��
			if particlesEffect is None: continue
			particlesEffect.start()													# ����Ч��
			if not self.visible: particlesEffect.fadeOut()

	def fadeOut( self ):
		"""
		������Ч
		"""
		EffectBase.fadeOut( self )
		if self.model is None: return
		# ���ӹ�Ч����
		self.model.visibleAttachments = True
		rds.effectMgr.fadeOutModelAttachments( self.model )
		# ����ģ��
		rds.effectMgr.fadeOutModel( self.model, self.modelFadeTime )

	def fadeIn( self ):
		"""
		�����Ч
		"""
		EffectBase.fadeIn( self )
		if self.model is None: return
		# ���ӹ�Ч����
		self.model.visibleAttachments = False
		rds.effectMgr.fadeInModelAttachments( self.model )
		# ����ģ��
		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( self.model, self.modelFadeInTime )

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )
		player = BigWorld.player()
		if not player.inWorld: return

		self.closeFloraCollision( self.model )
		if self.isStatic:
			if self.model and ( self.model in list( player.models ) ):
				player.delModel( self.model )
		else:
			rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.model )

		# �Ƴ����ģ������
		del self.model
		self.model = None

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getModel()

# ------------------------------------------------------------------------------------------------
# ģ����������
# ------------------------------------------------------------------------------------------------
class SelfModelEffect( ModelEffect ):
	"""
	��������ģ�͹�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		ModelEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

# ------------------------------------------------------------------------------------------------
# ģ��Ŀ������
# ------------------------------------------------------------------------------------------------
class TargetModelEffect( ModelEffect ):
	"""
	Ŀ�겥����ģ�͹�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		ModelEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.tModel, self.part )
		return self.tModel

# ------------------------------------------------------------------------------------------------
# ��������
# ------------------------------------------------------------------------------------------------
class HomerEffect( EffectBase ):
	"""
	���й�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = Const.EMPTY_MODEL_PATH
		self.hardPoint = dict.get( "particle_hardpoint", "" )			# ���ӷɳ�ȥ�İ󶨵�
		self.homerSpring = dict.get( "particle_spring", "" )			# ����Ŀ�������Ч
		self.homerHitPoint = dict.get( "particle_hitpoint", "" )		# ���л���Ŀ���
		self.homer = BigWorld.Homer()
		fl = str( dict.get( "particle_flyspeed", "" ) ).split(";")
		t= float( fl[0] )
		self.homer.speed = t if t else 0.0 						# �����ٶ�
		if len(fl)<2:
			self.homer.turnAxis = ( 0, 0, 1 )
		else:self.homer.turnAxis = ( 0, 0, 0 )
		self.homer.proximity = 0.36
		self.homer.turnRate = 314.159
		self.homerModel = None
		self.isReverse = dict.get( "particle_reverse", 0 )			# �������
		self.part = dict.get( "particle_part", "" )
		self.playBangOnEffect = True

	def getTModel( self ):
		"""
		���Ŀ��ģ��
		"""
		if self.isReverse: return self.cModel
		return self.tModel

	def getCModel( self ):
		"""
		�����ʼģ��
		"""
		if self.isReverse: model = self.tModel
		else: model = self.cModel
		if len( self.part ):
			return rds.effectMgr.getLinkObject( model, self.part )
		return model

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return self.cType

	def setBangOnEffect( self, isShow ):
		"""
		"""
		self.playBangOnEffect = isShow

	def getBangOnEffect( self ):
		"""
		"""
		return self.playBangOnEffect

	def play( self ):
		"""
		Virtual Method
		���ŷ��й�Ч
		"""
		cModel = self.getCModel()
		if cModel is None: return
		if not cModel.inWorld: return
		rds.effectMgr.addModelBGInPos( cModel, self.hardPoint, [self.modelSource], self.onLoadModel )
		EffectBase.play( self )

	def onBang( self ):
		"""
		����Ч������Ŀ���
		"""
		self.stop()
		self.homer.target = None
		self.homer.proximityCallback = None
		self.onBangOver()

		# �ɵ�Ŀ�괥��Ч��
		bangSect = rds.spellEffect.getEffectConfigSect( self.homerSpring )
		if bangSect is None: return
		bangOnEffect = createSuitableEffect( bangSect, self.getCModel(), self.getTModel(), self.cType, self.tType )
		if bangOnEffect is None: return
		if not self.getBangOnEffect(): return
		bangOnEffect.start()

	def onBangOver( self ):
		"""
		����Ч������Ŀ���
		���������Ч����fadeOut��һ����
		���ֿ�����Ŀ������Ϊ����Ч���ڷɳ�ȥû����Ŀ��ǰ�ǲ�����ֹ�ġ�
		"""
		# ����֮���������ջء�
		# ����Ч��ֻ���ڷɵ�Ŀ����ܽ�����
		if self.homerModel:
			self.homerModel.visible = False
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )

	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		self.homerModel = model
		if model is None:
			self.stop()
			self.onBangOver()
			return

		if not self.isPlaying:
			self.stop()
			self.onBangOver()
			return

		# ���÷��й�Ч��Ŀ���
		hitPoint = rds.effectMgr.accessNode( self.getTModel(), self.homerHitPoint )
		if hitPoint is None:
			self.stop()
			self.onBangOver()
			return

		self.openFloraCollision( self.homerModel )
		self.homerModel.addMotor( self.homer )
		self.homer.target = hitPoint
		self.homer.proximityCallback = self.onBang				# ���÷��й�Ч����Ŀ���callback ����
		if self.homerModel.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( self.homerModel, Const.MODEL_ACTION_PLAY )					# ����

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )
		player = BigWorld.player()
		if ( player is None ) or ( not player.inWorld ): return
		if self.homerModel and ( self.homerModel in list( player.models ) ):
			player.delModel( self.homerModel )
			self.closeFloraCollision( self.homerModel )
		self.homerModel = None

	def end( self ):
		"""
		��������µ���ֹ��Ч
		"""
		self.isPlaying = False
		self.homer.speed = 0.0
		self.homer.target = None
		self.homer.proximityCallback = None
		self.detach()

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getCModel()

# ------------------------------------------------------------------------------------------------
# ���ӷ�������
# ------------------------------------------------------------------------------------------------
class HomerParticleEffect( HomerEffect ):
	"""
	���й�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		HomerEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# ���и�������Ч��
		self.particle = None

	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale

		HomerEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return
		rds.effectMgr.createParticleBG( model, "HP_root", self.particleSource, self.__onLoadParticle, type = self.getType(), scale = self.scale )

	def __onLoadParticle( self, particle ):
		"""
		���Ӽ��ػص�
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

# ------------------------------------------------------------------------------------------------
# ģ�ͷ�������
# ------------------------------------------------------------------------------------------------
class HomerModelEffect( HomerEffect ):
	"""
	����ģ�͹�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		HomerEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = dict.get( "particle_msource", "" )							# ���и�������Ч��
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )			# ģ�͸�������
		self.modelFadeInTime = dict.get( "particle_modelfadeintime", 0.0 )				# ģ�ͽ���ʱ��
		self.modelFadeTime = dict.get( "particle_modelfadetime", 0.0 )					# ģ�ͽ���ʱ��

	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale * self.scale

		HomerEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return

		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( model, self.modelFadeInTime )
		for effectID in self.attachEffects:											# �ں��̴߳���ģ�͵ĸ��ӹ�Ч
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# ��ȡ��������
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.getTModel(), self.cType, self.tType )	# ����Ч��ʵ��
			if particlesEffect is None: continue
			particlesEffect.start()

	def onBangOver( self ):
		"""
		����Ч������Ŀ���
		���������Ч����fadeOut��һ����
		���ֿ�����Ŀ������Ϊ����Ч���ڷɳ�ȥû����Ŀ��ǰ�ǲ�����ֹ�ġ�
		"""
		# ����֮���������ջء�
		# ����Ч��ֻ���ڷɵ�Ŀ����ܽ�����
		if self.homerModel:
			rds.effectMgr.fadeOutModel( self.homerModel, self.modelFadeTime )
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )

# ------------------------------------------------------------------------------------------------
# �����߷�������
# ------------------------------------------------------------------------------------------------
class HomerParabolaEffect( EffectBase ):
	"""
	�����߷��й�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = Const.EMPTY_MODEL_PATH
		self.hardPoint = dict.get( "particle_hardpoint", "" )			# ���ӷɳ�ȥ�İ󶨵�
		self.homerSpring = dict.get( "particle_spring", "" )			# ����Ŀ�������Ч
		self.homerHitPoint = dict.get( "particle_hitpoint", "" )		# ���л���Ŀ���
		self.homer = BigWorld.CurveHomer()
		self.homer.speed = float( dict.get( "particle_flyspeed", 0.0 )	)		# �����ٶ�
		self.homer.proximity = 0.3
		self.homerModel = None
		self.isReverse = dict.get( "particle_reverse", 0 )				# �������
		self.part = dict.get( "particle_part", "" )
		self.homerAngle = dict.get( "particle_homerAngle", 0.0 )		# ���нǶ�
		self.casterPos = Math.Vector3()
		self.targetPos = Math.Vector3()
		self.playBangOnEffect = True

	def getTModel( self ):
		"""
		���Ŀ��ģ��
		"""
		if self.isReverse: return self.cModel
		return self.tModel

	def getCModel( self ):
		"""
		�����ʼģ��
		"""
		if self.isReverse: model = self.tModel
		else: model = self.cModel
		if len( self.part ):
			return rds.effectMgr.getLinkObject( model, self.part )
		return model

	def getType( self ):
		"""
		�������Ӽ�������
		"""
		return self.cType

	def setBangOnEffect( self, isShow ):
		"""
		"""
		self.playBangOnEffect = isShow

	def getBangOnEffect( self ):
		"""
		"""
		return self.playBangOnEffect

	def play( self ):
		"""
		Virtual Method
		���ŷ��й�Ч
		"""
		cModel = self.getCModel()
		if cModel is None: return
		if not cModel.inWorld: return
		rds.effectMgr.addModelBGInPos( cModel, self.hardPoint, [self.modelSource], self.onLoadModel )
		EffectBase.play( self )

	def onBang( self ):
		"""
		����Ч������Ŀ���
		"""
		self.stop()
		self.homer.target = None
		self.homer.proximityCallback = None
		self.onBangOver()

		# �ɵ�Ŀ�괥��Ч��
		bangSect = rds.spellEffect.getEffectConfigSect( self.homerSpring )
		if bangSect is None: return
		bangOnEffect = createSuitableEffect( bangSect, self.getCModel(), self.getTModel(), self.cType, self.tType )
		if bangOnEffect is None: return
		if not self.getBangOnEffect(): return
		bangOnEffect.start()

	def onBangOver( self ):
		"""
		����Ч������Ŀ���
		���������Ч����fadeOut��һ����
		���ֿ�����Ŀ������Ϊ����Ч���ڷɳ�ȥû����Ŀ��ǰ�ǲ�����ֹ�ġ�
		"""
		# ����֮���������ջء�
		# ����Ч��ֻ���ڷɵ�Ŀ����ܽ�����
		if self.homerModel:
			self.homerModel.visible = False
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )

	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		self.homerModel = model
		if model is None:
			self.stop()
			self.onBangOver()
			return

		if not self.isPlaying:
			self.stop()
			self.onBangOver()
			return

		self.onPlay()

	def onPlay( self ):
		"""
		"""
		self.casterPos = rds.effectMgr.accessNodePos( self.getCModel(), self.hardPoint )
		self.targetPos = rds.effectMgr.accessNodePos( self.getTModel(), self.homerHitPoint )

		dir = self.targetPos - self.casterPos
		len = dir.length/2.0
		dir.normalise()
		self.homerAngle = int( self.homerAngle )
		if self.homerAngle < 3:  # �ǶȲ��ܹ���
			self.stop()
			self.onBangOver()
			ERROR_MSG("The homerAngle is wrong!")
 			return
		pos = self.casterPos + len * dir + Math.Vector3( 0, 1, 0 )
		self.homer.reset()
		self.homer.setCtrlPt( [self.casterPos, pos, self.targetPos], self.homerAngle )
		self.homer.turn = 1
		self.homer.turnAxis = ( 0, 0, 1 )

		# ���÷��й�Ч��Ŀ���
		hitPoint = rds.effectMgr.accessNode( self.getTModel(), self.homerHitPoint )
		if hitPoint is None:
			self.stop()
			self.onBangOver()
			return

		if self.homerModel is None:
			self.stop()
			self.onBangOver()
			return

		self.openFloraCollision( self.homerModel )
		self.homerModel.addMotor( self.homer )
		self.homer.target = hitPoint
		self.homer.proximityCallback = self.onBang 		# ���÷��й�Ч����Ŀ���callback ����
		if self.homerModel.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( self.homerModel, Const.MODEL_ACTION_PLAY )					# ����

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )
		player = BigWorld.player()
		if ( player is None ) or ( not player.inWorld ): return
		if self.homerModel and ( self.homerModel in list( player.models ) ):
			player.delModel( self.homerModel )
			self.closeFloraCollision( self.homerModel )
		self.homerModel = None
		self.casterPos = Math.Vector3()
		self.targetPos = Math.Vector3()

	def end( self ):
		"""
		��������µ���ֹ��Ч
		"""
		self.isPlaying = False
		self.homer.speed = 0.0
		self.homer.target = None
		self.homer.proximityCallback = None
		self.detach()

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getCModel()

# ------------------------------------------------------------------------------------------------
# ���������߷�������
# ------------------------------------------------------------------------------------------------
class HomerParabolaParticleEffect( HomerParabolaEffect ):
	"""
	���������߷��й�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		HomerParabolaEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# ���и�������Ч��
		self.particle = None

	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale

		HomerParabolaEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return
		rds.effectMgr.createParticleBG( model, "HP_root", self.particleSource, self.__onLoadParticle, type = self.getType(), scale = self.scale )

	def __onLoadParticle( self, particle ):
		"""
		���Ӽ��ػص�
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

class HomerParaParPosEffect( HomerParabolaEffect ):
	"""
	���������߷��й�Ч���λ��
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		HomerParabolaEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# ���и�������Ч��
		self.particle = None
		
	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale

		HomerParabolaEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return
		rds.effectMgr.createParticleBG( model, "HP_root", self.particleSource, self.__onLoadParticle, type = self.getType(), scale = self.scale )

	def __onLoadParticle( self, particle ):
		"""
		���Ӽ��ػص�
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

	def onTargetPos( self, pos ):
		"""
		"""
		self.targetPos = Math.Vector3( pos  )

	def getTModel( self ):
		return None

	def getCModel( self ):
		"""
		���Ŀ��ģ��
		"""
		model = self.cModel
		if len( self.part ):
			return rds.effectMgr.getLinkObject( model, self.part )
		return model

	def onPlay( self ):
		"""
		"""
		self.casterPos = rds.effectMgr.accessNodePos( self.getCModel(), self.hardPoint )

		dir = self.targetPos - self.casterPos
		len = dir.length/2.0
		dir.normalise()
		self.homerAngle = int( self.homerAngle )
		if self.homerAngle < 3:  # �ǶȲ��ܹ���
			self.stop()
			self.onBangOver()
			ERROR_MSG("The homerAngle is wrong!")
			return
		pos = self.casterPos + len * dir + Math.Vector3( 0, 1, 0 )
		self.homer.reset()
		self.homer.setCtrlPt( [self.casterPos, pos, self.targetPos], self.homerAngle )
		self.homer.turn = 1
		self.homer.turnAxis = ( 0, 0, 1 )

		# ���÷��й�Ч��Ŀ���
		hitPoint = Math.Matrix()
		hitPoint.setTranslate( self.targetPos )

		if self.homerModel is None:
			self.stop()
			self.onBangOver()
			return

		self.openFloraCollision( self.homerModel )
		self.homerModel.addMotor( self.homer )
		self.homer.target = hitPoint
		self.homer.proximityCallback = self.onBang 		# ���÷��й�Ч����Ŀ���callback ����
		if self.homerModel.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( self.homerModel, Const.MODEL_ACTION_PLAY )

	def onBang( self ):
		"""
		����Ч������Ŀ���
		"""
		self.stop()
		self.homer.target = None
		self.homer.proximityCallback = None
		self.onBangOver()

		# �ɵ�Ŀ�괥��Ч��
		bangSect = rds.spellEffect.getEffectConfigSect( self.homerSpring )
		if bangSect is None: return
		bangOnEffect = createSuitableEffect( bangSect, self.getCModel(), self.getTModel(), self.cType, self.tType )
		if bangOnEffect is None: return
		if not self.getBangOnEffect(): return
		if bangOnEffect.__class__.__name__ == "PositionEffect":
			bangOnEffect.setPosition( self.targetPos )
			bangOnEffect.start()
# ------------------------------------------------------------------------------------------------
# ģ�������߷�������
# ------------------------------------------------------------------------------------------------
class HomerParabolaModelEffect( HomerParabolaEffect ):
	"""
	ģ�������߷��й�Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		HomerParabolaEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = dict.get( "particle_msource", "" )							# ���и�������Ч��
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )			# ģ�͸�������
		self.modelFadeInTime = dict.get( "particle_modelfadeintime", 0.0 )				# ģ�ͽ���ʱ��
		self.modelFadeTime = dict.get( "particle_modelfadetime", 0.0 )					# ģ�ͽ���ʱ��

	def onLoadModel( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale * self.scale

		HomerParabolaEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return

		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( model, self.modelFadeInTime )
		for effectID in self.attachEffects:											# �ں��̴߳���ģ�͵ĸ��ӹ�Ч
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# ��ȡ��������
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.getTModel(), self.cType, self.tType )	# ����Ч��ʵ��
			if particlesEffect is None: continue
			particlesEffect.start()

	def onBangOver( self ):
		"""
		����Ч������Ŀ���
		���������Ч����fadeOut��һ����
		���ֿ�����Ŀ������Ϊ����Ч���ڷɳ�ȥû����Ŀ��ǰ�ǲ�����ֹ�ġ�
		"""
		# ����֮���������ջء�
		# ����Ч��ֻ���ڷɵ�Ŀ����ܽ�����
		if self.homerModel:
			rds.effectMgr.fadeOutModel( self.homerModel, self.modelFadeTime )
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )


# ------------------------------------------------------------------------------------------------
# ���Ϲ�Ч����
# ------------------------------------------------------------------------------------------------
class ComplexParticleEffect( EffectBase ):
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.childEffect = []
		for i in xrange( 1, 9 ):
			value = dict["particle_child" + str( i )]
			if value == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( value )
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, cModel, tModel, cType, tType, self.scale )
			if particlesEffect is None: continue
			self.childEffect.append( particlesEffect )

	def play( self ):
		"""
		Virtual Method
		"""
		for effect in self.childEffect:
			effect.start()
		EffectBase.play( self )

	def stop( self ):
		"""
		Virtual Method
		"""
		for effect in self.childEffect:
			effect.stop()
		EffectBase.stop( self )

	def fadeOut( self ):
		"""
		������Ч����
		"""
		EffectBase.fadeOut( self )
		for effect in self.childEffect:
			effect.fadeOut()

	def fadeIn( self ):
		"""
		�����Ч����p
		"""
		EffectBase.fadeIn( self )
		for effect in self.childEffect:
			effect.fadeIn()

class LinkEffect( EffectBase ):
	"""
	�������ӹ�Ч������WOW��DK������֮��/ ���� / ��Ѫ�ļ��ܵ���Ч��
	by wuxo 2012-5-11
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.isStatic = dict.get( "particle_static", 0 )			# �Ƿ�̬Ч��
		self.particleSource = dict.get( "particle_source", "" )		# ���������ļ�
		self.hardPoint = dict.get( "particle_hardpoint", "" )		# �����ߵ�������ʼ��
		self.part = dict.get( "particle_part", "" )					# ����ģ�ͱ���
		self.staticModel = None										# ��̬ģ��
		self.particle = None
		hitpoint = dict.get( "particle_hitpoint", "" ).split(":")          #�����ߵ�����Ŀ���
		if len( hitpoint ) == 1:
			self.hitPoint = hitpoint[0]
			self.tModel = [self.tModel]
		elif len( hitpoint ) == 2:
			self.hitPoint = hitpoint[0]
			if int( hitpoint[1] ) == 1:  #��ʾhitpointΪ����İ󶨵�
				self.tModel = [self.cModel]
			else:
				self.tModel = [self.tModel]
		
		self.floraModel = None

	def getModel( self ):
		"""
		���ز���Ч����ģ��
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def play( self ):
		"""
		���Ź�Ч
		"""
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return

		if self.isStatic:
			rds.effectMgr.addModelBGInPos( model, self.hardPoint, [ Const.EMPTY_MODEL_PATH ], self.__onLoadModel )
		else:
			if self.flora:
				self.floraModel = BigWorld.Model( Const.EMPTY_MODEL_PATH )
				rds.effectMgr.attachObject( model, self.hardPoint, self.floraModel )
			rds.effectMgr.createParticleBG( model, self.hardPoint, self.particleSource, self.__onLoadParticle, scale = self.scale )

		EffectBase.play( self )

	def fadeOut( self ):
		"""
		������Ч
		"""
		EffectBase.fadeOut( self )
		if self.particle:
			rds.effectMgr.fadeOutParticle( self.particle )	# ��Ч������ʧ��ʽ

	def fadeIn( self ):
		"""
		�����Ч
		"""
		EffectBase.fadeIn( self )
		if self.particle:
			rds.effectMgr.fadeInParticle( self.particle )

	def __onLoadModel( self, model ):
		"""
		����ģ�ͻص�
		@param model		:	��Ч���ͷ�Դ
		@type model			:	pyModel
		"""
		self.staticModel = model
		if self.getModel():
			model.scale = self.getModel().scale

		if not self.isPlaying:
			self.stop()
			return

		if not self.visible: self.fadeOut()

		rds.effectMgr.createParticleBG( model, "HP_root", self.particleSource, self.__onLoadParticle, scale = self.scale )

	def __onLoadParticle( self, particle ):
		"""
		�ص��������������ں��̴߳�������֮��ص�
		���ǵ��첽�����⣬�����ʱ�����Ѿ��յ�ֹͣ����Ϣ
		������Ч
		@param particle		:	�ͷŵĹ�Ч
		@type particle		:	pyMetaParticle
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

		if not self.visible: self.fadeOut()
		hitPoint = self.getAllHitPoint()

		if self.particle:
			for i in range( self.particle.nSystems() ):
				try:
					action = self.particle.system(i).action( SOURCE_MATRIX_SWARM )
				except:
					action = None
				if action:
					action.targets = hitPoint

		self.openFloraCollision( self.floraModel )
		self.openFloraCollision( self.staticModel )

	def getAllHitPoint( self ):
		hitPoint = []
		for model in self.tModel:
			node = rds.effectMgr.accessNode( model, self.hitPoint )
			hitPoint.append( node )
		return hitPoint

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )

		if self.particle:
			for i in range( self.particle.nSystems() ):
				try:
					action = self.particle.system(i).action( SOURCE_MATRIX_SWARM )
				except:
					action = None
				if action:
					action.targets = []

		if self.isStatic:
			player = BigWorld.player()
			if not player.inWorld: return
			if self.staticModel and ( self.staticModel in list( player.models ) ):
				player.delModel( self.staticModel )
				self.closeFloraCollision( self.staticModel )
		else:
			rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.particle )
			if self.floraModel:
				self.closeFloraCollision( self.floraModel )
				rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.floraModel )

		# �Ƴ����ģ������
		del self.staticModel
		self.staticModel = None
		del self.particle
		self.particle = None
		del self.floraModel
		self.floraModel = None

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getModel()

class DisColorEffect( EffectBase ):
	"""
	��ɫ��Ч
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	����Ч����������
		@type dict			:	dict
		@param cModel		:	��Ч���ͷ�Դ
		@type cModel		:	pyModel
		@param tModel		:	��Ч�Ľ���Դ
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.color = eval( dict.get( "particle_source", "()" ))	# ��ɫ��Ч��ɫ
		self.fadeInTime = dict.get( "particle_modelfadeintime", 0.0 )     #��ɫ���뵭��ʱ��

	def play( self ):
		"""
		���Ź�Ч
		"""
		if len( self.color ) == 0: return
		model = self.tModel
		srcColor = (1.0,1.0,1.0,1.0)
		rds.effectMgr.setModelColor( model, srcColor, self.color, self.fadeInTime )
		EffectBase.play( self )

	def detach( self ):
		"""
		ж����Ч
		"""
		EffectBase.detach( self )
		if len( self.color ) > 0:
			model = self.tModel
			rds.effectMgr.setModelColor( model, self.color, (1.0,1.0,1.0,1.0), self.fadeInTime )

	def getPlaySoundModel( self ):
		"""
		"""
		return self.tModel

EFFECT_CLASSES = {
	"CameraEffect"					:		CameraEffect,
	"PositionEffect"				:		PositionEffect,
	"SelfParticleEffect"			:		SelfParticleEffect,
	"TargetParticleEffect"			:		TargetParticleEffect,
	"HomerParticleEffect"			:		HomerParticleEffect,
	"SelfModelEffect"				:		SelfModelEffect,
	"TargetModelEffect"				:		TargetModelEffect,
	"HomerModelEffect"				:		HomerModelEffect,
	"ComplexParticleEffect"			:		ComplexParticleEffect,
	"SelfLoftEffect"				:		SelfLoftEffect,
	"PictureEffect"					:		PictureEffect,
	"SelfPictureEffect" 			:		SelfPictureEffect,
	"TargetPictureEffect"			:		TargetPictureEffect,
	"LinkEffect"					:		LinkEffect,
	"HomerParabolaParticleEffect"	:		HomerParabolaParticleEffect,
	"HomerParabolaModelEffect"		:		HomerParabolaModelEffect,
	"DisColorEffect"				:		DisColorEffect,
	"HomerParaParPosEffect"			:		HomerParaParPosEffect,
}

def createSuitableEffect( dict, cModel, tModel, cType = Define.TYPE_PARTICLE_PLAYER, tType = Define.TYPE_PARTICLE_PLAYER, scale = 1.0 ):
	try:
		className = dict["particle_type"]
		return EFFECT_CLASSES[className]( dict, cModel, tModel, cType, tType, scale )
	except Exception, e:
		WARNING_MSG( e )
		return None

#
# $Log: not supported by cvs2svn $
# Revision 1.20  2008/08/25 10:05:02  yangkai
# no message
#
# Revision 1.19  2008/08/25 10:00:46  yangkai
# ���3��ģ�͹�Ч����
#
# Revision 1.18  2008/08/06 04:04:12  yangkai
# ������Ҳ�����Դ�ļ��ĳ�����ʾ
#
# Revision 1.17  2008/07/28 09:11:10  yangkai
# no message
#
# Revision 1.16  2008/07/28 08:43:28  yangkai
# 1�������˹�Ч���Ϳ��
# 2������˾�̬��Ч��֧��
#
# Revision 1.15  2008/07/23 05:39:03  yangkai
# no message
#
# Revision 1.14  2008/07/22 09:01:11  yangkai
# 1������Ŀ���HP_hitPoint�㣬������й�Ч���е��λ��ƫ��
# 2������������ã���ֹ��������
#
# Revision 1.13  2008/07/15 04:08:01  kebiao
# �����������޸ĵ�datatool��س�ʼ����Ҫ�޸�
#
# Revision 1.12  2008/07/08 09:20:09  yangkai
# ������ ��Ч���ü��ط�ʽ
#
# Revision 1.11  2008/07/05 08:36:34  yangkai
# �����ͨ����ʩչ��Ч�Ĵ���
#
# Revision 1.10  2008/04/24 08:40:32  phw
# method modified: TargetParticleEffect::start(), ��Ч�ı����㷨������
#
# Revision 1.9  2008/03/27 07:13:48  yangkai
# ��ӽӿ� playHitSounds �����ܻ�ʱ������
#
# Revision 1.8  2008/03/25 03:34:31  yangkai
# ��ӽӿ� interrupt
#
# Revision 1.7  2008/03/06 08:33:03  yangkai
# ��Ч������Ӵ�����Ч
#
# Revision 1.6  2008/01/30 07:19:05  yangkai
# ���Ϲ�Ч�ӹ�Ч��Ŀ֧��8��
#
# Revision 1.5  2008/01/25 10:41:51  huangyongwei
# < 		Sound.instance().playVocality( soundName, playEntity.model )
#
# ---
# > 		soundMgr.playVocality( soundName, playEntity.model )
#
# Revision 1.4  2008/01/23 03:47:23  yangkai
# ���ݲ߻�Ҫ�� ��������ʱ��ǿ����ֹ������Ч
#
# Revision 1.3  2008/01/08 06:39:57  yangkai
# no message
#
# Revision 1.2  2008/01/05 03:51:34  yangkai
# ��Ӹ��Ϲ�Ч֧��
# �Ż����й�Ч��һ�β��ſ�������
# �Ż���Ч���ͳ�ʼ��
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
# Revision 1.34  2008/01/02 07:44:05  yangkai
# ���ɾ�������쳣����
#
# Revision 1.33  2008/01/02 01:47:48  yangkai
# ע�͵��Դ���
#
# Revision 1.32  2007/12/29 09:32:22  yangkai
# ������Ч����
#
# Revision 1.31  2007/09/28 02:25:52  yangkai
# �����ļ�·������:
# res/client  -->  res/config
#
# Revision 1.30  2007/09/21 03:35:14  yangkai
# ɾ��һЩ���Դ���
#
# Revision 1.29  2007/09/21 03:26:59  yangkai
# �����Ҳ�����Ч�ļ��Ĵ���
#
# Revision 1.28  2007/09/12 08:45:20  yangkai
# ������ܻ���Ч��ģ�ͱ�������
# �������й�Ч������ʧ����������
# �����󶨵���ж�
#
# Revision 1.27  2007/07/20 02:43:36  kebiao
# ����ʩչ��������˷�װ���������ּ��ܽӿ�
#
# Revision 1.26  2007/06/14 10:44:47  huangyongwei
# ������ȫ�ֶ���
#
# Revision 1.25  2007/06/07 02:53:34  yangkai
# playCastEffects()
# ��Ӳ�����position
#
# Revision 1.24  2007/06/07 02:18:46  yangkai
# ����ȥ�����õĶ���
#
# Revision 1.23  2007/06/04 01:30:01  yangkai
# no message
#
# Revision 1.22  2007/05/24 08:32:06  yangkai
# ��ӹ�Ч���뵭��Ч��
#
# Revision 1.21  2007/05/24 06:45:35  yangkai
# ���������ʵ��
#
# Revision 1.20  2007/03/21 08:20:13  yangkai
# ֻ�������10�����ڵ�ս����Ч
#
# Revision 1.19  2007/03/20 08:23:25  yangkai
# ��Ч�ж�ʱ�������ж�
#
# Revision 1.18  2007/03/20 01:44:09  yangkai
# ������Ч��ʼ����ʽ��������ܵ�һ�β��ſ���BUG
#
# Revision 1.17  2007/03/16 09:34:30  yangkai
# ȥ��ע����Ϣ
#
# Revision 1.16  2007/03/15 07:00:38  yangkai
# ���������������Ҫ�ӳ�0.01�벥�Ź�Ч��
# ������������ֹ�����ʱ�䣨���ʺܵͣ����Ǵ��ڣ�
# ���¹�Ч����ʧ��BUG
#
# Revision 1.15  2007/03/14 02:22:54  yangkai
# ��Ϊ�����������еĹ�Ч�ӳ�0.01�벥��
#
# Revision 1.14  2007/03/10 09:46:42  yangkai
# �������˵Ľ��飬��������������⵼�µĵ�һ�ι�Ч��ʾ��������BUG
#
# Revision 1.13  2007/03/01 09:07:36  yangkai
# ���KEEP_TO_BANGON��־��
#
# Revision 1.12  2007/02/28 07:32:02  yangkai
# ������Ч����ʧ��
#
# Revision 1.11  2007/02/13 08:31:22  phw
# g_sound --> Sound.instance()
#
# Revision 1.10  2007/01/18 07:20:06  lilian
# ���position��Ĭ��ֵ��0,0��0��������Ӧbuffer�����
# def cast( self, caster, targetID, position = Math.Vector3(0.0, 0.0, 0.0) ):
#
# Revision 1.9  2007/01/13 07:24:04  yangkai
# ��� playBuffEffects�������Բ���buff��Ч
#
# Revision 1.8  2006/12/13 09:11:00  yangkai
# �Ż��˹�Ч�Ĳ��ţ�ʹ���������ļ������
#
# Revision 1.7  2006/12/11 03:04:26  yangkai
# ������targetģ�͹�Ч���Ų�����
#
# Revision 1.6  2006/12/02 07:44:07  lilian
# self.interruptSpell --> self.interruptAttack
#
# Revision 1.5  2006/12/02 07:21:04  lilian
# �����isPlaying ����
#
# Revision 1.4  2006/11/25 08:22:37  lilian
# �޸Ĺ�Ч����(����yangkai��lilian�޸ĵ����д���)
#
# Revision 1.3  2006/06/12 10:26:08  panguankong
# ����������������˻���Ч��
#
# Revision 1.2  2006/06/10 07:30:36  panguankong
# �޸��˹���Ч��
#
# Revision 1.1  2006/06/08 09:35:31  panguankong
# ��ӹ���Ч��������
#

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

SOURCE_MATRIX_SWARM = 13 #粒子效果中用于实现类似WOW中死亡之握效果的action

EFFECT_LIFE_TIME = 0.3												#受击中光效存活时间
EFFECT_LIMIT_COUNT = 2												#受击中光效限制数量


class Effect:
	"""
	效果
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
		@param dict		:	技能配置数据
		@type dict		:	python dict
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	施展对象
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
		@param dict		:	技能配置数据
		@type dict		:	python dict
		@param cModel	:	施展模型
		@type cModel	:	PyModel
		@param tModel	:	目标模型
		@type tModel	:	PyModel
		@param cType	:	施展粒子类型
		@type cType		:	int
		@param tType	:	目标粒子类型
		@type tType		:	int
		"""
		return createSuitableEffect( dict, cModel, tModel, cType, tType )

	def createEffectByID( self, effectID, cModel, tModel, cType, tType ):
		"""
		Return the Effect type instance
		@param effectID	:	技能配置ID
		@type effectID	:	string
		@param cModel	:	施展模型
		@type cModel	:	PyModel
		@param tModel	:	目标模型
		@type tModel	:	PyModel
		@param cType	:	施展粒子类型
		@type cType		:	int
		@param tType	:	目标粒子类型
		@type tType		:	int
		"""
		dict = rds.spellEffect.getEffectConfigDict( effectID )
		if len( dict ) == 0: return
		return self.createEffect( dict, cModel, tModel, cType, tType )

	def playBeginEffects( self, caster, targetObject, skillID ):
		"""
		Play the BeginEffects
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	施展对象
		@type  target	:	一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@param 	:	技能ID
		@type skillID	:	Int
		"""
		# 声音
		soundNames = rds.spellEffect.getSpellStartSound( skillID )
		voiceNames = ()
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			gender = caster.getGender()
			if gender == csdefine.GENDER_MALE:
				voiceNames = rds.spellEffect.getSpellStartVoice_Man( skillID )	# all voiceNames用于人声发音 by姜毅
			else:
				voiceNames = rds.spellEffect.getSpellStartVoice_Female( skillID )
			soundNames += voiceNames
		caster.allEffects[ "beginSound" ] = soundNames
		for name in soundNames:
			self.playSound( caster, name )
		# 光效
		dict = rds.spellEffect.getStartEffect( skillID, caster.id, caster.weaponType )
		if dict is None: return
		if targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION:
			#do some thing
			sk = skills.getSkill( skillID )		# CSOL-1724位置光效技能起始光效支持
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
		@param caster	:	施展entity
		@type caster	:	entity
		"""
		# 停止起始光效
		effect = caster.allEffects.get( "begin" )
		if effect:
			effect.stop()
			caster.allEffects.pop( "begin" )

		# 停止起始音效
		soundNames = caster.allEffects.get( "beginSound" )
		if soundNames:
			for name in soundNames:
				self.stopSound( caster, name )
			caster.allEffects.pop( "beginSound" )

	def playLoopEffects( self, caster, targetObject, skillID ):
		"""
		Play the LoopEffects
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
		@type skillID	:	Int
		"""
		# 声音
		soundNames = rds.spellEffect.getSpellLoopSound( skillID )
		voiceNames = ()
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			gender = caster.getGender()
			if gender == csdefine.GENDER_MALE:
				voiceNames = rds.spellEffect.getSpellLoopVoice_Man( skillID )	# all voiceNames用于人声发音 by姜毅
			else:
				voiceNames = rds.spellEffect.getSpellLoopVoice_Female( skillID )
			soundNames += voiceNames
		caster.allEffects["loopSound"] = soundNames
		for name in soundNames:
			self.playSound( caster, name )

		# 光效
		dict = rds.spellEffect.getLoopEffect( skillID, caster.id, caster.weaponType )
		if dict is None: return
		if targetObject.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION:
			#do some thing
			sk = skills.getSkill( skillID )		# CSOL-1724位置光效技能起始光效支持
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
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
		@type skillID	:	Int
		"""
		# 停止循环光效
		effect = caster.allEffects.get( "loop" )
		if effect:
			effect.stop()
			caster.allEffects.pop( "loop" )
		# 停止循环音效
		soundNames = caster.allEffects.get( "loopSound" )
		if soundNames:
			for name in soundNames:
				self.stopSound( caster, name )
			caster.allEffects.pop( "loopSound" )

	def playLinkEffect( self, caster, targetObject, skillID ):
		"""
		播放连线光效
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
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
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
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
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
		中止释放光效
		@param caster	:	施展entity
		@type caster	:	entity
		"""
		if caster is None: return
		if not caster.inWorld: return
		if caster.homingEffect:
			caster.homingEffect.stop()

	def stopMovingEffects( self, caster ):
		"""
		中止释放光效
		@param caster	:	施展entity
		@type caster	:	entity
		"""
		if caster is None: return
		if not caster.inWorld: return
		if caster.movingEffect:
			caster.movingEffect.end()

	def playBuffEffects( self, caster, target, skillID ):
		"""
		播放buff效果
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	BUffID
		@type skillID	:	Int
		"""
		target.buffEffect[skillID] = {}
		# 光效
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

		# 声音
		soundNames = rds.spellEffect.getSpellCastSound( skillID )
		target.buffEffect[skillID]["buff_sound"] = soundNames
		for name in soundNames:
			self.playSound( target, name )


	def stopBuffEffects( self, caster, target, skillID ):
		"""
		Play the BeginEffects
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
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
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
		@type skillID	:	Int
		"""
		# 声音
		self.playHitSounds( caster, target, skillID )
		# 光效
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
		#此时才播放受击光效
		effect.start()

	def playBangOnEffects( self, caster, target, skillID ):
		"""
		Play the BangOnEffects
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
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
		播放声音
		@param entity	:	声音播放的位置
		@type entity	:	entity
		@param soundName:	声音文件对应的字段名
		@type soundName	:	string
		"""
		if entity is None: return
		model = entity.getModel()
		if model is None: return
		soundMgr.playVocality( soundName, model )

	def stopSound( self, entity, soundName ):
		"""
		播放声音
		@param entity	:	声音播放的位置
		@type entity	:	entity
		@param soundName:	声音文件对应的字段名
		@type soundName	:	string
		"""
		soundMgr.stopVocality( soundName, entity.getModel() )

	def playCastSounds( self, caster, skillID ):
		"""
		播放普通攻击挥舞时的声音
		@param caster	:	施展entity
		@type caster	:	entity
		@param skillID	:	技能ID
		@type skillID	:	Int
		"""
		voiceNames = ()
		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			weaponType = caster.weaponType
			soundNames = rds.spellEffect.getNormalCastSound( weaponType )
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				gender = caster.getGender()
				if gender == csdefine.GENDER_MALE:
					voiceNames = rds.spellEffect.getNormalCastVoice_Man( weaponType )	# all voiceNames用于人声发音 by姜毅
				else:
					voiceNames = rds.spellEffect.getNormalCastVoice_Female( weaponType )
				soundNames += voiceNames
		else:
			soundNames = rds.spellEffect.getSpellCastSound( skillID )
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				gender = caster.getGender()
				if gender == csdefine.GENDER_MALE:
					voiceNames = rds.spellEffect.getSpellCastVoice_Man( skillID )	# all voiceNames用于人声发音 by姜毅
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
		播放摄像机效果
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
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
		播放一个摄像头震动效果
		@type cameraEffectID	:	Int
		@param cameraEffectID	:	摄像头效果ID
		"""
		lastTime = rds.spellEffect.getCameraEffectLastTime( cameraEffectID )
		rangeShake = rds.spellEffect.getCameraEffectRangeShake( cameraEffectID )
		centerShake = rds.spellEffect.getCameraEffectCenterShake( cameraEffectID )
		rds.effectMgr.cameraShake( lastTime, rangeShake, centerShake )

	def playHitSounds( self, caster, target, skillID ):
		"""
		播放受击时的声音
		@param caster	:	施展entity
		@type caster	:	entity
		@param target	:	接收entity
		@type target	:	entity
		@param skillID	:	技能ID
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
		攻击音效 by姜毅
		"""
		if not caster.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnAttackSound( caster.modelNumber )	# 获取攻击音效
		if len( soundNames ) <= 0 :
			print "get monster AttackSound null"
			return
		soundName = random.choice( soundNames )
		caster.playSound( soundName )	# 播放攻击音效

	def interrupt( self, caster ):
		"""
		停止光效
		"""
		self.stopBeginEffects( caster )
		self.stopLoopEffects( caster )
		self.stopCastEffects( caster )
		caster.allEffects = {}

# ------------------------------------------------------------------------------------------------
# 光效类型基类
# ------------------------------------------------------------------------------------------------
class EffectBase:
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		self.dict = dict										# 效果数据段
		self.cModel = cModel									# 效果起始模型
		self.tModel = tModel									# 效果结束模型
		self.isPlaying = False									# 当前播放状态
		self.visible = True										# 当前显示状态
		self.sound = dict.get( "particle_sound", "" )			# 触发声音配置
		self.delayTime = dict.get( "particle_delaytime", 0.0 )	# 延迟播放时间
		self.scale = dict.get( "particle_scale", 0.0 )			# 光效/贴图缩放倍率
		if not self.scale: self.scale = 1.0						# 默认缩放倍率1.0
		self.scale = self.scale * scale
		pl = str( dict.get( "particle_lasttime", "0.0" )).split(";")
		self.lastTime = 0.0
		self.fadeOutTime = 2.0
		if len( pl ) > 0 and pl[ 0 ] != "":
			self.lastTime = float( pl[ 0 ] )	# 持续播放时间
		if len( pl ) > 1 and pl[ 1 ] != "":
			self.fadeOutTime = float( pl[ 1 ] )	# 删除时淡出时间
		flora = dict.get( "particle_flora", "" ).split( ";" )
		self.flora = 0			# 是否草碰撞
		self.floraOnce = 0		# 只碰撞一次
		if len( flora ) > 0 and flora[0] != "":
			self.flora = int( flora[0] )
		if len( flora ) > 1 and flora[1] != "":
			self.floraOnce = int( flora[1] )
		floraDatas = dict.get( "particle_floraData", "" ).split( ";" )
		self.floraDis = 1.0		# 草碰撞范围
		self.floraSpeed = 4.0	# 草晃动速度
		self.floraTime = 4.0	# 草晃动时间
		self.floraForce = 3.0	# 草碰撞力度
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
		开始播放光效表现
		"""
		self.isPlaying = True
		BigWorld.callback( self.delayTime, self.playAc )		# 在延迟时间后播放该粒子光效

	def playAc( self ):
		"""
		播放光效表现
		"""
		if not self.isPlaying: return
		self.play()
		if self.lastTime == 0: return
		BigWorld.callback( self.lastTime, self.stop )			# 在持续时间后停止该粒子光效

	def play( self ):
		"""
		Virtual Method
		播放光效表现
		"""
		self.playParticleSound()

	def stop( self ):
		"""
		Virtual Method
		停止光效表现
		"""
		self.isPlaying = False
		self.fadeOut()
		BigWorld.callback( self.fadeOutTime, self.detach )

	def end( self ):
		"""
		某种特殊情况下的终止光效
		add by wuxo 2012-4-28
		"""
		pass

	def fadeOut( self ):
		"""
		Virtual Method
		渐隐光效表现
		"""
		self.visible = False

	def fadeIn( self ):
		"""
		Virtual Method
		渐入光效表现
		"""
		self.visible = True

	def detach( self ):
		"""
		Virtual Method
		移除光效效果
		"""
		self.stopParticleSound()

	def getType( self ):
		"""
		返回粒子加载类型
		"""
		return Define.TYPE_PARTICLE_PLAYER

	def getPlaySoundModel( self ):
		"""
		返回播放光效触发声音的模型
		"""
		return self.cModel

	def playParticleSound( self ):
		"""
		播放光效触发声音
		"""
		model = self.getPlaySoundModel()
		if model is None: return
		soundMgr.playVocality( self.sound, model )

	def stopParticleSound( self ):
		"""
		停止光效触发声音
		"""
		model = self.getPlaySoundModel()
		if model is None: return
		soundMgr.stopVocality( self.sound, model )

	def openFloraCollision( self, model ):
		"""
		开启草碰撞
		"""
		if model is None: return
		if not self.flora: return
		model.floraCollision = True
		model.floraCollisionDis = self.floraDis
		model.floraCollisionSpeed = self.floraSpeed
		model.floraCollisionTime = self.floraTime
		model.floraCollisionForce = self.floraForce
		functor = Functor( self.closeFloraCollision, model )
		if self.floraOnce:	# 只做一次碰撞
			BigWorld.callback( 0.01, functor )

	def closeFloraCollision( self, model ):
		"""
		关闭草碰撞
		"""
		if model is None: return
		model.floraCollision = False

# ------------------------------------------------------------------------------------------------
# 摄像机震动效果类型
# ------------------------------------------------------------------------------------------------
class CameraEffect( EffectBase ):
	"""
	摄像机震动效果
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.cameraEffectID = dict.get("particle_cameraEffectID", 0 )   #摄像机效果ID

	def play( self ):
		"""
		播放震动效果
		"""
		rds.skillEffect.playCameraEffect( self.cameraEffectID )

		EffectBase.play( self )

	def stop( self ):
		"""
		停止震动效果
		"""
		rds.skillEffect.playCameraEffect( 0 )

		EffectBase.stop( self )

# ------------------------------------------------------------------------------------------------
# 位置光效类型
# ------------------------------------------------------------------------------------------------
class PositionEffect( EffectBase ):
	"""
	指定位置播放光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.position = dict.get( "particle_position", Math.Vector3() )		 		# 播放位置
		self.effectIDs = dict.get( "particle_posEffectIDs", "" ).split(";" )		# 播放光效ID
		self.childEffects = []														# 播放光效ID列表
		self.model = None

	def getType( self ):
		"""
		返回粒子加载类型
		"""
		return self.cType

	def setPosition( self, pos ):
		"""
		设置动态位置
		@param		pos		: 位置
		@type		pos		: Vector3
		"""
		self.position = pos

	def play( self ):
		"""
		播放光效
		"""
		rds.effectMgr.addModelBGWithPos( self.position, [Const.EMPTY_MODEL_PATH ], self.__onLoadModel )

		EffectBase.play( self )

	def __onLoadModel( self, model ):
		"""
		加载模型回调函数
		@param		model		: 光效的释放源
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
		卸载光效
		"""
		for effect in self.childEffects:
			effect.stop()

		EffectBase.stop( self )

	def detach( self ):
		"""
		卸载模型
		"""
		player = BigWorld.player()
		if player is None: return

		if self.model in list( player.models ):
			player.delModel( self.model )

		EffectBase.detach( self )

# ------------------------------------------------------------------------------------------------
# 位置贴图光效类型
# ------------------------------------------------------------------------------------------------
class PictureEffect( EffectBase ):
	"""
	位置播放贴图光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param sect			:	技能效果配置数据
		@type sect			:	sect
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		pictureDatas = dict.get("particle_picture","" ).split( ";" )
		self.picture = ""
		self.pictureColor = Math.Vector3( 1.0, 1.0, 1.0 )
		self.pictureFadeInTime = 0.0
		self.pictureFadeOutTime = 0.0
		if len( pictureDatas ) > 0 and pictureDatas[0] != "":	# 贴花贴图路径
			self.picture = pictureDatas[0]
		if len( pictureDatas ) > 1 and pictureDatas[1] != "":	# 贴花颜色，默认为白色
			self.pictureColor = Math.Vector3( eval( pictureDatas[1] ) )
		if len( pictureDatas ) > 2 and pictureDatas[2] != "":	# 贴花渐入时间
			self.pictureFadeInTime = float( pictureDatas[2] )
		if len( pictureDatas ) > 3 and pictureDatas[3] != "":	# 贴花渐隐时间
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
		返回产生效果的位置
		Virtual Method
		"""
		return self.position

	def setPosition( self, pos ):
		"""
		"""
		self.position = pos

	def getDir( self ):
		"""
		返回贴图的朝向
		Virtual Method
		"""
		return Math.Vector3()

	def play( self ):
		"""
		播放光效
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
		缩小
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
		放大
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
		卸除光效
		"""
		if self.isTgaAnimation:
			self.quit = 1
		BigWorld.deleteDecal( self.calIndex, self.pictureFadeOutTime )
		EffectBase.detach( self )

# ------------------------------------------------------------------------------------------------
# 自身位置贴图光效类型
# ------------------------------------------------------------------------------------------------
class SelfPictureEffect( PictureEffect ):
	"""
	自身位置播放贴图光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param sect			:	技能效果配置数据
		@type sect			:	sect
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		PictureEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getPosition( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		return self.cModel.position

	def getDir( self ):
		"""
		返回贴图的朝向
		Virtual Method
		"""
		yaw = self.cModel.yaw
		return Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )

# ------------------------------------------------------------------------------------------------
# 目标位置贴图光效类型
# ------------------------------------------------------------------------------------------------
class TargetPictureEffect( PictureEffect ):
	"""
	目标位置播放贴图光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param sect			:	技能效果配置数据
		@type sect			:	sect
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		PictureEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getPosition( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		return self.tModel.position

	def getDir( self ):
		"""
		返回贴图的朝向
		Virtual Method
		"""
		yaw = self.tModel.yaw
		return Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )

	def getPlaySoundModel( self ):
		"""
		"""
		return self.tModel

# ------------------------------------------------------------------------------------------------
# 粒子类型
# ------------------------------------------------------------------------------------------------
class ParticleEffect( EffectBase ):
	"""
	粒子效果
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.isStatic = dict.get( "particle_static", 0 )			# 是否静态效果
		self.particleSource = dict.get( "particle_source", "" )		# 粒子配置文件
		self.hardPoint = dict.get( "particle_hardpoint", "" )		# 播放的绑定点
		self.part = dict.get( "particle_part", "" )					# 额外模型表现
		self.staticModel = None										# 静态模型
		self.particle = None
		self.floraModel = None

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def play( self ):
		"""
		播放光效
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
		渐隐光效
		"""
		EffectBase.fadeOut( self )
		rds.effectMgr.fadeOutParticle( self.particle )	# 光效渐隐消失方式

	def fadeIn( self ):
		"""
		渐入光效
		"""
		EffectBase.fadeIn( self )
		rds.effectMgr.fadeInParticle( self.particle )

	def __onLoadModel( self, model ):
		"""
		加载模型回调
		@param model		:	光效的释放源
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
		回调函数，当粒子在后线程创建好了之后回调
		考虑到异步的问题，如果此时粒子已经收到停止的消息
		则渐隐光效
		@param particle		:	释放的光效
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
		卸除光效
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

		# 移除相关模型粒子
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
# 粒子自身类型
# ------------------------------------------------------------------------------------------------
class SelfParticleEffect( ParticleEffect ):
	"""
	释放源粒子效果
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		ParticleEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def getType( self ):
		"""
		返回粒子加载类型
		"""
		return self.cType

# ------------------------------------------------------------------------------------------------
# 粒子目标类型
# ------------------------------------------------------------------------------------------------
class TargetParticleEffect( ParticleEffect ):
	"""
	目标源粒子效果
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		ParticleEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.tModel, self.part )
		return self.tModel

	def getType( self ):
		"""
		返回粒子加载类型
		"""
		return self.tType

# ------------------------------------------------------------------------------------------------
# 刀光类型
# ------------------------------------------------------------------------------------------------
class LoftEffect( EffectBase ):
	"""
	粒子效果
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# 粒子配置文件
		self.hardPoint = dict.get( "particle_hardpoint", "" )		# 播放的绑定点
		self.part = dict.get( "particle_part", "" )					# 额外模型表现
		self.particle = None
		self.floraModel = None

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def getType( self ):
		"""
		返回粒子加载类型
		"""
		return self.cType

	def play( self ):
		"""
		播放刀光
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
		渐隐光效
		"""
		EffectBase.fadeOut( self )
		if self.particle:
			system = self.particle.system(0)
			if system:
				system.renderer.stop()

	def fadeIn( self ):
		"""
		渐入光效
		"""
		EffectBase.fadeIn( self )
		if self.particle:
			self.particle.system(0).renderer.start()

	def __onLoadParticle( self, particle ):
		"""
		回调函数，当粒子在后线程创建好了之后回调
		考虑到异步的问题，如果此时粒子已经收到停止的消息
		则渐隐光效
		@param particle		:	释放的光效
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
		卸除光效
		"""
		EffectBase.detach( self )
		rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.particle )
		if self.floraModel:
			self.closeFloraCollision( self.floraModel )
			rds.effectMgr.detachObject( self.getModel(), self.hardPoint, self.floraModel )
		# 移除相关模型粒子
		del self.particle
		self.particle = None
		del self.floraModel
		self.floraModel = None

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getModel()

# ------------------------------------------------------------------------------------------------
# 刀光自身类型
# ------------------------------------------------------------------------------------------------
class SelfLoftEffect( LoftEffect ):
	"""
	自身播放类刀光光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		LoftEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

# ------------------------------------------------------------------------------------------------
# 模型类型
# ------------------------------------------------------------------------------------------------
class ModelEffect( EffectBase ):
	"""
	模型光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = dict.get( "particle_msource", "" )					# 模型配置
		self.hardPoint = dict.get( "particle_hardpoint", "" )					# 播放的绑定点
		self.isStatic = dict.get( "particle_static", 0 )						# 是否静态
		self.part = dict.get( "particle_part", "" )								# 额外模型表现
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )	# 模型附加配置
		self.modelFadeInTime = dict.get( "particle_modelfadeintime", 0.0 )		# 模型渐入时间
		self.modelFadeTime = dict.get( "particle_modelfadetime", 0.0 )			# 模型渐隐时间
		self.model = None

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def play( self ):
		"""
		播放光效
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
		模型加载回调
		"""
		self.model = model
		model.scale = ( self.scale, self.scale, self.scale )							# 缩放模型

		if not self.isPlaying:
			self.stop()
			return

		# 调整模型的朝向
		if self.cModel and self.tModel:
			yaw = utils.yawFromPos( self.cModel.position, self.tModel.position )
			if self.model: self.model.yaw = yaw

		if not self.isStatic:
			rds.effectMgr.attachObject( self.getModel(), self.hardPoint, model )		# 给释放者加上模型光效
		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( model, self.modelFadeInTime )					# 渐入模型
		if model.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( model, Const.MODEL_ACTION_PLAY )					# 动作

		self.openFloraCollision( model )

		if not self.visible:  self.fadeOut()

		for effectID in self.attachEffects:											# 在后线程创建模型的附加光效
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# 获取配置数据
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.cModel, self.cType, self.tType )	# 创建效果实例
			if particlesEffect is None: continue
			particlesEffect.start()													# 播放效果
			if not self.visible: particlesEffect.fadeOut()

	def fadeOut( self ):
		"""
		渐隐光效
		"""
		EffectBase.fadeOut( self )
		if self.model is None: return
		# 附加光效渐隐
		self.model.visibleAttachments = True
		rds.effectMgr.fadeOutModelAttachments( self.model )
		# 渐隐模型
		rds.effectMgr.fadeOutModel( self.model, self.modelFadeTime )

	def fadeIn( self ):
		"""
		渐入光效
		"""
		EffectBase.fadeIn( self )
		if self.model is None: return
		# 附加光效渐入
		self.model.visibleAttachments = False
		rds.effectMgr.fadeInModelAttachments( self.model )
		# 渐入模型
		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( self.model, self.modelFadeInTime )

	def detach( self ):
		"""
		卸除光效
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

		# 移除相关模型粒子
		del self.model
		self.model = None

	def getPlaySoundModel( self ):
		"""
		"""
		return self.getModel()

# ------------------------------------------------------------------------------------------------
# 模型自身类型
# ------------------------------------------------------------------------------------------------
class SelfModelEffect( ModelEffect ):
	"""
	自身播放类模型光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		ModelEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

# ------------------------------------------------------------------------------------------------
# 模型目标类型
# ------------------------------------------------------------------------------------------------
class TargetModelEffect( ModelEffect ):
	"""
	目标播放类模型光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		ModelEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.tModel, self.part )
		return self.tModel

# ------------------------------------------------------------------------------------------------
# 飞行类型
# ------------------------------------------------------------------------------------------------
class HomerEffect( EffectBase ):
	"""
	飞行光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = Const.EMPTY_MODEL_PATH
		self.hardPoint = dict.get( "particle_hardpoint", "" )			# 粒子飞出去的绑定点
		self.homerSpring = dict.get( "particle_spring", "" )			# 到达目标出发光效
		self.homerHitPoint = dict.get( "particle_hitpoint", "" )		# 飞行击中目标点
		self.homer = BigWorld.Homer()
		fl = str( dict.get( "particle_flyspeed", "" ) ).split(";")
		t= float( fl[0] )
		self.homer.speed = t if t else 0.0 						# 飞行速度
		if len(fl)<2:
			self.homer.turnAxis = ( 0, 0, 1 )
		else:self.homer.turnAxis = ( 0, 0, 0 )
		self.homer.proximity = 0.36
		self.homer.turnRate = 314.159
		self.homerModel = None
		self.isReverse = dict.get( "particle_reverse", 0 )			# 反向飞行
		self.part = dict.get( "particle_part", "" )
		self.playBangOnEffect = True

	def getTModel( self ):
		"""
		获得目标模型
		"""
		if self.isReverse: return self.cModel
		return self.tModel

	def getCModel( self ):
		"""
		获得起始模型
		"""
		if self.isReverse: model = self.tModel
		else: model = self.cModel
		if len( self.part ):
			return rds.effectMgr.getLinkObject( model, self.part )
		return model

	def getType( self ):
		"""
		返回粒子加载类型
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
		播放飞行光效
		"""
		cModel = self.getCModel()
		if cModel is None: return
		if not cModel.inWorld: return
		rds.effectMgr.addModelBGInPos( cModel, self.hardPoint, [self.modelSource], self.onLoadModel )
		EffectBase.play( self )

	def onBang( self ):
		"""
		飞行效果到达目标点
		"""
		self.stop()
		self.homer.target = None
		self.homer.proximityCallback = None
		self.onBangOver()

		# 飞到目标触发效果
		bangSect = rds.spellEffect.getEffectConfigSect( self.homerSpring )
		if bangSect is None: return
		bangOnEffect = createSuitableEffect( bangSect, self.getCModel(), self.getTModel(), self.cType, self.tType )
		if bangOnEffect is None: return
		if not self.getBangOnEffect(): return
		bangOnEffect.start()

	def onBangOver( self ):
		"""
		飞行效果到达目标点
		这个函数的效果和fadeOut是一样的
		区分开来的目的是因为飞行效果在飞出去没到达目标前是不能中止的。
		"""
		# 离弦之箭、不可收回。
		# 飞行效果只有在飞到目标才能渐隐。
		if self.homerModel:
			self.homerModel.visible = False
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )

	def onLoadModel( self, model ):
		"""
		模型加载回调
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

		# 设置飞行光效的目标点
		hitPoint = rds.effectMgr.accessNode( self.getTModel(), self.homerHitPoint )
		if hitPoint is None:
			self.stop()
			self.onBangOver()
			return

		self.openFloraCollision( self.homerModel )
		self.homerModel.addMotor( self.homer )
		self.homer.target = hitPoint
		self.homer.proximityCallback = self.onBang				# 设置飞行光效到达目标的callback 函数
		if self.homerModel.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( self.homerModel, Const.MODEL_ACTION_PLAY )					# 动作

	def detach( self ):
		"""
		卸除光效
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
		特殊情况下的终止光效
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
# 粒子飞行类型
# ------------------------------------------------------------------------------------------------
class HomerParticleEffect( HomerEffect ):
	"""
	飞行光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		HomerEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# 飞行附带粒子效果
		self.particle = None

	def onLoadModel( self, model ):
		"""
		模型加载回调
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
		粒子加载回调
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

# ------------------------------------------------------------------------------------------------
# 模型飞行类型
# ------------------------------------------------------------------------------------------------
class HomerModelEffect( HomerEffect ):
	"""
	飞行模型光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		HomerEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = dict.get( "particle_msource", "" )							# 飞行附带粒子效果
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )			# 模型附加配置
		self.modelFadeInTime = dict.get( "particle_modelfadeintime", 0.0 )				# 模型渐入时间
		self.modelFadeTime = dict.get( "particle_modelfadetime", 0.0 )					# 模型渐隐时间

	def onLoadModel( self, model ):
		"""
		模型加载回调
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale * self.scale

		HomerEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return

		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( model, self.modelFadeInTime )
		for effectID in self.attachEffects:											# 在后线程创建模型的附加光效
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# 获取配置数据
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.getTModel(), self.cType, self.tType )	# 创建效果实例
			if particlesEffect is None: continue
			particlesEffect.start()

	def onBangOver( self ):
		"""
		飞行效果到达目标点
		这个函数的效果和fadeOut是一样的
		区分开来的目的是因为飞行效果在飞出去没到达目标前是不能中止的。
		"""
		# 离弦之箭、不可收回。
		# 飞行效果只有在飞到目标才能渐隐。
		if self.homerModel:
			rds.effectMgr.fadeOutModel( self.homerModel, self.modelFadeTime )
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )

# ------------------------------------------------------------------------------------------------
# 抛物线飞行类型
# ------------------------------------------------------------------------------------------------
class HomerParabolaEffect( EffectBase ):
	"""
	抛物线飞行光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = Const.EMPTY_MODEL_PATH
		self.hardPoint = dict.get( "particle_hardpoint", "" )			# 粒子飞出去的绑定点
		self.homerSpring = dict.get( "particle_spring", "" )			# 到达目标出发光效
		self.homerHitPoint = dict.get( "particle_hitpoint", "" )		# 飞行击中目标点
		self.homer = BigWorld.CurveHomer()
		self.homer.speed = float( dict.get( "particle_flyspeed", 0.0 )	)		# 飞行速度
		self.homer.proximity = 0.3
		self.homerModel = None
		self.isReverse = dict.get( "particle_reverse", 0 )				# 反向飞行
		self.part = dict.get( "particle_part", "" )
		self.homerAngle = dict.get( "particle_homerAngle", 0.0 )		# 飞行角度
		self.casterPos = Math.Vector3()
		self.targetPos = Math.Vector3()
		self.playBangOnEffect = True

	def getTModel( self ):
		"""
		获得目标模型
		"""
		if self.isReverse: return self.cModel
		return self.tModel

	def getCModel( self ):
		"""
		获得起始模型
		"""
		if self.isReverse: model = self.tModel
		else: model = self.cModel
		if len( self.part ):
			return rds.effectMgr.getLinkObject( model, self.part )
		return model

	def getType( self ):
		"""
		返回粒子加载类型
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
		播放飞行光效
		"""
		cModel = self.getCModel()
		if cModel is None: return
		if not cModel.inWorld: return
		rds.effectMgr.addModelBGInPos( cModel, self.hardPoint, [self.modelSource], self.onLoadModel )
		EffectBase.play( self )

	def onBang( self ):
		"""
		飞行效果到达目标点
		"""
		self.stop()
		self.homer.target = None
		self.homer.proximityCallback = None
		self.onBangOver()

		# 飞到目标触发效果
		bangSect = rds.spellEffect.getEffectConfigSect( self.homerSpring )
		if bangSect is None: return
		bangOnEffect = createSuitableEffect( bangSect, self.getCModel(), self.getTModel(), self.cType, self.tType )
		if bangOnEffect is None: return
		if not self.getBangOnEffect(): return
		bangOnEffect.start()

	def onBangOver( self ):
		"""
		飞行效果到达目标点
		这个函数的效果和fadeOut是一样的
		区分开来的目的是因为飞行效果在飞出去没到达目标前是不能中止的。
		"""
		# 离弦之箭、不可收回。
		# 飞行效果只有在飞到目标才能渐隐。
		if self.homerModel:
			self.homerModel.visible = False
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )

	def onLoadModel( self, model ):
		"""
		模型加载回调
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
		if self.homerAngle < 3:  # 角度不能过大
			self.stop()
			self.onBangOver()
			ERROR_MSG("The homerAngle is wrong!")
 			return
		pos = self.casterPos + len * dir + Math.Vector3( 0, 1, 0 )
		self.homer.reset()
		self.homer.setCtrlPt( [self.casterPos, pos, self.targetPos], self.homerAngle )
		self.homer.turn = 1
		self.homer.turnAxis = ( 0, 0, 1 )

		# 设置飞行光效的目标点
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
		self.homer.proximityCallback = self.onBang 		# 设置飞行光效到达目标的callback 函数
		if self.homerModel.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( self.homerModel, Const.MODEL_ACTION_PLAY )					# 动作

	def detach( self ):
		"""
		卸除光效
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
		特殊情况下的终止光效
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
# 粒子抛物线飞行类型
# ------------------------------------------------------------------------------------------------
class HomerParabolaParticleEffect( HomerParabolaEffect ):
	"""
	粒子抛物线飞行光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		HomerParabolaEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# 飞行附带粒子效果
		self.particle = None

	def onLoadModel( self, model ):
		"""
		模型加载回调
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
		粒子加载回调
		"""
		self.particle = particle

		if not self.isPlaying:
			self.stop()
			return

class HomerParaParPosEffect( HomerParabolaEffect ):
	"""
	粒子抛物线飞行光效针对位置
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		HomerParabolaEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.particleSource = dict.get( "particle_source", "" )		# 飞行附带粒子效果
		self.particle = None
		
	def onLoadModel( self, model ):
		"""
		模型加载回调
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
		粒子加载回调
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
		获得目标模型
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
		if self.homerAngle < 3:  # 角度不能过大
			self.stop()
			self.onBangOver()
			ERROR_MSG("The homerAngle is wrong!")
			return
		pos = self.casterPos + len * dir + Math.Vector3( 0, 1, 0 )
		self.homer.reset()
		self.homer.setCtrlPt( [self.casterPos, pos, self.targetPos], self.homerAngle )
		self.homer.turn = 1
		self.homer.turnAxis = ( 0, 0, 1 )

		# 设置飞行光效的目标点
		hitPoint = Math.Matrix()
		hitPoint.setTranslate( self.targetPos )

		if self.homerModel is None:
			self.stop()
			self.onBangOver()
			return

		self.openFloraCollision( self.homerModel )
		self.homerModel.addMotor( self.homer )
		self.homer.target = hitPoint
		self.homer.proximityCallback = self.onBang 		# 设置飞行光效到达目标的callback 函数
		if self.homerModel.hasAction( Const.MODEL_ACTION_PLAY ):
			rds.actionMgr.playAction( self.homerModel, Const.MODEL_ACTION_PLAY )

	def onBang( self ):
		"""
		飞行效果到达目标点
		"""
		self.stop()
		self.homer.target = None
		self.homer.proximityCallback = None
		self.onBangOver()

		# 飞到目标触发效果
		bangSect = rds.spellEffect.getEffectConfigSect( self.homerSpring )
		if bangSect is None: return
		bangOnEffect = createSuitableEffect( bangSect, self.getCModel(), self.getTModel(), self.cType, self.tType )
		if bangOnEffect is None: return
		if not self.getBangOnEffect(): return
		if bangOnEffect.__class__.__name__ == "PositionEffect":
			bangOnEffect.setPosition( self.targetPos )
			bangOnEffect.start()
# ------------------------------------------------------------------------------------------------
# 模型抛物线飞行类型
# ------------------------------------------------------------------------------------------------
class HomerParabolaModelEffect( HomerParabolaEffect ):
	"""
	模型抛物线飞行光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		HomerParabolaEffect.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.modelSource = dict.get( "particle_msource", "" )							# 飞行附带粒子效果
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )			# 模型附加配置
		self.modelFadeInTime = dict.get( "particle_modelfadeintime", 0.0 )				# 模型渐入时间
		self.modelFadeTime = dict.get( "particle_modelfadetime", 0.0 )					# 模型渐隐时间

	def onLoadModel( self, model ):
		"""
		模型加载回调
		"""
		if self.getCModel():
			model.scale = self.getCModel().scale * self.scale

		HomerParabolaEffect.onLoadModel( self, model )
		if not self.isPlaying:
			self.stop()
			return

		if self.modelFadeInTime > 0.0:
			rds.effectMgr.fadeInModel( model, self.modelFadeInTime )
		for effectID in self.attachEffects:											# 在后线程创建模型的附加光效
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# 获取配置数据
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.getTModel(), self.cType, self.tType )	# 创建效果实例
			if particlesEffect is None: continue
			particlesEffect.start()

	def onBangOver( self ):
		"""
		飞行效果到达目标点
		这个函数的效果和fadeOut是一样的
		区分开来的目的是因为飞行效果在飞出去没到达目标前是不能中止的。
		"""
		# 离弦之箭、不可收回。
		# 飞行效果只有在飞到目标才能渐隐。
		if self.homerModel:
			rds.effectMgr.fadeOutModel( self.homerModel, self.modelFadeTime )
			self.homerModel.visibleAttachments = True
			rds.effectMgr.fadeOutModelAttachments( self.homerModel )


# ------------------------------------------------------------------------------------------------
# 复合光效类型
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
		渐隐光效表现
		"""
		EffectBase.fadeOut( self )
		for effect in self.childEffect:
			effect.fadeOut()

	def fadeIn( self ):
		"""
		渐入光效表现p
		"""
		EffectBase.fadeIn( self )
		for effect in self.childEffect:
			effect.fadeIn()

class LinkEffect( EffectBase ):
	"""
	连线粒子光效（类似WOW中DK的死亡之握/ 抽蓝 / 抽血的技能的特效）
	by wuxo 2012-5-11
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.isStatic = dict.get( "particle_static", 0 )			# 是否静态效果
		self.particleSource = dict.get( "particle_source", "" )		# 粒子配置文件
		self.hardPoint = dict.get( "particle_hardpoint", "" )		# 粒子线的连接起始点
		self.part = dict.get( "particle_part", "" )					# 额外模型表现
		self.staticModel = None										# 静态模型
		self.particle = None
		hitpoint = dict.get( "particle_hitpoint", "" ).split(":")          #粒子线的连接目标点
		if len( hitpoint ) == 1:
			self.hitPoint = hitpoint[0]
			self.tModel = [self.tModel]
		elif len( hitpoint ) == 2:
			self.hitPoint = hitpoint[0]
			if int( hitpoint[1] ) == 1:  #表示hitpoint为自身的绑定点
				self.tModel = [self.cModel]
			else:
				self.tModel = [self.tModel]
		
		self.floraModel = None

	def getModel( self ):
		"""
		返回产生效果的模型
		Virtual Method
		"""
		if len( self.part ):
			return rds.effectMgr.getLinkObject( self.cModel, self.part )
		return self.cModel

	def play( self ):
		"""
		播放光效
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
		渐隐光效
		"""
		EffectBase.fadeOut( self )
		if self.particle:
			rds.effectMgr.fadeOutParticle( self.particle )	# 光效渐隐消失方式

	def fadeIn( self ):
		"""
		渐入光效
		"""
		EffectBase.fadeIn( self )
		if self.particle:
			rds.effectMgr.fadeInParticle( self.particle )

	def __onLoadModel( self, model ):
		"""
		加载模型回调
		@param model		:	光效的释放源
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
		回调函数，当粒子在后线程创建好了之后回调
		考虑到异步的问题，如果此时粒子已经收到停止的消息
		则渐隐光效
		@param particle		:	释放的光效
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
		卸除光效
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

		# 移除相关模型粒子
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
	变色光效
	"""
	def __init__( self, dict, cModel, tModel, cType, tType, scale ):
		"""
		@param dict			:	技能效果配置数据
		@type dict			:	dict
		@param cModel		:	光效的释放源
		@type cModel		:	pyModel
		@param tModel		:	光效的接收源
		@type tModel		:	pyModel
		"""
		EffectBase.__init__( self, dict, cModel, tModel, cType, tType, scale )
		self.color = eval( dict.get( "particle_source", "()" ))	# 变色光效颜色
		self.fadeInTime = dict.get( "particle_modelfadeintime", 0.0 )     #变色淡入淡出时间

	def play( self ):
		"""
		播放光效
		"""
		if len( self.color ) == 0: return
		model = self.tModel
		srcColor = (1.0,1.0,1.0,1.0)
		rds.effectMgr.setModelColor( model, srcColor, self.color, self.fadeInTime )
		EffectBase.play( self )

	def detach( self ):
		"""
		卸除光效
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
# 添加3种模型光效功能
#
# Revision 1.18  2008/08/06 04:04:12  yangkai
# 添加了找不到资源文件的出错提示
#
# Revision 1.17  2008/07/28 09:11:10  yangkai
# no message
#
# Revision 1.16  2008/07/28 08:43:28  yangkai
# 1、调整了光效类型框架
# 2、添加了静态光效的支持
#
# Revision 1.15  2008/07/23 05:39:03  yangkai
# no message
#
# Revision 1.14  2008/07/22 09:01:11  yangkai
# 1、根据目标的HP_hitPoint点，计算飞行光效击中点的位置偏移
# 2、添加了弱引用，防止交叉引用
#
# Revision 1.13  2008/07/15 04:08:01  kebiao
# 将技能配置修改到datatool相关初始化需要修改
#
# Revision 1.12  2008/07/08 09:20:09  yangkai
# 修正了 光效配置加载方式
#
# Revision 1.11  2008/07/05 08:36:34  yangkai
# 添加普通攻击施展音效的处理
#
# Revision 1.10  2008/04/24 08:40:32  phw
# method modified: TargetParticleEffect::start(), 光效的倍率算法调整；
#
# Revision 1.9  2008/03/27 07:13:48  yangkai
# 添加接口 playHitSounds 播放受击时的声音
#
# Revision 1.8  2008/03/25 03:34:31  yangkai
# 添加接口 interrupt
#
# Revision 1.7  2008/03/06 08:33:03  yangkai
# 光效配置添加触发光效
#
# Revision 1.6  2008/01/30 07:19:05  yangkai
# 复合光效子光效数目支持8个
#
# Revision 1.5  2008/01/25 10:41:51  huangyongwei
# < 		Sound.instance().playVocality( soundName, playEntity.model )
#
# ---
# > 		soundMgr.playVocality( soundName, playEntity.model )
#
# Revision 1.4  2008/01/23 03:47:23  yangkai
# 根据策划要求： 吟唱结束时候，强行终止吟唱光效
#
# Revision 1.3  2008/01/08 06:39:57  yangkai
# no message
#
# Revision 1.2  2008/01/05 03:51:34  yangkai
# 添加复合光效支持
# 优化飞行光效第一次播放卡的问题
# 优化光效类型初始化
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
# Revision 1.34  2008/01/02 07:44:05  yangkai
# 添加删除粒子异常处理
#
# Revision 1.33  2008/01/02 01:47:48  yangkai
# 注释调试代码
#
# Revision 1.32  2007/12/29 09:32:22  yangkai
# 调整光效播放
#
# Revision 1.31  2007/09/28 02:25:52  yangkai
# 配置文件路径更改:
# res/client  -->  res/config
#
# Revision 1.30  2007/09/21 03:35:14  yangkai
# 删除一些调试代码
#
# Revision 1.29  2007/09/21 03:26:59  yangkai
# 屏蔽找不到光效文件的错误
#
# Revision 1.28  2007/09/12 08:45:20  yangkai
# 添加了受击光效随模型比例缩放
# 修正飞行光效淡淡消失的美观问题
# 修正绑定点的判断
#
# Revision 1.27  2007/07/20 02:43:36  kebiao
# 技能施展对象进行了封装，调整部分技能接口
#
# Revision 1.26  2007/06/14 10:44:47  huangyongwei
# 整理了全局定义
#
# Revision 1.25  2007/06/07 02:53:34  yangkai
# playCastEffects()
# 添加参数：position
#
# Revision 1.24  2007/06/07 02:18:46  yangkai
# 整理，去除无用的定义
#
# Revision 1.23  2007/06/04 01:30:01  yangkai
# no message
#
# Revision 1.22  2007/05/24 08:32:06  yangkai
# 添加光效淡入淡出效果
#
# Revision 1.21  2007/05/24 06:45:35  yangkai
# 添加了声音实现
#
# Revision 1.20  2007/03/21 08:20:13  yangkai
# 只播放玩家10米以内的战斗音效
#
# Revision 1.19  2007/03/20 08:23:25  yangkai
# 光效中断时，增加判断
#
# Revision 1.18  2007/03/20 01:44:09  yangkai
# 修正光效初始化方式，解决技能第一次播放卡的BUG
#
# Revision 1.17  2007/03/16 09:34:30  yangkai
# 去掉注释消息
#
# Revision 1.16  2007/03/15 07:00:38  yangkai
# 修正因零点问题需要延迟0.01秒播放光效，
# 当技能正好终止在这个时间（概率很低，但是存在）
# 导致光效不消失的BUG
#
# Revision 1.15  2007/03/14 02:22:54  yangkai
# 因为零点的问题所有的光效延迟0.01秒播放
#
# Revision 1.14  2007/03/10 09:46:42  yangkai
# 根据狼人的建议，修正了因零点问题导致的第一次光效显示不出来的BUG
#
# Revision 1.13  2007/03/01 09:07:36  yangkai
# 添加KEEP_TO_BANGON标志。
#
# Revision 1.12  2007/02/28 07:32:02  yangkai
# 修正光效不消失，
#
# Revision 1.11  2007/02/13 08:31:22  phw
# g_sound --> Sound.instance()
#
# Revision 1.10  2007/01/18 07:20:06  lilian
# 添加position的默认值（0,0，0），以适应buffer的情况
# def cast( self, caster, targetID, position = Math.Vector3(0.0, 0.0, 0.0) ):
#
# Revision 1.9  2007/01/13 07:24:04  yangkai
# 添加 playBuffEffects（）用以播放buff光效
#
# Revision 1.8  2006/12/13 09:11:00  yangkai
# 优化了光效的播放，使技能配置文件更简洁
#
# Revision 1.7  2006/12/11 03:04:26  yangkai
# 修正了target模型光效播放不正常
#
# Revision 1.6  2006/12/02 07:44:07  lilian
# self.interruptSpell --> self.interruptAttack
#
# Revision 1.5  2006/12/02 07:21:04  lilian
# 添加了isPlaying 函数
#
# Revision 1.4  2006/11/25 08:22:37  lilian
# 修改光效播放(包括yangkai和lilian修改的所有代码)
#
# Revision 1.3  2006/06/12 10:26:08  panguankong
# 调整了声音，添加了击中效果
#
# Revision 1.2  2006/06/10 07:30:36  panguankong
# 修改了攻击效果
#
# Revision 1.1  2006/06/08 09:35:31  panguankong
# 添加攻击效果和声音
#

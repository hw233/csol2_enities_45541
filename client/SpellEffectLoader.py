# -*- coding: gb18030 -*-

#$Id: SpellEffectLoader.py,v 1.8 2008-08-25 09:59:07 yangkai Exp $

from bwdebug import *
import Language
import Define
import csconst
import csdefine
import random
import Math
import BigWorld
from config.client.SkillEffect import SpellEffect
from config.client.SkillEffect import ClassArmorTypeMap
from config.client.SkillEffect import MWeaponType
from config.client.SkillEffect import SoundType
from config.client.SkillEffect import ActionType
from config.client.SkillEffect import NormalAttackEffect
from config.client.SkillEffect import ParticlesConfig
from config.client.SkillEffect import BranchParticlesConfig
from config.client.SkillEffect import CameraEffectConfig
from config.client.SkillEffect import ActionRule
from config.client.SkillEffect import ActionLimit
from config.client.SkillEffect import CameraFollowAction
# ----------------------------------------------------------------------------------------------------
# 技能效果配置加载 包括动作，光效，声音，图标
# ----------------------------------------------------------------------------------------------------

class SpellEffectLoader:
	"""
	技能效果配置加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：{...}}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert SpellEffectLoader._instance is None, "instance already exist in"
		self._atDatas = ActionType.Datas			# like as { actionTypeID : {"actionType" : action...}, ...}
		self._efDatas = SpellEffect.Datas			# like as { weaponType : { "spell_action_start" : ...}, ...}
		self._pDatas = ParticlesConfig.Datas		# like as { particesID : { "lastTime" : ... }, ... }
		self._bpDatas = BranchParticlesConfig.Datas	# like as { particesID : { "lastTime" : ... }, ... }
		self._nDatas = NormalAttackEffect.Datas		# like as { weaponType : { "spell_action_start" : ...}, ...}
		self._sDatas = SoundType.Datas				# like as { weaponType : { armorType : Sound, ... }, ... }
		self._mwDatas = MWeaponType.Datas			# like as { monsterNum : { "weaponType" : weaponType, "armorType" : armorType } }
		self._cDatas =  ClassArmorTypeMap.Datas		# like as { class : armorType ...}
		self._caDatas = CameraEffectConfig.Datas
		self._arDatas = ActionRule.Datas
		self._alDatas = ActionLimit.Datas
		self._cfDatas = CameraFollowAction.Datas
		self.WNormalMap = {				Define.WEAPON_TYPE_NONE			:	"action_type_none",
								Define.WEAPON_TYPE_WEIGHTBLUNT	:	"action_type_weightblunt",
								Define.WEAPON_TYPE_LIGHTBLUNT	:	"action_type_lightblunt",
								Define.WEAPON_TYPE_WEIGHTSHARP	:	"action_type_weightsharp",
								Define.WEAPON_TYPE_LIGHTSHARP	:	"action_type_lightsharp",
								Define.WEAPON_TYPE_DOUBLEHAND	:	"action_type_doublehand",
								Define.WEAPON_TYPE_BOW			:	"action_type_bow",
								Define.WEAPON_TYPE_POSISON		:	"action_type_poison",
								Define.WEAPON_TYPE_THROW		:	"action_type_throw",
								Define.WEAPON_TYPE_BIANSHEN		:	"action_type_bianshen",
								}
		self.WVehicleHipMap = {	Define.WEAPON_TYPE_NONE			:	"action_type_vehicleHip_none",
								Define.WEAPON_TYPE_WEIGHTBLUNT	:	"action_type_vehicleHip_weightblunt",
								Define.WEAPON_TYPE_LIGHTBLUNT	:	"action_type_vehicleHip_lightblunt",
								Define.WEAPON_TYPE_WEIGHTSHARP	:	"action_type_vehicleHip_weightsharp",
								Define.WEAPON_TYPE_LIGHTSHARP	:	"action_type_vehicleHip_lightsharp",
								Define.WEAPON_TYPE_DOUBLEHAND	:	"action_type_vehicleHip_doublehand",
								Define.WEAPON_TYPE_BOW			:	"action_type_vehicleHip_bow",
								Define.WEAPON_TYPE_POSISON		:	"action_type_vehicleHip_poison",
								Define.WEAPON_TYPE_THROW		:	"action_type_vehicleHip_throw",
								Define.WEAPON_TYPE_BIANSHEN		:	"action_type_vehicleHip_bianshen",
								}
		self.WVehiclePanMap = {	Define.WEAPON_TYPE_NONE			:	"action_type_vehiclePan_none",
								Define.WEAPON_TYPE_WEIGHTBLUNT	:	"action_type_vehiclePan_weightblunt",
								Define.WEAPON_TYPE_LIGHTBLUNT	:	"action_type_vehiclePan_lightblunt",
								Define.WEAPON_TYPE_WEIGHTSHARP	:	"action_type_vehiclePan_weightsharp",
								Define.WEAPON_TYPE_LIGHTSHARP	:	"action_type_vehiclePan_lightsharp",
								Define.WEAPON_TYPE_DOUBLEHAND	:	"action_type_vehiclePan_doublehand",
								Define.WEAPON_TYPE_BOW			:	"action_type_vehiclePan_bow",
								Define.WEAPON_TYPE_POSISON		:	"action_type_vehiclePan_poison",
								Define.WEAPON_TYPE_THROW		:	"action_type_vehiclePan_throw",
								Define.WEAPON_TYPE_BIANSHEN		:	"action_type_vehiclePan_bianshen",
								}
		self._armorTypeMap = {	Define.ARMOR_TYPE_EMPTY			:	"armor_type_empty",
								Define.ARMOR_TYPE_CLOTH			:	"armor_type_cloth",
								Define.ARMOR_TYPE_SKIN			:	"armor_type_skin",
								Define.ARMOR_TYPE_WOOD			:	"armor_type_wood",
								Define.ARMOR_TYPE_METAL			:	"armor_type_metal",
								Define.ARMOR_TYPE_SHIELD		:	"armor_type_shield",
								Define.ARMOR_TYPE_ROCK			:	"armor_type_rock",
								}

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = SpellEffectLoader()
		return self._instance

	# ---------------------------------------------------------------------------------
	# private
	# ---------------------------------------------------------------------------------

	def __idConvert( self, skillID ):
		"""
		转换技能ID为系列ID
		如：311120001 -> 311120
		程序自定义技能ID无需转换
		"""
		# 技能ID小于1000为程序自用，不需转换
		if skillID < csdefine.SKILL_ID_LIMIT:
			return skillID
		return skillID/1000

	def __getActionName( self, skillID, weaponType, useTimeType, vehicleType = 0 ):
		"""
		根据技能ID，武器类型，动作使用时段获取动作名
		@type  skillID: INT
		@param skillID: 技能ID号
		@type  weaponType: INT
		@param weaponType: 武器装备类型
		@type  useTimeType: String
		@param useTimeType: 动作使用时段，分"spell_action_start"/"spell_action_loop"/"spell_action_cast"
		@type  vehicleType: Int
		@param vehicleType: 骑宠类型
		"""
		id = self.__idConvert( skillID )
		# 普通攻击和技能攻击分开处理
		if id in csconst.SKILL_ID_PHYSICS_LIST:
			if id == csdefine.SKILL_ID_PHYSICS:
				id = weaponType
			else:
				id = id + 7		# 宠物远程技能
			data = self._nDatas
			useTimeType = "normal_%s" % useTimeType
		else:
			data = self._efDatas
			useTimeType = "spell_%s" % useTimeType

		aData = data.get( id )
		if aData is None: return []

		anames = aData.get( useTimeType )
		if anames is None: return []

		anames = random.choice( anames )

		# 根据骑宠座位类型决定该播放哪个动作
		if vehicleType == Define.VEHICLE_MODEL_HIP:
			MAPS = self.WVehicleHipMap
		elif vehicleType == Define.VEHICLE_MODEL_PAN:
			MAPS = self.WVehiclePanMap
		else:
			MAPS = self.WNormalMap
		tname = MAPS.get( weaponType )
		if tname is None: return []

		rActions = []
		for name in anames:
			wData = self._atDatas.get( name )
			if wData is None: continue
			action = wData.get( tname )
			if action is None: continue
			rActions.append( action )

		return rActions

	def __getEffectSect( self, skillID, casterID, weaponType, useTimeType ):
		"""
		获取光效配置数据段
		根据技能ID，武器类型，光效使用的Sect数据
		@type  skillID: INT
		@param skillID: 技能ID号
		@type  casterID: INT
		@param casterID: 施法者ID
		@type  weaponType: INT
		@param weaponType: 武器装备类型
		@type  useTimeType: String
		@param useTimeType: 动作使用时段，分"spell_effect_start"/"spell_effect_loop"/"spell_effect_cast"
		"""
		id = self.__idConvert( skillID )
		if id in csconst.SKILL_ID_PHYSICS_LIST:
			if id == csdefine.SKILL_ID_PHYSICS:
				id = weaponType
			else:
				id = id + 7		# 宠物远程技能
			data = self._nDatas
			useTimeType = "normal_%s" % useTimeType
		else:
			data = self._efDatas
			useTimeType = "spell_%s" % useTimeType

		try:
			effectID = data[ id ][ useTimeType ][0]
			player = BigWorld.player()
			caster = BigWorld.entities[casterID]
			if caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
				caster = caster.getOwner()
			if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and caster.id != player.id:
				bEffectID = "branch_%s" % effectID
				if self._bpDatas.has_key( bEffectID ):
					return self._bpDatas[bEffectID]
				else:
					return self._pDatas[effectID]
			else:
				return self._pDatas[effectID]
		except:
			return None

	def __getEffectID( self, skillID, weaponType, useTimeType ):
		"""
		根据技能ID，武器类型，光效使用时段获取光效ID
		"""
		id = self.__idConvert( skillID )
		if id in csconst.SKILL_ID_PHYSICS_LIST:
			if id == csdefine.SKILL_ID_PHYSICS:
				id = weaponType
			else:
				id = id + 7		# 宠物远程技能
			data = self._nDatas
			useTimeType = "normal_%s" % useTimeType
		else:
			data = self._efDatas
			useTimeType = "spell_%s" % useTimeType
		try:
			effectID = data[ id ][ useTimeType ][0]
		except:
			return ""
		return effectID

	# ---------------------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------------------
	def getSpellEffectSect( self, skillID ):
		"""
		根据技能ID得到配置数据段
		"""
		id = self.__idConvert( skillID )
		return self._efDatas.get( id )

	def getEffectIDList( self, skillID ):
		"""
		根据技能ID得到效果ID列表
		"""
		useTimeTypeList = []
		effectIDList = []
		spellEffectSect = self.getSpellEffectSect( skillID )
		if spellEffectSect is None: return []
		for i in spellEffectSect.keys():
			if i.startswith( "spell_effect" ):
				useTimeTypeList.append( i )
		if useTimeTypeList == []: return []
		for j in useTimeTypeList:
			k = self.getSpellEffectSect( skillID ).get( j )
			m = k[0]
			effectIDList.append( m )
		return effectIDList

	def getUseEffectIDList( self, skillID ):
		"""
		根据技能ID得到所有子效果ID列表
		"""
		particle_type_list1 = ["SelfModelEffect", "TargetModelEffect"]
		particle_type_list2 = ["PositionEffect", "PictureEffect"]
		particle_type_list3 = ["HomerParticleEffect", "HomerModelEffect"]
		useEffectIDList = self.getEffectIDList( skillID )
		if useEffectIDList == []: return []
		for i in useEffectIDList:
			j = self._pDatas.get( i )
			if j is None: continue
			type = j.get( "particle_type", "" )
			if type == "ComplexParticleEffect":
				for n in j.keys():
					if n.startswith( "particle_child" ):
						k = j.get( n )
						if k != "":
							useEffectIDList.append( k )
			elif type in particle_type_list1:
				mparticle = j.get( "particle_mparticle", "" )
				if mparticle == "": m = []
				m = mparticle.split(";")
				useEffectIDList.extend( m )
			elif type in particle_type_list2:
				posEffectIDs = j.get( "particle_posEffectIDs", "" )
				if posEffectIDs == "": p = []
				p = posEffectIDs.split(";")
				useEffectIDList.extend( p )
			elif type in particle_type_list3:
				s = j.get( "particle_spring","" )
				if s != "":
					useEffectIDList.append( s )
				mparticle = j.get( "particle_mparticle", "" )
				if mparticle == "": m = []
				m = mparticle.split(";")
				useEffectIDList.extend( m )
		return useEffectIDList

	def getParticlesPathList( self, skillID ):
		"""
		根据技能ID得到光效的路径列表
		"""
		particlesPathList = []
		useEffectIDList = self.getUseEffectIDList( skillID )
		if useEffectIDList == []: return []
		for i in useEffectIDList:
			j = self._pDatas.get( i )
			if j is None: j = {}
			k = j.get( "particle_source", "" )
			if k != "":
				particlesPathList.append( k )
#		particlesPathList = list( set( particlesPathList ) )  #去掉相同的光效路径
		return particlesPathList

	def getSkillIDByParticlesOverCount( self, count ):
		"""
		遍历所有的技能,返回光效路径列表长度大于num的技能ID及其光效路径列表长度的一个字典
		"""
		skillDict = {}
		for i in self._efDatas.keys():
			j  =  str( i ) + "001"
			k = int( j )
			particlesPathList = self.getParticlesPathList( k )
			if len( particlesPathList ) > count:
				dict = { i:len( particlesPathList ) }
				skillDict.update( dict )
		return skillDict

	def getEffectConfigDict( self, effectID ):
		"""
		获得效果ID的dict数据
		@type  effectID: INT
		@param effectID: 效果ID号
		@return DataSect
		"""
		if effectID.startswith( "branch_" ):
			return self._bpDatas.get( effectID, {} )
		else:
			return self._pDatas.get( effectID, {} )

	def getEffectXml( self ):
		"""
		获取所有用到的光效xml数据
		@return {} like as {particleID:particleXml...}
		"""
		effectDatas = {}
		for particleID, particle in self._pDatas.items():
			xml = particle.get( "particle_source", "" )
			if xml != "":
				effectDatas[particleID] = xml
		return effectDatas

	def getEffectConfigSect( self, effectID ):
		"""
		获得效果ID的sect数据
		@type  effectID: INT
		@param effectID: 效果ID号
		@return DataSect
		"""
		try:
			if effectID.startswith( "branch_" ):
				return self._bpDatas[effectID]
			else:
				return self._pDatas[effectID]
		except:
			return None

	def getStartAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		获得起始动作名
		@type  skillID: INT
		@param skillID: 技能ID号
		@type  weaponType: INT
		@param weaponType: 装备类型
		@type  vehicleType: BOOL
		@param vehicleType: 是否在骑宠
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_start", vehicleType )

	def getLoopAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		获得循环动作名
		@type  skillID: INT
		@param skillID: 技能ID号
		@type  weaponType: INT
		@param weaponType: 装备类型
		@type  vehicleType: BOOL
		@param vehicleType: 是否在骑宠
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_loop", vehicleType )

	def getCastAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		获得释放动作名
		@type  skillID: INT
		@param skillID: 技能ID号
		@type  weaponType: INT
		@param weaponType: 装备类型
		@type  vehicleType: BOOL
		@param vehicleType: 是否在骑宠
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_cast", vehicleType )

	def getHitAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		获得受击动作名
		@type  skillID: INT
		@param skillID: 技能ID号
		@type  weaponType: INT
		@param weaponType: 装备类型
		@type  vehicleType: BOOL
		@param vehicleType: 是否在骑宠
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_hit", vehicleType )

	def getStartEffect( self, skillID, casterID, type ):
		"""
		获取粒子配置dataSection
		@type  effectID: String
		@param effectID: 效果ID号
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_start" )

	def getLoopEffect( self, skillID, casterID, type ):
		"""
		获取粒子配置dataSection
		@type  effectID: String
		@param effectID: 效果ID号
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_loop" )

	def getCastEffect( self, skillID, casterID, type ):
		"""
		获取粒子配置dataSection
		@type  effectID: String
		@param effectID: 效果ID号
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_cast" )

	def getCastEffectID( self, skillID, type ):
		"""
		获取释放光效ID
		"""
		return self.__getEffectID( skillID, type, "effect_cast" )

	def getHitEffect( self, skillID, casterID, type ):
		"""
		获取粒子配置dataSection
		@type  effectID: String
		@param effectID: 效果ID号
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_hit" )

	def getHitEffectID( self, skillID, type ):
		"""
		获取受击光效ID
		"""
		return self.__getEffectID( skillID, type, "effect_hit" )

	def getIcon( self, skillID ):
		"""
		获得图标路径
		@type  skillID: INT
		@param skillID: 技能ID号
		@return String
		"""
		try:
			id = self.__idConvert( skillID )
			if id in Define.TRIGGER_SKILL_IDS: return "icons/skill_physics_037.dds"
			return "icons/%s.dds" % self._efDatas[ id ]["spell_icon"][0]
		except:
			return "icons/tb_yw_sj_005.dds"

	def getWeaponType( self, modelNum ):
		"""
		根据怪物模型编号获取怪物的武器类型
		(策划自定义)
		@type  skillID: INT
		@param skillID: 技能ID号
		@return Int
		"""
		try:
			return self._mwDatas[modelNum]["weapon_type"]
		except:
			return 0

	def getArmorTypeByNum( self, modelNum ):
		"""
		根据怪物模型编号获取怪物的防具类型
		(策划自定义) ( 见方法 :  self.getArmorTypeByClass )
		@type  skillID: INT
		@param skillID: 技能ID号
		@return Int
		"""
		try:
			return self._mwDatas[modelNum]["armor_type"]
		except:
			return 0

	def getArmorTypeByClass( self, classType ):
		"""
		根据职业获取防具类型
		策划定义为如果一个entity有装备胸甲则根据职业来判定其防具类型
		如果没有 则根据模型编号来获取策划自定义的防具类型( 见方法: self.getArmorTypeByNum )
		"""
		try:
			return self._cDatas[classType]
		except:
			return 0

	def getNormalHitSound( self, weaponType, armorType ):
		"""
		根据武器和防具类型获取应该播放的声音类型
		这个是获取普通攻击击中时候的击中声音效果
		@type  weaponType: INT
		@param weaponType: 武器类型
		@type  armorType: INT
		@param armorType: 防具类型
		@return String
		"""
		key = self._armorTypeMap.get( armorType )
		try:
			return self._sDatas[weaponType][key]
		except:
			WARNING_MSG( "Can't find NormalHitSound Config by WeaponType (%s) - ArmorType (%s)"%( weaponType, armorType ) )
			return None

	def getNormalCastSound( self, weaponType ):
		"""
		根据武器和防具类型获取应该播放的声音类型
		这个是获取普通攻击施展时候的施展声音效果
		@type  weaponType: INT
		@param weaponType: 武器类型
		@return String
		"""
		try:
			return self._nDatas[weaponType]["normal_sound_cast"]
		except KeyError:
			WARNING_MSG( "Can't find NormalCastSound Config by WeaponType (%s) "% weaponType )
			return ()

	def getNormalCastVoice_Man( self, weaponType ):
		"""
		根据武器和防具类型获取应该播放的声音类型
		这个是获取普通攻击施展时候的施展声音效果 男声
		@type  weaponType: INT
		@param weaponType: 武器类型
		@return String
		"""
		try:
			return self._nDatas[weaponType]["normal_voice_man_cast"]
		except KeyError:
			WARNING_MSG( "Can't find NormalCastVoice Config by WeaponType (%s) "% weaponType )
			return ()

	def getNormalCastVoice_Female( self, weaponType ):
		"""
		根据武器和防具类型获取应该播放的声音类型
		这个是获取普通攻击施展时候的施展声音效果 女声
		@type  weaponType: INT
		@param weaponType: 武器类型
		@return String
		"""
		try:
			return self._nDatas[weaponType]["normal_voice_female_cast"]
		except KeyError:
			WARNING_MSG( "Can't find NormalCastVoice Config by WeaponType (%s) "% weaponType )
			return ()

	def getSpellStartSound( self, skillID ):
		"""
		根据技能ID获取释放时的声音
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_start"]
		except:
			return ()

	def getSpellStartVoice_Man( self, skillID ):
		"""
		根据技能ID获取释放时的 男性 人声 by姜毅
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_man_start"]
		except:
			return ()

	def getSpellStartVoice_Female( self, skillID ):
		"""
		根据技能ID获取释放时的 女性 人声 by姜毅
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_female_start"]
		except:
			return ()

	def getSpellLoopSound( self, skillID ):
		"""
		根据技能ID获取释放时的声音
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_loop"]
		except:
			return ()

	def getSpellLoopVoice_Man( self, skillID ):
		"""
		根据技能ID获取释放时的人声 男声
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_man_loop"]
		except:
			return ()

	def getSpellLoopVoice_Female( self, skillID ):
		"""
		根据技能ID获取释放时的人声 女声
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_female_loop"]
		except:
			return ()

	def getSpellCastSound( self, skillID ):
		"""
		根据技能ID获取释放时的声音
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_cast"]
		except:
			return ()

	def getSpellCastVoice_Man( self, skillID ):
		"""
		根据技能ID获取释放时的声音 男声
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_man_cast"]
		except:
			return ()

	def getSpellCastVoice_Female( self, skillID ):
		"""
		根据技能ID获取释放时的声音 女声
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_female_cast"]
		except:
			return ()

	def getSpellHitSound( self, skillID ):
		"""
		根据技能ID获取释放时的声音
		@type  skillID: INT
		@param skillID: 技能ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_hit"]
		except:
			return ()

	def getCameraEffectID( self, skillID ):
		"""
		根据摄像头效果ID获取效果类型
		@type  effectID: INT
		@param effectID: 摄像头效果ID
		@return Int
		"""
		skillID = self.__idConvert( skillID )
		data = self._efDatas.get( skillID, None )
		if data is None: return 0
		return data.get( "spell_camera_effect_id", 0 )

	def getCameraEffectType( self, effectID ):
		"""
		根据摄像头效果ID获取效果类型
		@type  effectID: INT
		@param effectID: 摄像头效果ID
		@return Int
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return 0
		return data.get( "camera_effect_type", 0 )

	def getCameraEffectLastTime( self, effectID ):
		"""
		根据摄像头效果ID获取效果持续时间
		@type  effectID: INT
		@param effectID: 摄像头效果ID
		@return Float
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return 0.0
		return data.get( "camera_effect_lastTime", 0.0 )

	def getCameraEffectRangeShake( self, effectID ):
		"""
		根据摄像头效果ID获取效果XYZ晃动振幅
		@type  effectID: INT
		@param effectID: 摄像头效果ID
		@return Vector3
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return Math.Vector3()
		return data.get( "camera_effect_rangeShake", Math.Vector3() )

	def getCameraEffectCenterShake( self, effectID ):
		"""
		根据摄像头效果ID获取效果中心晃动振幅
		@type  effectID: INT
		@param effectID: 摄像头效果ID
		@return Vector3
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return Math.Vector3()
		return data.get( "camera_effect_centerShake", Math.Vector3() )

	def getActionGrade( self, actionName ):
		"""
		根据动作名获取动作优先级
		@param actionName: 动作名字
		@type actionName: string
		@return: Int
		"""
		return self._arDatas.get( actionName, 0 )

	def getActionLimitList( self ):
		"""
		获取动作限制列表
		@return: List
		"""
		return self._alDatas

	def checkActionLimit( self, actionName ):
		"""
		判断动作名是否在动作限制列表中
		@param actionName: 动作名字
		@type actionName: string
		@return: Bool
		"""
		if actionName in self._alDatas:
			return True
		return False

	def getCameraFollowActionList( self ):
		"""
		获取镜头跟随动作列表
		@return: List
		"""
		return self._cfDatas

	def checkCameraFollowAction( self, actionName ):
		"""
		判断动作名是否在镜头跟随动作列表列表中
		@param actionName: 动作名字
		@type actionName: string
		@return: Bool
		"""
		if actionName in self._cfDatas:
			return True
		return False

	def reset( self ):
		"""
		重新加载配置数据
		用于测试
		"""
		reload( SpellEffect )
		reload( ClassArmorTypeMap )
		reload( MWeaponType )
		reload( SoundType )
		reload( ActionType )
		reload( NormalAttackEffect )
		reload( ParticlesConfig )
		reload( BranchParticlesConfig )
		reload( CameraEffectConfig )
		reload( ActionRule )
		reload( ActionLimit )
		reload( CameraFollowAction )
		self._atDatas = ActionType.Datas		# like as { actionTypeID : {"actionType" : action...}, ...}
		self._efDatas = SpellEffect.Datas		# like as { weaponType : { "spell_action_start" : ...}, ...}
		self._pDatas = ParticlesConfig.Datas		# like as { particesID : { "lastTime" : ... }, ... }
		self._bpDatas = BranchParticlesConfig.Datas	# like as { particesID : { "lastTime" : ... }, ... }
		self._nDatas = NormalAttackEffect.Datas		# like as { weaponType : { "spell_action_start" : ...}, ...}
		self._sDatas = SoundType.Datas		# like as { weaponType : { armorType : Sound, ... }, ... }
		self._mwDatas = MWeaponType.Datas		# like as { monsterNum : { "weaponType" : weaponType, "armorType" : armorType } }
		self._cDatas =  ClassArmorTypeMap.Datas		# like as { class : armorType ...}
		self._caDatas = CameraEffectConfig.Datas
		self._arDatas = ActionRule.Datas
		self._alDatas = ActionLimit.Datas
		self._cfDatas = CameraFollowAction.Datas

#$Log: not supported by cvs2svn $
#Revision 1.7  2008/07/05 08:36:08  yangkai
#添加普通攻击施展音效的处理
#
#Revision 1.6  2008/03/27 07:14:42  yangkai
#声音配置加载
#
#Revision 1.5  2008/02/22 01:45:51  yangkai
#策划要求：默认图标改为 tb_yw_sj_005
#
#Revision 1.4  2008/01/25 10:07:40  yangkai
#配置文件路径修改
#
#Revision 1.3  2008/01/05 03:55:28  yangkai
#添加接口 getEffectConfigSect
#
#Revision 1.2  2007/12/29 09:34:12  yangkai
#光效配置加载
#
#Revision 1.1  2007/12/22 07:35:54  yangkai
#技能动作光效声音等效果加载代码
#

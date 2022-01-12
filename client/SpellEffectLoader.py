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
# ����Ч�����ü��� ������������Ч��������ͼ��
# ----------------------------------------------------------------------------------------------------

class SpellEffectLoader:
	"""
	����Ч�����ü���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��{...}}
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
		ת������IDΪϵ��ID
		�磺311120001 -> 311120
		�����Զ��弼��ID����ת��
		"""
		# ����IDС��1000Ϊ�������ã�����ת��
		if skillID < csdefine.SKILL_ID_LIMIT:
			return skillID
		return skillID/1000

	def __getActionName( self, skillID, weaponType, useTimeType, vehicleType = 0 ):
		"""
		���ݼ���ID���������ͣ�����ʹ��ʱ�λ�ȡ������
		@type  skillID: INT
		@param skillID: ����ID��
		@type  weaponType: INT
		@param weaponType: ����װ������
		@type  useTimeType: String
		@param useTimeType: ����ʹ��ʱ�Σ���"spell_action_start"/"spell_action_loop"/"spell_action_cast"
		@type  vehicleType: Int
		@param vehicleType: �������
		"""
		id = self.__idConvert( skillID )
		# ��ͨ�����ͼ��ܹ����ֿ�����
		if id in csconst.SKILL_ID_PHYSICS_LIST:
			if id == csdefine.SKILL_ID_PHYSICS:
				id = weaponType
			else:
				id = id + 7		# ����Զ�̼���
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

		# ���������λ���;����ò����ĸ�����
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
		��ȡ��Ч�������ݶ�
		���ݼ���ID���������ͣ���Чʹ�õ�Sect����
		@type  skillID: INT
		@param skillID: ����ID��
		@type  casterID: INT
		@param casterID: ʩ����ID
		@type  weaponType: INT
		@param weaponType: ����װ������
		@type  useTimeType: String
		@param useTimeType: ����ʹ��ʱ�Σ���"spell_effect_start"/"spell_effect_loop"/"spell_effect_cast"
		"""
		id = self.__idConvert( skillID )
		if id in csconst.SKILL_ID_PHYSICS_LIST:
			if id == csdefine.SKILL_ID_PHYSICS:
				id = weaponType
			else:
				id = id + 7		# ����Զ�̼���
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
		���ݼ���ID���������ͣ���Чʹ��ʱ�λ�ȡ��ЧID
		"""
		id = self.__idConvert( skillID )
		if id in csconst.SKILL_ID_PHYSICS_LIST:
			if id == csdefine.SKILL_ID_PHYSICS:
				id = weaponType
			else:
				id = id + 7		# ����Զ�̼���
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
		���ݼ���ID�õ��������ݶ�
		"""
		id = self.__idConvert( skillID )
		return self._efDatas.get( id )

	def getEffectIDList( self, skillID ):
		"""
		���ݼ���ID�õ�Ч��ID�б�
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
		���ݼ���ID�õ�������Ч��ID�б�
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
		���ݼ���ID�õ���Ч��·���б�
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
#		particlesPathList = list( set( particlesPathList ) )  #ȥ����ͬ�Ĺ�Ч·��
		return particlesPathList

	def getSkillIDByParticlesOverCount( self, count ):
		"""
		�������еļ���,���ع�Ч·���б��ȴ���num�ļ���ID�����Ч·���б��ȵ�һ���ֵ�
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
		���Ч��ID��dict����
		@type  effectID: INT
		@param effectID: Ч��ID��
		@return DataSect
		"""
		if effectID.startswith( "branch_" ):
			return self._bpDatas.get( effectID, {} )
		else:
			return self._pDatas.get( effectID, {} )

	def getEffectXml( self ):
		"""
		��ȡ�����õ��Ĺ�Чxml����
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
		���Ч��ID��sect����
		@type  effectID: INT
		@param effectID: Ч��ID��
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
		�����ʼ������
		@type  skillID: INT
		@param skillID: ����ID��
		@type  weaponType: INT
		@param weaponType: װ������
		@type  vehicleType: BOOL
		@param vehicleType: �Ƿ������
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_start", vehicleType )

	def getLoopAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		���ѭ��������
		@type  skillID: INT
		@param skillID: ����ID��
		@type  weaponType: INT
		@param weaponType: װ������
		@type  vehicleType: BOOL
		@param vehicleType: �Ƿ������
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_loop", vehicleType )

	def getCastAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		����ͷŶ�����
		@type  skillID: INT
		@param skillID: ����ID��
		@type  weaponType: INT
		@param weaponType: װ������
		@type  vehicleType: BOOL
		@param vehicleType: �Ƿ������
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_cast", vehicleType )

	def getHitAction( self, skillID, weaponType, vehicleType = 0 ):
		"""
		����ܻ�������
		@type  skillID: INT
		@param skillID: ����ID��
		@type  weaponType: INT
		@param weaponType: װ������
		@type  vehicleType: BOOL
		@param vehicleType: �Ƿ������
		@return String
		"""
		return self.__getActionName( skillID, weaponType, "action_hit", vehicleType )

	def getStartEffect( self, skillID, casterID, type ):
		"""
		��ȡ��������dataSection
		@type  effectID: String
		@param effectID: Ч��ID��
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_start" )

	def getLoopEffect( self, skillID, casterID, type ):
		"""
		��ȡ��������dataSection
		@type  effectID: String
		@param effectID: Ч��ID��
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_loop" )

	def getCastEffect( self, skillID, casterID, type ):
		"""
		��ȡ��������dataSection
		@type  effectID: String
		@param effectID: Ч��ID��
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_cast" )

	def getCastEffectID( self, skillID, type ):
		"""
		��ȡ�ͷŹ�ЧID
		"""
		return self.__getEffectID( skillID, type, "effect_cast" )

	def getHitEffect( self, skillID, casterID, type ):
		"""
		��ȡ��������dataSection
		@type  effectID: String
		@param effectID: Ч��ID��
		@return String
		"""
		return self.__getEffectSect( skillID, casterID, type, "effect_hit" )

	def getHitEffectID( self, skillID, type ):
		"""
		��ȡ�ܻ���ЧID
		"""
		return self.__getEffectID( skillID, type, "effect_hit" )

	def getIcon( self, skillID ):
		"""
		���ͼ��·��
		@type  skillID: INT
		@param skillID: ����ID��
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
		���ݹ���ģ�ͱ�Ż�ȡ�������������
		(�߻��Զ���)
		@type  skillID: INT
		@param skillID: ����ID��
		@return Int
		"""
		try:
			return self._mwDatas[modelNum]["weapon_type"]
		except:
			return 0

	def getArmorTypeByNum( self, modelNum ):
		"""
		���ݹ���ģ�ͱ�Ż�ȡ����ķ�������
		(�߻��Զ���) ( ������ :  self.getArmorTypeByClass )
		@type  skillID: INT
		@param skillID: ����ID��
		@return Int
		"""
		try:
			return self._mwDatas[modelNum]["armor_type"]
		except:
			return 0

	def getArmorTypeByClass( self, classType ):
		"""
		����ְҵ��ȡ��������
		�߻�����Ϊ���һ��entity��װ���ؼ������ְҵ���ж����������
		���û�� �����ģ�ͱ������ȡ�߻��Զ���ķ�������( ������: self.getArmorTypeByNum )
		"""
		try:
			return self._cDatas[classType]
		except:
			return 0

	def getNormalHitSound( self, weaponType, armorType ):
		"""
		���������ͷ������ͻ�ȡӦ�ò��ŵ���������
		����ǻ�ȡ��ͨ��������ʱ��Ļ�������Ч��
		@type  weaponType: INT
		@param weaponType: ��������
		@type  armorType: INT
		@param armorType: ��������
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
		���������ͷ������ͻ�ȡӦ�ò��ŵ���������
		����ǻ�ȡ��ͨ����ʩչʱ���ʩչ����Ч��
		@type  weaponType: INT
		@param weaponType: ��������
		@return String
		"""
		try:
			return self._nDatas[weaponType]["normal_sound_cast"]
		except KeyError:
			WARNING_MSG( "Can't find NormalCastSound Config by WeaponType (%s) "% weaponType )
			return ()

	def getNormalCastVoice_Man( self, weaponType ):
		"""
		���������ͷ������ͻ�ȡӦ�ò��ŵ���������
		����ǻ�ȡ��ͨ����ʩչʱ���ʩչ����Ч�� ����
		@type  weaponType: INT
		@param weaponType: ��������
		@return String
		"""
		try:
			return self._nDatas[weaponType]["normal_voice_man_cast"]
		except KeyError:
			WARNING_MSG( "Can't find NormalCastVoice Config by WeaponType (%s) "% weaponType )
			return ()

	def getNormalCastVoice_Female( self, weaponType ):
		"""
		���������ͷ������ͻ�ȡӦ�ò��ŵ���������
		����ǻ�ȡ��ͨ����ʩչʱ���ʩչ����Ч�� Ů��
		@type  weaponType: INT
		@param weaponType: ��������
		@return String
		"""
		try:
			return self._nDatas[weaponType]["normal_voice_female_cast"]
		except KeyError:
			WARNING_MSG( "Can't find NormalCastVoice Config by WeaponType (%s) "% weaponType )
			return ()

	def getSpellStartSound( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_start"]
		except:
			return ()

	def getSpellStartVoice_Man( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ�� ���� ���� by����
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_man_start"]
		except:
			return ()

	def getSpellStartVoice_Female( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ�� Ů�� ���� by����
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_female_start"]
		except:
			return ()

	def getSpellLoopSound( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_loop"]
		except:
			return ()

	def getSpellLoopVoice_Man( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������ ����
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_man_loop"]
		except:
			return ()

	def getSpellLoopVoice_Female( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������ Ů��
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_female_loop"]
		except:
			return ()

	def getSpellCastSound( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_cast"]
		except:
			return ()

	def getSpellCastVoice_Man( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������ ����
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_man_cast"]
		except:
			return ()

	def getSpellCastVoice_Female( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������ Ů��
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_voice_female_cast"]
		except:
			return ()

	def getSpellHitSound( self, skillID ):
		"""
		���ݼ���ID��ȡ�ͷ�ʱ������
		@type  skillID: INT
		@param skillID: ����ID
		@return String
		"""
		skillID = self.__idConvert( skillID )
		try:
			return self._efDatas[skillID]["spell_sound_hit"]
		except:
			return ()

	def getCameraEffectID( self, skillID ):
		"""
		��������ͷЧ��ID��ȡЧ������
		@type  effectID: INT
		@param effectID: ����ͷЧ��ID
		@return Int
		"""
		skillID = self.__idConvert( skillID )
		data = self._efDatas.get( skillID, None )
		if data is None: return 0
		return data.get( "spell_camera_effect_id", 0 )

	def getCameraEffectType( self, effectID ):
		"""
		��������ͷЧ��ID��ȡЧ������
		@type  effectID: INT
		@param effectID: ����ͷЧ��ID
		@return Int
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return 0
		return data.get( "camera_effect_type", 0 )

	def getCameraEffectLastTime( self, effectID ):
		"""
		��������ͷЧ��ID��ȡЧ������ʱ��
		@type  effectID: INT
		@param effectID: ����ͷЧ��ID
		@return Float
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return 0.0
		return data.get( "camera_effect_lastTime", 0.0 )

	def getCameraEffectRangeShake( self, effectID ):
		"""
		��������ͷЧ��ID��ȡЧ��XYZ�ζ����
		@type  effectID: INT
		@param effectID: ����ͷЧ��ID
		@return Vector3
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return Math.Vector3()
		return data.get( "camera_effect_rangeShake", Math.Vector3() )

	def getCameraEffectCenterShake( self, effectID ):
		"""
		��������ͷЧ��ID��ȡЧ�����Ļζ����
		@type  effectID: INT
		@param effectID: ����ͷЧ��ID
		@return Vector3
		"""
		data = self._caDatas.get( effectID, None )
		if data is None: return Math.Vector3()
		return data.get( "camera_effect_centerShake", Math.Vector3() )

	def getActionGrade( self, actionName ):
		"""
		���ݶ�������ȡ�������ȼ�
		@param actionName: ��������
		@type actionName: string
		@return: Int
		"""
		return self._arDatas.get( actionName, 0 )

	def getActionLimitList( self ):
		"""
		��ȡ���������б�
		@return: List
		"""
		return self._alDatas

	def checkActionLimit( self, actionName ):
		"""
		�ж϶������Ƿ��ڶ��������б���
		@param actionName: ��������
		@type actionName: string
		@return: Bool
		"""
		if actionName in self._alDatas:
			return True
		return False

	def getCameraFollowActionList( self ):
		"""
		��ȡ��ͷ���涯���б�
		@return: List
		"""
		return self._cfDatas

	def checkCameraFollowAction( self, actionName ):
		"""
		�ж϶������Ƿ��ھ�ͷ���涯���б��б���
		@param actionName: ��������
		@type actionName: string
		@return: Bool
		"""
		if actionName in self._cfDatas:
			return True
		return False

	def reset( self ):
		"""
		���¼�����������
		���ڲ���
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
#�����ͨ����ʩչ��Ч�Ĵ���
#
#Revision 1.6  2008/03/27 07:14:42  yangkai
#�������ü���
#
#Revision 1.5  2008/02/22 01:45:51  yangkai
#�߻�Ҫ��Ĭ��ͼ���Ϊ tb_yw_sj_005
#
#Revision 1.4  2008/01/25 10:07:40  yangkai
#�����ļ�·���޸�
#
#Revision 1.3  2008/01/05 03:55:28  yangkai
#��ӽӿ� getEffectConfigSect
#
#Revision 1.2  2007/12/29 09:34:12  yangkai
#��Ч���ü���
#
#Revision 1.1  2007/12/22 07:35:54  yangkai
#���ܶ�����Ч������Ч�����ش���
#

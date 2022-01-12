# -*- coding: gb18030 -*-

# $Id: PreviewRole.py,v 1.26 2008-08-20 01:47:08 yangkai Exp $


"""
candidate role, model only exists in client
-- 2006/04/21 written by wanhp( the old name Candidate )
-- 2006/08/25 modified by huangyongwei
-- 2007/02/30 rewriten by huangyongwei( from Candidate renamed to PreviewRole )
"""

import copy
import math
import BigWorld
import Math
import csdefine
import Define
import ItemTypeEnum as ITE
import event.EventCenter as ECenter
from bwdebug import *
from keys import *
from gbref import rds
from interface.GameObject import GameObject
from Function import Functor
import Const
import random
import Pixie

# --------------------------------------------------------------------
# global methods
# --------------------------------------------------------------------
def createPreviewRole( roleInfo, space ) :
	"""
	call to create a preview role
	@type			roleInfo : RoleInfo
	@param			roleInfo : instance of RoleInfo defined in RoleMaker
	@type			space	 : INT32
	@param			space	 : space id of the space the created preview locate in
	@rtype					 : PreviewRole
	@return					 : a new preview role map to roleInfo
	"""
	vehicle = 0
	position = ( 55.5, 1.0, -185.0 )
	direction = ( 0.0, 0.0, 2.76 )
	id = BigWorld.createEntity( "PreviewRole", space, vehicle, position, direction, {} )
	role = BigWorld.entity( id )
	return role


# --------------------------------------------------------------------
# implement preview role
# --------------------------------------------------------------------
class PreviewRole( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )
		self.setSelectable( True )
		self.selectable = True
		self.model = None									# ģ��
		self.talismanModel = None
		self.tam = None
		self.__roleInfo = None								# �󶨵Ľ�ɫ�����Ϣ
		self.__genderModels = {}							# �Ա����ģ��
		self.__genderModels[csdefine.GENDER_MALE]	= None
		self.__genderModels[csdefine.GENDER_FEMALE] = None
		self.__controled = False

		self.__rotateCBID = 0								# ��ɫ��תʱ�� callback ID

		self.onMouseEnter = None							# ������ʱ�������ĺ���
		self.onMouseLeave = None							# ����뿪ʱ�������ĺ���
		self.onClick = None									# �����ʱ�������ĺ���

		self.am = BigWorld.ActionMatcher( self )			# ����ƥ����
		self.am.matchCaps = [Define.CAPS_LOGIN, Define.CAPS_NOWEAPON]	# Ĭ��Caps
		self.am.turnModelToEntity = True

		self.am.boredNotifier = self.onBored				# ������ĳ���������� ���ᴥ��
		#self.am.patience = random.random() * 6 + 6.0		# ��ʼ��ʱ��patienceʱ�佻���������
		self.am.fuse = random.random() * 6 + 6.0			# ��ǰ��fuseʱ��Ҳ�����������

		# Ĭ����������Ϊ����
		self.weaponType = Define.WEAPON_TYPE_NONE
		self.randomActionsWithWeapon = []					# ��������������б�
		self.randomActionsWithDanWeapon = []				# ���ֽ�������������б�
		self.randomActionsWithShuangWeapon = []				# ˫�ֽ�������������б�
		self.randomActionsWithFuWeapon = []					# ��ͷ������������б�
		self.randomActionsWithChangWeapon = []				# ��ǹ������������б�
		self.randomActionsNoWeapon = []						# ��������������б�

		self.faceInt = 0									# ��ʱ�����������ж���ǰ��ʾЧ���Ƿ����

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def roleInfo( self ) :
		"""
		��ȡ��Ӧ��ɫ�����Ϣ
		"""
		return self.__roleInfo

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onTargetFocus( self ) :
		"""
		������ģ��ʱ������
		"""
		if self.useGlowEff and self.model and self.model.visible:
			self.model.enableShine = True

		if callable( self.onMouseEnter ) :
			self.onMouseEnter( self )

	def onTargetBlur( self ) :
		"""
		����뿪ģ��ʱ������
		"""
		if self.useGlowEff and self.model and self.model.visible:
			self.model.enableShine = False

		if callable( self.onMouseLeave ) :
			self.onMouseLeave( self )

	def onTargetClick( self, sender ) :
		"""
		�����ģ��ʱ������
		"""
		GameObject.onTargetClick( self, sender )
		if callable( self.onClick ) :
			self.onClick( self )

	# -------------------------------------------------
	def prerequisites( self ):
		"""
		����ɫ������Ϸʱ������
		���´�����Ҫ��Ϊ�˴����ɫѡ���е�Բ�̺ͽ�ɫ������ PATROL_TARGET
		"""
		if len( self.modelName ):
			return [self.modelName, ]
		return []

	def enterWorld( self ) :
		"""
		����ɫ������Ϸʱ������
		���´�����Ҫ��Ϊ�˴����ɫѡ���е�Բ��
		"""
		if len( self.modelName ) and self.model is None:
			self.model = BigWorld.Model( self.modelName )
			#if self.model:
			#	self.model.scale = (0.15, 0.15, 0.15)

	# -------------------------------------------------
	def onMovingNotify( self, isMoving ) :
		"""
		�ƶ�ʱʵʱ����
		"""
		self.notifyAttachments_( "onMovingNotify", isMoving )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setModel( self, model ):
		"""
		����ģ��
		"""
		if model is not None:
			if model.attached :
				ERROR_MSG( "model '%s' is attached!" )				# output error message -- hyw( 2009.12.25 )
				return
			self.model = model
			if self.am.owner != None: self.am.owner.delMotor( self.am )
			self.model.motors = ( self.am, )
			# ͷ������
			hairModel = model.head
			rds.actionMgr.playAction( hairModel, Const.MODEL_ACTION_HAIR_BONE_1 )
		else:
			self.model = None
			self.models = []

		# ˢ�¼�¼ģ�͵������������
		model = self.getModel()
		if hasattr( model, "shangshen1" ) :
			if model.shangshen1.tint[-2] == "_":
				if hasattr( model, "lian1" ) and not model.lian1.tint.endswith("_2") :
					tint = model.lian1.tint
					tint += "_2"
					model.lian1 = tint
		self.getRandomActions()

	def onPartModelLoad( self, model ):
		"""
		��������ģ�ͼ�����ɻص�
		"""
		self.setModel( model )
		profession = self.__roleInfo.getClass()
		gender = self.__roleInfo.getGender()
		# ���ط���
		hairNum = self.__roleInfo.getHairNumber()
		fashionNum = self.__roleInfo.getFashionNum()
		rds.roleMaker.createHairModelBG( hairNum, fashionNum, profession, gender, self.onHairModelLoad )
		# ����������ģ��
		rds.roleMaker.createMWeaponModelBG( self.__roleInfo.getRHFDict(), Functor( self.onRighthandModelLoad, self.__roleInfo.getRHFDict() ) )
		rds.roleMaker.createMWeaponModelBG( self.__roleInfo.getLHFDict(), Functor( self.onLefthandModelLoad, self.__roleInfo.getLHFDict() ) )
		# ���ط���ģ��
		rds.roleMaker.createTalismanModelBG( self.__roleInfo.getTalismanNum(), Functor( self.onTalismanModelLoad, self.__roleInfo.getTalismanNum() ) )
		# װ����������Ч��
		if not self.__roleInfo.getFashionNum():
			self.resetEquipEffect( model )
		# ��ʦ��������Ч��
		if profession == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER )

	def onHairModelLoad( self, hairModel ):
		"""
		callback Method
		���ͻ�װ��ɻص�
		"""
		if self.__roleInfo is None: return
		model = self.model
		key = "HP_head"
		rds.effectMgr.linkObject( model, key, hairModel )
		rds.actionMgr.playAction( hairModel, Const.MODEL_ACTION_HAIR_BONE_1 )

	def onRighthandModelLoad( self, weaponDict, model ):
		"""
		�����������ػص�
		"""
		if model:
			self.weaponAttachEffect( model, weaponDict )
		if self.__roleInfo is None: return
		roleModel = self.model
		if roleModel is None: return

		# ��ģ��
		key = "HP_right_hand"
		rds.effectMgr.linkObject( roleModel, key, model )

		weaponNum = self.__roleInfo.getRHFDict()["modelNum"]
		if weaponNum:
			actionName = rds.itemModel.getActionsName( weaponNum )
			if actionName:
				timetick = rds.itemModel.getTimetick( weaponNum )

				def callback():
					if not model:return
					if not model.inWorld:return
					if model.hasAction( actionName):
						rds.actionMgr.playAction( model, actionName )
					BigWorld.callback(random.randint( timetick[0], timetick[1] ),callback )
				callback()
		self.resetWeaponType()

	def onLefthandModelLoad( self, weaponDict, model ):
		"""
		��������ģ�ͼ������
		"""
		if model:
			self.weaponAttachEffect( model, weaponDict )
		if self.__roleInfo is None: return
		roleModel = self.model
		if roleModel is None: return
		profession = self.__roleInfo.getClass()
		key = "HP_left_shield"
		if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
			key = "HP_left_hand"
		rds.effectMgr.linkObject( roleModel, key, model )

		self.resetWeaponType()

	def resetWeaponType( self ):
		"""
		������������
		"""
		if self.__roleInfo is None: return
		profession = self.__roleInfo.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.__roleInfo.getLHFDict()["modelNum"]
		else:
			weaponNum = self.__roleInfo.getRHFDict()["modelNum"]

		if weaponNum:
			weaponType = Define.CLASS_WEAPONTYPE.get( profession, [] )
			if len( weaponType ) == 0: weaponType = 0
			if profession == csdefine.CLASS_SWORDMAN:    # ����
				if not self.__roleInfo.getLHFDict()["modelNum"]:
					weaponType = weaponType[0]
				else:
					weaponType = weaponType[1]
			elif profession == csdefine.CLASS_FIGHTER:  #սʿ
				if str( weaponNum )[1:3] == str(Define.PRE_EQUIP_TWOLANCE):
					weaponType = weaponType[1]
				else:
					weaponType = weaponType[0]
			else:
				weaponType = weaponType[0]
			self.weaponType = weaponType
		else:
			self.weaponType = 0
		# ����Caps״̬
		self.setArmCaps()

	def weaponAttachEffect( self, model, weaponDict ):
		"""
		������������Ч��
		@type		model 		: pyModel
		@param		model 		: ģ��
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��������
		"""
		pType = Define.TYPE_PARTICLE_PLAYER
		# ģ��Dyes
		dyes = rds.roleMaker.getMWeaponModelDyes( weaponDict )
		rds.effectMgr.createModelDye( model, dyes )
		# �Դ���Ч
		weaponNum = weaponDict["modelNum"]

		effectIDs = rds.itemModel.getMEffects( weaponNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, pType, pType )
			effect.start()

		if model.hasAction( "wwm_01_036_animations" ):
			rds.actionMgr.playAction( model, "wwm_01_036_animations" )

		# ��Ƕ��Ч
		stAmount = weaponDict["stAmount"]
		xqHp = rds.equipParticle.getXqHp( stAmount )
		xqGx = rds.equipParticle.getXqGx( stAmount )
		for hp, particle in zip( xqHp, xqGx ):
			rds.effectMgr.createParticleBG( model, hp, particle, type = pType )
		# ǿ���Է���
		intensifyLevel = weaponDict["iLevel"]
		if intensifyLevel >= Const.EQUIP_WEAPON_GLOW_LEVEL:
			paths = rds.roleMaker.getMWeaponModelPath( weaponDict )
			if len( paths ) == 0: return
			weaponKey = paths[0]
			type = rds.equipParticle.getWType( weaponKey )
			if not type:return
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )

	def resetEquipEffect( self, model ):
		"""
		ˢ�¹�ЧЧ������
		"""
		profession = self.__roleInfo.getClass()
		gender = self.__roleInfo.getGender()
		bodyFDict = self.__roleInfo.getBodyFDict()
		feetFDict = self.__roleInfo.getFeetFDict()

		######################�ز���Ч#################################
		intensifyLevel = bodyFDict["iLevel"]
		# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		###########Ь�ӹ�Ч######################################################
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )


	def createTalismanAM( self ):
		"""
		��������motor
		"""
		# ����Բ�ι켣motor������motor�Ĳ���
		self.tam = BigWorld.Orbitor()
		self.tam.spinRadius = 0.5
		self.tam.startSpin = 0.5
		self.tam.endSpeed = 1.0
		self.tam.speed = 1.0
		self.tam.wobble = True
		self.tam.wobbleFreq = 0.45
		self.tam.wobbleMax = 0.4
		self.tam.proximity = 0.8
		self.tam.target = rds.effectMgr.accessNode( self.getModel(), "HP_right_shoulder" )

	def setTalismanModel( self, model ):
		"""
		���÷���ģ��
		"""
		if self.talismanModel and self.talismanModel in list( self.models ):
			self.delModel( self.talismanModel )
		self.talismanModel = model
		if self.talismanModel:
			self.addModel( self.talismanModel )
			self.talismanModel.position = self.position + ( 1.2, 1.7, 0.0 )
			rds.actionMgr.playAction( self.talismanModel, Const.MODEL_ACTION_PLAY )
			if self.tam is None:
				self.createTalismanAM()
			else:
				if self.tam.owner != None: self.tam.owner.delMotor( self.tam )
			self.talismanModel.addMotor( self.tam )

	def onTalismanModelLoad( self, talismanNum, model ):
		"""
		����ģ�ͼ��ػص�
		"""
		# ����Dyes
		talismanDyes = rds.roleMaker.getTalismanModelDyes( talismanNum )
		rds.effectMgr.createModelDye( model, talismanDyes )
		# �Դ���Ч
		effectIDs = rds.itemModel.getMEffects( talismanNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
			effect.start()

		self.setTalismanModel( model )

	def setInfo( self, info ):
		"""
		���ý�ɫ�����Ϣ
		"""
		self.__roleInfo = info

	def setToControl( self ) :
		"""
		����Ϊ�ɿͻ��˶�������
		"""
		self.__controled = True
		BigWorld.controlEntity( self, True )
		self.physics = STANDARD_PHYSICS									# defined in keys.py
		self.physics.velocity = ( 0.0, 0.0, 0.0 )
		self.physics.velocityMouse = "Direction"
		self.physics.angular = 0
		#self.physics.angularMouse = "MouseX"
		self.physics.collide = False
		self.physics.gravity = 0
		self.physics.fall = False
		self.physics.userDirected = False								# ����Ǳ���ģ������ģ�͵�yaw������귽��ı�
		self.physics.isMovingNotifier = self.onMovingNotify

	def destroy( self ) :
		"""
		����ģ��
		"""
		BigWorld.controlEntity( self, False )
		BigWorld.destroyEntity( self.id )

	def setArmCaps( self ) :
		"""
		set caps
		"""
		if self.__roleInfo is None: return

		profession = self.__roleInfo.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.__roleInfo.getLHFDict()["modelNum"]
		else:
			weaponNum = self.__roleInfo.getRHFDict()["modelNum"]

		armCaps = []
		if weaponNum:
			if profession == csdefine.CLASS_FIGHTER:
				armCaps.append( Define.CAPS_CHANG_WEAPON )	# ��ǹ
			elif profession == csdefine.CLASS_SWORDMAN:
				armCaps.append( Define.CAPS_DAN_WEAPON )	# ���ֽ�
			else:
				armCaps.append( Define.CAPS_WEAPON )
			#if self.weaponType == Define.WEAPON_TYPE_LIGHTSHARP:
			#	armCaps.append( Define.CAPS_DAN_WEAPON )	# ���ֽ�
			#elif self.weaponType == Define.WEAPON_TYPE_DOUBLEHAND:
			#	armCaps.append( Define.CAPS_SHUANG_WEAPON )	# ˫�ֽ�
			#elif self.weaponType == Define.WEAPON_TYPE_WEIGHTSHARP:
			#	armCaps.append( Define.CAPS_FU_WEAPON )		# ��ͷ
			#elif self.weaponType == Define.WEAPON_TYPE_LIGHTBLUNT:	
			#	armCaps.append( Define.CAPS_CHANG_WEAPON )	# ��ǹ
			#else:
			#	armCaps.append( Define.CAPS_WEAPON )
		else:
			armCaps.append( Define.CAPS_NOWEAPON )
		stateCaps = Define.CAPS_LOGIN
		if stateCaps is None:
			caps = armCaps
		else:
			caps = [stateCaps] + armCaps
		self.am.matchCaps = caps

	# ----------------------------------------------------------------
	# ����������
	# ----------------------------------------------------------------
	def switchRandomAction( self, isTigger ):
		"""
		"""
		if isTigger:
			value = random.random() * 6 + 6.0
		else:
			value = 0.0
		self.am.patience = value

	def onBored( self, actionName ):
		"""
		�˻ص����ڲ����������
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		# ���action �ǿ�ʱ������fuse�����¿�ʼ��ʱ
		if actionName is None: return

		# ����գ�۾�( 0-8 )�����֮�󣬲���գ�۶���
		BigWorld.callback( random.random() * 8, self.playNictation )

		# ֻ��վ�ŵ�ʱ��Ų����������
		if actionName == "login_stand": self.playRandomAction()
		# ��һ��������ʼ����ʱ fuse ������Ϊ0
		# �����ƺ���bug����ʱ��û������ fuse ������ԣ���������������
		self.am.fuse = 0
		# ÿ֪ͨһ�� onBored  ������Զ��� patience ��Ϊһ����ֵ??
		# ֻ������ patience ֵ ���������Ĳ�ͣ���� onBored ����
		self.am.patience = random.random() * 6 + 6.0

	def playRandomAction( self ):
		"""
		play random Action
		"""
		caps = self.am.matchCaps
		if Define.CAPS_LOGIN not in caps: return

		# �������������Ͳ������������Ĵ���
		if Define.CAPS_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithWeapon )
		elif Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithDanWeapon )
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithShuangWeapon )
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithFuWeapon )
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithChangWeapon )
		else:
			randomActionCount = len( self.randomActionsNoWeapon )

		# ȡ������
		if randomActionCount == 0: return
		index = random.randint( 0, randomActionCount - 1 )
		capsIndex = Define.CAPS_INDEX25 + index

		caps.remove( Define.CAPS_LOGIN )
		caps.append( capsIndex )
		caps.append( Define.CAPS_RANDOM )
		self.am.matchCaps = caps

		BigWorld.callback( 0.1, self.onOneShoot )

	def onOneShoot( self ):
		"""
		<oneShot>
		Setting this to TRUE means that the Action Matcher will not continue
		playing that action past one cycle of it, if it is no longer triggered,
		but a <cancel> section was keeping it active.
		"""
		# ����Ѳ�����Ұ�����
		if not self.inWorld: return
		self.setArmCaps()

	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		��ȡ���������������������������̶���
		��ȡ���������random1��ʼ��random2,random3....��ȡʧ���򷵻�
		"""
		if self.model is None: return

		# ��������������б�
		self.randomActionsWithWeapon = []
		# �������������������������������ֿ�����
		for index in range(1,10):
			weaponActName = "random%s" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithWeapon.append( weaponActName )
			else:
				break

		# ���ֽ�������������б�
		self.randomActionsWithDanWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_dan" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithDanWeapon.append( weaponActName )
			else:
				break

		# ˫�ֽ�������������б�
		self.randomActionsWithShuangWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_shuang" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithShuangWeapon.append( weaponActName )
			else:
				break

		# ��ͷ������������б�
		self.randomActionsWithFuWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_fu" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithFuWeapon.append( weaponActName )
			else:
				break

		# ��ǹ������������б�
		self.randomActionsWithChangWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_chang" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithChangWeapon.append( weaponActName )
			else:
				break

		# ��������������б�
		self.randomActionsNoWeapon = []
		for index in xrange( 1, 10 ):
			noWeaponActName = "random%s_noweapon" % index
			if self.model.hasAction( noWeaponActName ):
				self.randomActionsNoWeapon.append( noWeaponActName )
			else:
				break

	def playPoseAction( self, delay = 0.0, cb = None ):
		"""
		play pose Action
		"""
		if self.model is None: return False
		if not self.inWorld: return False

		def onActionOver():
			if callable( cb ):cb()
			if self.model is None: return
			if "newlybuilt" in self.model.queue: return
			self.switchLoft( False )

		self.setArmCaps()
		if Define.CAPS_WEAPON in self.am.matchCaps:
			index = 1
		elif Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			index = 2
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			index = 3
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			index = 4
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			index = 5
		else:
			index = 0
		
		newlybuilt_list = Const.MODEL_ACTION_NEWLYBUILT_LIST
		rds.actionMgr.playAction( self.model, newlybuilt_list[index], time = delay, callback = onActionOver )
		self.playPoseEffect()
		return True

	def playPoseEffect( self ):
		"""
		����ְҵ��ʾЧ��
		"""

		def loadParticle( lastTime, hp, path ):
			"""
			�ӳټ�������
			"""
			def onParticleLoad( particle ):
				"""
				���Ӽ�����ɻص�
				"""
				if particle is None: return
				if not self.inWorld: return
				if faceInt != self.faceInt: return
				rds.effectMgr.attachObject( model, hp, particle )
				particle.force()
				functor = Functor( onFadeOut, hp, particle )
				BigWorld.callback( lastTime, functor )

			def onFadeOut( hp, particle ):
				"""
				��������
				"""
				rds.effectMgr.fadeOutParticle( particle )
				functor = Functor( onDetach, hp, particle )
				BigWorld.callback( 3.0, functor )

			def onDetach( hp, particle ):
				"""
				ж������
				"""
				rds.effectMgr.detachObject( model, hp, particle )

			if not self.inWorld: return
			if faceInt != self.faceInt: return
			rds.effectMgr.pixieCreateBG( path, onParticleLoad )

		model = self.model
		self.faceInt += 1
		faceInt = self.faceInt
		profession = self.__roleInfo.getClass()
		data = Const.ROLE_CREATE_EFFECT_CLASS_MAP.get( profession )
		if data is None: data = []
		for delayTime, lastTime, hp, path in data:
			functor = Functor( loadParticle, lastTime, hp, path )
			BigWorld.callback( delayTime, functor )
		if profession in [ csdefine.CLASS_FIGHTER, csdefine.CLASS_SWORDMAN ]:
			self.switchLoft( True )

	def switchLoft( self, switch ):
		attachments = []
		model = self.model
		if hasattr( model, "right_hand" ) and model.right_hand:
			rightHand = model.right_hand
			if hasattr( rightHand, "sfx1" ):
				attachments.extend( rightHand.node("HP_sfx1").attachments )
			if hasattr( rightHand, "sfx2" ):
				attachments.extend( rightHand.node("HP_sfx2").attachments )
		if hasattr( model, "left_hand" ) and model.left_hand:
			leftHand = model.left_hand
			if hasattr( leftHand, "sfx1" ):
				attachments.extend( leftHand.node("HP_sfx1").attachments )
			if hasattr( leftHand, "sfx2" ):
				attachments.extend( leftHand.node("HP_sfx2").attachments )
		for particle in attachments:
			if not isinstance( object, Pixie.MetaParticleSystem ): continue
			system = particle.system(0)
			if system is None: continue
			render = system.renderer
			if render.__class__.__name__ != "LoftRenderer": continue
			if switch:
				render.start()
			else:
				render.stop()

	def playNictation( self, key = None ):
		"""
		գ�۾�
		"""
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return

		# �����ɵ���dye���Ա�ָ�
		oldTint = model.lian1.tint
		if hasattr( model, "shangshen1" ) :
			if model.shangshen1.tint[-2] == "_":
				if "_nictation_2" in oldTint: return
				if not oldTint.endswith("_2"):
					oldTint = oldTint + "_2"
				oldTint = oldTint.replace("_2","_nictation_2")
				model.lian1 = oldTint
			else:
				if "_nictation" in oldTint: return
				if oldTint.endswith("_2"):
					oldTint = oldTint.replace("_2","")
				oldTint = oldTint + "_nictation"
				model.lian1 = oldTint
		else:
			if "_nictation" in oldTint: return
			if oldTint.endswith("_2"):
				oldTint = oldTint.replace("_2","")
			oldTint = oldTint + "_nictation"
			model.lian1 = oldTint

		# ����գ��6-9�룬�ָ��ɵ���dye
		faceNum = self.__roleInfo.getFaceNumber()
		functor = Functor( self.onPlayNictationOver, oldTint, faceNum )
		BigWorld.callback( random.random() * 3 + 6, functor )

	def onPlayNictationOver( self, oldTint, oldFaceNum ):
		"""
		գ�۶����������
		"""
		# ������ܻ��漰
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return

		faceNum = self.__roleInfo.getFaceNumber()
		if faceNum != oldFaceNum: return

		if oldTint.endswith("_nictation"):
			oldTint = oldTint.replace( "_nictation", "" )
		elif oldTint.endswith("_nictation_2"):
			oldTint = oldTint.replace( "_nictation_2", "_2" )
		if hasattr( model, "shangshen1" ):
			if model.shangshen1.tint[-2] == "_" and not oldTint.endswith("_2"):
				oldTint = oldTint + "_2"
			elif model.shangshen1.tint[-2] != "_" and oldTint.endswith("_2"):
				oldTine = oldTint.replace("_2","")
		elif oldTint.endswith("_2"):
			oldTint = oldTint.replace("_2","")

		model.lian1 = oldTint

	# -------------------------------------------------
	def faceTo( self, pos, callback = None ) :
		"""
		������������
		@type			pos		 : Vector3
		@param			pos		 : ���������
		@type			callback : functor
		@param			callback : ��ת�ص������������һ��������ָ�������Ƿ�ɹ�
		"""
		yaw = ( pos - self.position ).yaw
		self.physics.seek( ( 0, 0, 0, yaw ), 1, 0, callback )

	def oppositeTo( self, pos, callback = None ) :
		"""
		���ñ�������
		@type			pos		 : Vector3
		@param			pos		 : ���������
		@type			callback : functor
		@param			callback : ��ת�ص������������һ��������ָ�������Ƿ�ɹ�
		"""
		yaw = ( self.position - pos ).yaw
		self.physics.seek( ( 0, 0, 0, yaw ), 1, 0, callback )

	def turnaround( self, deltaRadian, callback = None ) :
		"""
		��תָ���Ƕ�
		@type			deltaRadian	: float
		@param			deltaRadian	: ��ת�Ļ���
		@type			callback	: functor
		@param			callback	: ��ת�ص������������һ��������ָ�������Ƿ�ɹ�
		"""
		self.physics.seek( ( 0, 0, 0, self.yaw + deltaRadian ), 1, 0, callback )
	
	def turnaroundToYaw( self, deltaRadian, callback = None ) :
		"""
		��תָ���Ƕ�
		@type			deltaRadian	: float
		@param			deltaRadian	: ��ת�Ļ���
		@type			callback	: functor
		@param			callback	: ��ת�ص������������һ��������ָ�������Ƿ�ɹ�
		"""
		self.physics.seek( ( 0, 0, 0, deltaRadian ), 1, 0, callback )

	def instantRotate( self, srcPos, dstPos, callback = None ) :
		"""
		��ת�ĽǶ�Ϊ��srcPos �������Ƕ� �� dstPos �������ǶȲ�
		@type				srcPos		: Vector3
		@param				srcPos		: ��תǰ����������
		@type				dstPos		: Vector3
		@param				dstPos		: ��ת�����������
		@type				callback	: functor
		@param				callback	: ��ת������ĵ���
		@return							: None
		"""
		srcPos = Math.Vector3( srcPos )							# ��תǰ����������
		dstPos = Math.Vector3( dstPos )							# ��ת�����������
		dstYaw = ( dstPos - self.position ).yaw					# ��ת��ķ���
		srcYaw = ( srcPos - self.position ).yaw					# ��תǰ�ķ���
		self.turnaround( dstYaw - srcYaw )						# ��ת��ǰ������ǶȲ�
		if callback:
			callback()

	def sostenutoRotate( self, srcPos, dstPos, stepRadians, rotateSpeed = 0.1, cbArrived = None, cbRotating = None ):
		"""
		��һ���ٶȳ�������ת�Լ�����ת�ĽǶ�Ϊ��srcPos �������Ƕ� �� dstPos �������ǶȲ�
		@type				srcPos		: Vector3
		@param				srcPos		: ��תǰ����������
		@type				dstPos		: Vector3
		@param				dstPos		: ��ת�����������
		@type				stepRadians	: float
		@param				stepRadians	: ÿ tick ��ת�ĵĲ���(����)
		@type				rotateSpeed	: int
		@param				rotateSpeed	: �ٶ�(��λ����/��)
		@type				cbArrived	: functor
		@param				cbArrived	: ��ת������ĵ��ã�����һ����������ʾ��ת����ʱ���Ƿ�������ת��λ
		@type				cbRotating	: functor
		@param				cbRotating	: ��ת������ÿ tick �Ļص�
		@return							: None
		"""
		if self.__rotateCBID != 0 :							# �����ǰ������ת
			BigWorld.cancelCallback( self.__rotateCBID )	# ��ֹͣ��ǰ����ת״̬
			self.__rotateCBID = 0

		srcPos = Math.Vector3( srcPos )						# ��תǰ����������
		dstPos = Math.Vector3( dstPos )						# ��ת�����������
		srcYaw = ( srcPos - self.position ).yaw				# ��תǰ�ķ���
		dstYaw = ( dstPos - self.position ).yaw				# ��ת��ķ���
		deltaRadian = dstYaw - srcYaw						# ��ת������תǰ������ǶȲ�
		if deltaRadian > math.pi :
			deltaRadian = 2 * math.pi - deltaRadian
			stepRadians = -stepRadians						# ͨ�� stepRadians ��������ȷ����ת�ķ���
		elif deltaRadian < -math.pi :
			deltaRadian = 2 * math.pi + deltaRadian

		def rotate( radians, stepRadians ) :				# ѭ����ת radians ��
			if radians == 0 :								# ��ת����
				if cbArrived : cbArrived( True )
				return
			if radians > abs( stepRadians ) :
				radians -= abs( stepRadians )
			else :
				if stepRadians < 0 : stepRadians = -radians
				else : stepRadians = radians
				radians = 0
			if self.physics is None :						# ���󱻳���
				if cbArrived : cbArrived( False )			# ��ת����;ʱʧ��
				return
			self.physics.seek( ( 0, 0, 0, self.yaw + stepRadians ), 1, 0, None )
			if cbRotating : cbRotating( self.yaw )
			self.__rotateCBID = BigWorld.callback( rotateSpeed, Functor( rotate, radians, stepRadians ) )
		rotate( abs( deltaRadian ), stepRadians )

	def velocityTo( self, position, speed, callback = None, isSeekToGoal = True ) :
		"""
		velocity to one position( when arrived destination, it will not stop, so you must set stop at callback )
		ע����ǰ�ƶ���ָ��λ��ʱ��ͣ������Ϊ�˾�ȷ��������Ҫ�޸ĵײ�physics.seek()�ӿڣ����롰������Ƿ���velocityΪ0���Ĳ����������
		add: �ײ��������� isSeekToGoal ΪFalse ʱ�� Ŀ��ڵ���������˶�ƽ������
		@type			position	: Vector3
		@param			position	: �ƶ�����Ŀ��λ��
		@type			speed		: Float
		@param			speed		: �ƶ��ٶ�
		@type			callback	: Fucntor
		@param			callback	: ����Ŀ�ĵ��Ļص�
		@type			isSeekToGoal  : bool
		@param          isSeekToGoal  ���Ƿ�ǿ�Ƶ���ָ����Ŀ���
		@return						  : None
		"""
		BigWorld.dcursor().yaw = 0
		pos = Math.Vector3( position )
		dist = pos.distTo( self.position )
		needTime = dist * 1.5 / speed

		self.physics.velocity = 0, 0, speed
		yaw = ( pos - self.position ).yaw
		self.physics.seek( ( pos.x,pos.y,pos.z, yaw ), needTime, 0.1, callback, isSeekToGoal )

	def stopVelocity( self ) :
		"""
		ֹͣ�ƶ�
		@return						: None
		"""
		self.physics.stop( True )		# stop velocity
		if self.physics.seeking:
			self.physics.seek( None )	# stop seek


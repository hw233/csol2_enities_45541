# -*- coding: gb18030 -*-
import math

import BigWorld
import Math
from Function import Functor
import cschannel_msgs
import Define
import Const
import csdefine
import Pixie
from gbref import rds
from interface.GameObject import GameObject
import event.EventCenter as ECenter
from RoleMaker import RoleInfo
from config.client.DanceActivityConfig import Datas
titleColor = {'gold':(218,178,115,255),'sliver':(233,233,216,255), 'copper':(186,110,64,255), 'wait':(255,255,255,255)}

class DanceKing( GameObject ):
	def __init__( self ):
		GameObject.__init__( self )
		self.talismanModel = None
		self.modelScale = 1.0
		self.equipEffects = []

	def onCacheCompleted( self ):
		self.createModel()
		GameObject.onCacheCompleted( self )
	

	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT1 )

	def createModel( self ):
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			self.am.matchCaps = [Define.CAPS_ENVIRONMENT_OBJECT]
		self.createEquipModel( Define.MODEL_LOAD_ENTER_WORLD )

	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		GameObject.onModelChange( self, oldModel, newModel )
		if newModel is None: return
		if self.am.owner != None: self.am.owner.delMotor( self.am )
		newModel.motors = ( self.am, )
		newModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
		self.flushAttachments_()

	def createEquipModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		����װ��ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		paths = self.getEquipModelPaths()
		functor = Functor( self.onEquipModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getEquipModelPaths( self ):
		"""
		��ȡװ��ģ��·��
		@return dict
		"""
		roleInfo = self.getModelInfo()
		paths = {}
		profession = self.getClass()
		gender = self.getGender()
		# ��ɫ����ģ��
		bodyPaths= rds.roleMaker.getShowModelPath( roleInfo )
		if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
		# ����ģ�ͷ���
		hairPaths = rds.roleMaker.getHairModelPath( self.hairNumber, self.fashionNum, profession, gender )
		if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths
		# ����ģ����������
		rightHandPaths = rds.roleMaker.getMWeaponModelPath( self.righthandFDict )
		if len( rightHandPaths ): paths[Define.MODEL_EQUIP_RHAND] = rightHandPaths
		# ����ģ����������
		leftHandPaths = rds.roleMaker.getMWeaponModelPath( self.lefthandFDict )
		if len( leftHandPaths ): paths[Define.MODEL_EQUIP_LHAND] = leftHandPaths
		return paths

	def onEquipModelLoad( self, event, modelDict ):
		"""
		װ��ģ�ͼ������
		"""
		if not self.inWorld: return

		mainModel = self.composeEquipModel( modelDict )
		self.setModel( mainModel, event )
		self.setArmCaps()
		if self.locationIndex:
			if self.getDictFromDatas(self.locationIndex):
				path = self.getDictFromDatas(self.locationIndex)["path"]
				hardPoint = self.getDictFromDatas(self.locationIndex)["hardPoint"]
				p =  Pixie.create(path)
				self.model.node(hardPoint).attach( p )
				p.force()
			else:
				print "DanceActivityConfig has not index",self.locationIndex,"config about particle"

		rds.actionMgr.playAction(self.model, "dance")   #ģ�ͼ����꣬���Ŷ���dance
		self.model.scale = (self.modelScale, self.modelScale, self.modelScale)  #����ģ�ʹ�С

	def setArmCaps( self ):
		"""
		set caps
		"""
		if not self.inWorld: return
		profession = self.raceclass & csdefine.RCMASK_CLASS
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.lefthandFDict["modelNum"]
		else:
			weaponNum = self.righthandFDict["modelNum"]

		armCaps = []
		if weaponNum:
			if profession == csdefine.CLASS_SWORDMAN:
				if not self.lefthandFDict["modelNum"]:
					armCaps.append( Define.CAPS_DAN_WEAPON )	# ���ֽ�
				else:
					armCaps.append( Define.CAPS_SHUANG_WEAPON )	# ˫�ֽ�
			elif profession == csdefine.CLASS_FIGHTER:
				if str( weaponNum )[1:3] == str(Define.PRE_EQUIP_TWOLANCE):
					armCaps.append( Define.CAPS_CHANG_WEAPON )	# ��ǹ
				else:
					armCaps.append( Define.CAPS_FU_WEAPON )		# ��ͷ

		self.am.matchCaps = [Define.CAPS_ENVIRONMENT_OBJECT] + armCaps

	def getModelInfo( self ):
		"""
		��ȡ����ģ����ر�Ҫ����Ϣ
		"""
		infoDict = {}
		infoDict["roleID"]			= 0
		infoDict["roleName"]	 	= self.uname
		infoDict["level"]			= 0
		infoDict["raceclass"]		= self.raceclass
		infoDict["hairNumber"]		= self.hairNumber
		infoDict["faceNumber"]		= self.faceNumber
		infoDict["bodyFDict"]		= self.bodyFDict
		infoDict["volaFDict"]		= self.volaFDict
		infoDict["breechFDict"]		= self.breechFDict
		infoDict["feetFDict"]		= self.feetFDict
		infoDict["lefthandFDict"]	= self.lefthandFDict
		infoDict["righthandFDict"]	= self.righthandFDict
		infoDict["talismanNum"]		= self.talismanNum
		infoDict["fashionNum"]		= self.fashionNum
		infoDict["adornNum"]		= self.adornNum
		infoDict["headTextureID"]	= 0
		return RoleInfo( infoDict )

	def composeEquipModel( self, modelDict ):
		"""
		���װ��ģ��
		"""
		# ����ģ��
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None: return
		roleInfo = self.getModelInfo()
		rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
		#����ģ�ͷ���
		headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
		self.attachHairModel( mainModel, headModel )
		profession = self.getClass()
		gender = self.getGender()
		rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
		"""
		# ����ģ����������
		righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
		self.attachRHModel( mainModel, righthandModel )
		self.weaponAttachEffect( righthandModel, self.righthandFDict  )
		# ����ģ����������
		lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
		self.attachLHModel( mainModel, lefthandModel )
		self.weaponAttachEffect( lefthandModel, self.lefthandFDict )
		"""
		# �������ʱװģʽ������ʾ����װ������Ч��
		if not self.fashionNum: self.resetEquipEffect( mainModel )
		# ���ְҵ�Ƿ�ʦ������ʾ�ŵ�����Ч��
		if self.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = Define.TYPE_PARTICLE_NPC )

		return mainModel

	def weaponAttachEffect( self, model, weaponDict ):
		"""
		������������Ч��
		@type		model 		: pyModel
		@param		model 		: ģ��
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��������
		"""
		pType = Define.TYPE_PARTICLE_NPC
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
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )


	def resetEquipEffect( self, model ):
		"""
		ˢ�¹�ЧЧ������
		"""
		self.equipEffects = []

		######################�ز���Ч#################################
		bodyFDict = self.bodyFDict
		profession = self.getClass()
		gender = self.getGender()
		intensifyLevel = bodyFDict["iLevel"]
		# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		###########Ь�ӹ�Ч######################################################
		feetFDict = self.feetFDict
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )


	def onEquipParticleLoad( self, particle ):
		"""
		װ���������Ӽ������
		"""
		if not self.inWorld: return
		if particle is None: return
		self.equipEffects.append( particle )

		roleModel = self.getModel()
		if roleModel and roleModel.visible:
			visible = True
		else:
			visible = False

		rds.effectMgr.fadeOutParticle( particle )

	def attachHairModel( self, mainModel, hairModel ):
		"""
		����ͷ��
		"""
		rds.effectMgr.linkObject( mainModel, Const.MODEL_HAIR_HP, hairModel )
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )

	def attachRHModel( self, mainModel, rModel ):
		"""
		װ������ģ��
		"""
		if not hasattr( mainModel, "right_hand" ): return
		# ��ģ��
		rds.effectMgr.linkObject( mainModel, Const.MODEL_RIGHT_HAND_HP, rModel )
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )

	def attachLHModel( self, mainModel, lModel ):
		"""
		װ������ģ��
		"""
		if not hasattr( mainModel, "left_hand" ): return
		# ��ģ��
		profession = self.getClass()
		key = Const.MODEL_LEFT_SHIELD_HP
		if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
			key = Const.MODEL_LEFT_HAND_HP
		rds.effectMgr.linkObject( mainModel, key, lModel )
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )

	def attachTalismanModel( self, mainModel, talismanModel ):
		"""
		���ӷ���ģ��
		"""
		matrixProvider = rds.effectMgr.accessNode( mainModel, Const.TALISMAN_TARGET_HP )
		self.setTalismanModel( talismanModel, matrixProvider )

	def setTalismanModel( self, model, matrixProvider ):
		"""
		���÷���ģ��
		"""
		self.talismanModel = model
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )
		if self.talismanModel is None: return
		self.addModel( self.talismanModel )
		self.talismanModel.position = self.position + ( 1.2, 1.7, 0.0 )
		rds.actionMgr.playAction( self.talismanModel, Const.MODEL_ACTION_PLAY )
		#if self.tam is None: self.createTalismanAM()
		#self.setTalismanTarget( matrixProvider )
		#self.talismanModel.addMotor( self.tam )

	def setModelVisible( self, visibleType ):
		if not self.model:
			return

		self.setVisibility( True )
		self.model.visibleAttachments = False

	def setVisibility( self, visible ) :
		"""
		����ģ�Ϳɼ���
		hyw -- 09.01.10
		"""
		GameObject.setVisibility( self, visible )
		# ����ģ��
		model = self.getModel()
		if model and model != self.model:
			model.visible = visible

	def setName( self, uname ):
		"""
		define method.
		��������
		"""
		self.uname = uname
		ECenter.fireEvent( "EVT_ON_DANCEKING_NAME_CHANGED", self.id, uname )
		

	def getName( self ):
		"""
		ȡ��entity����
		"""
		return self.uname

	def setTitle( self, title ):
		# define method
		self.title = self.getTitlefromIndex(self.locationIndex)
		if self.title:
			ECenter.fireEvent( "EVT_ON_DANCEKING_TITLENAME_CHANGE", self.id, title )
			#ECenter.fireEvent( "EVT_ON_DANCEKING_TITLECOLOR_CHANGE", self.id, self.getColorfromIndex(self.locationIndex) )
		

	def getTitle( self ):
		"""
		virtual method.
		��ȡͷ��
		@return: string
		"""
		return self.title

	def setRaceclass( self, race ):
		# define method
		self.raceclass = race

	def isRaceclass( self, rc, mask = csdefine.RCMASK_ALL):
		"""
		�Ƿ�Ϊָ������ְҵ��
		@return: bool
		"""
		return self.raceclass & mask == rc

	def getClass( self ):
		"""
		ȡ������ְҵ
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def getGender( self ):
		"""
		ȡ�������Ա�
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getRace( self ):
		"""
		ȡ����������
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_RACE

	def getFaction( self ):
		"""
		ȡ����������������
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_FACTION ) >> 12

	def setHairNumber( self, hair ):
		# define method
		self.hairNumber = hair

	def setFaceNumber( self , face ):
		# define method
		self.faceNumber = face

	def setBodyFDict( self, body ):
		# define method
		self.bodyFDict = body

	def setVolaFDict( self, volaf ):
		self.volaFDict = volaf

	def setBreechFDict( self, breechf ):
		# define method
		self.breechFDict = breechf

	def	setFeetFDict( self, feet ):
		# define method
		self.feetFDict = feet

	def setLefthandFDict( self, lefthand ):
		# define method
		self.lefthandFDict = lefthand

	def setRighthandFDict( self, righthand ):
		# define method
		self.righthandFDict = righthand

	def setTalismanNum( self, talisman ):
		# define method
		self.talismanNum = talisman

	def setFashionNum( self, fashion ):
		# define method
		self.fashionNum = fashion

	def setAdornNum( self, adorn ):
		# define method
		self.adornNum = adorn

	def setHeadTextureID( self, headTexture ):
		# define method
		self.headTextureID = headTexture

	def setAction( self, act ):
		# define method
		self.playAction = act

	def setModelScale( self, modelScale ):
		# define method
		self.modelScale = modelScale
		
	def setTongName( self, tongName ):
		# define method
		self.tongName = tongName
		
	def getDictFromDatas(self, index):
		for item in Datas:
			if index == item["locationIndex"]:
				return item
		return None

	def getColorfromIndex(self, index):
		if index == 1:
			return titleColor['gold']
		if index < 4:
			return titleColor['sliver']
		if index < 10:
			return titleColor['copper']
		if index < 20:
			return titleColor['wait']
	
	def getTitlefromIndex(self, index):
		if index == 1:
			return cschannel_msgs.DANCEGOLD
		if index < 4:
			return cschannel_msgs.DANCESILVER
		if index < 10:
			return cschannel_msgs.DANCECOPPER
		if index < 20:
			return 	cschannel_msgs.DANCEWAIT
		return ''

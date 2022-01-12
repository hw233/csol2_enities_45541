
# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.99 2008-08-29 02:38:42 huangyongwei Exp $

"""
�����࣬�̳���NPC
"""

import BigWorld
import GUI
from bwdebug import *
import csdefine
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit

import GUIFacade
import Define
import ItemTypeEnum
from utils import *
from gbref import rds
from UnitSelect import UnitSelect
import event.EventCenter as ECenter
from Sound import soundMgr
import random
import EntityCache
import csconst
import csstatus
import csstatus_msgs as StatusMsgs
import Const
from Function import Functor
from config.client.MonsterBlastConfig import Datas as MONSTERBLASTDATAS #add by wuxo 2011-11-17
import Math
from ModelLoaderMgr import ModelLoaderMgr
import csol
import skills
import Timer
import math
from config.client.BossGethitLightAndRockIDs import Datas as bossGetHitDatas
from config.client.SkillCauseLightAndRockIDs import Datas as skillCauseDatas
g_entityCache = EntityCache.EntityCache.instance()
g_mlMgr = ModelLoaderMgr.instance()      # ΢��ģ����Դ���ع�����

ACTION_MAPS = {	"walk" 			: [ "ride_walk", "crossleg_walk"],
				"run" 			: [ "ride_run", "crossleg_run" ],
				"stand"			: [ "ride_stand", "crossleg_stand" ],
					}

class Monster( NPCObject, CombatUnit ):
	"""
	����NPC��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.am = None
		# ��¼Monster ������������ϣ������Ի�����ģ�͵ĸı���ı�
		self.randomActions = []
		# Ĭ����������Ϊ����
		self.weaponType = Define.WEAPON_TYPE_NONE
		# Ĭ�Ϸ�������Ϊ�޷���
		self.armorType = Define.ARMOR_TYPE_EMPTY
		# skeletonCollider attr
		#self.skeletonCollider = BigWorld.SkeletonCollider()
		self.lefthandNumber = 0
		self.righthandNumber = 0
		self.canShowDescript = False	# �Ƿ���ʾ����
		self.takeLevel = -1	# ��Я���ȼ���10:15 2009-4-23��wsf

		self.isBlastFlag = False	#����Ƿ�Ӧ�ò��ű�ʬЧ�� add by wuxo 2011-11-17
		self.bootyOwner = ( 0, 0 )

		self.moveTime = 0.0
		self.faceTimerID = 0
		self.standbyEffect = None		# ������Ч
		self.admisActionFlag = False
		self.startEffect = None
		self.loopEffect = None
		self.adminEffect = None
		self.endEffect = None
		
		self.uiAttachsShow = True
		
		self.lastPos = Math.Vector3( 0, 0, 0 )
		self.isLoadModel = False       #�Ƿ����ڸı�ģ����
		self.delayActionNames = []   #�ı�ģ���зż��ܵ�ʩ������
		self.delayCastEffects = []     #�ı�ģ���м��ܵ�ʩ����Ч
		self.hipModels = []
		self.panModels = []
		self.pitchModelcbid = 0
		self.rotateTimerID = 0

		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]
	# ----------------------------------------------------------------
	# This method is called when the entity enters the world
	# Any of our properties may have changed underneath us,
	#  so we do most of the entity setup here
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld:
			return
		NPCObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )

		# original model Boundbox be replaced with user skeletonCollider
		#baAttachNode = self.model.node("hips")
		#if( baAttachNode ):
		#	ba = BigWorld.BoxAttachment()
		#	ba.name = "hips"
		#	ba.minBounds = -0.5*self.model.scale
		#	ba.maxBounds = 0.5*self.model.scale
		#	baAttachNode.attach(ba)
		#	self.skeletonCollider.addCollider(ba)

		# ���õ�ǰ״̬
		self.set_state()
		self.queryBootyOwner()
		#���������������ٻ��Ĺ����Ƿ�����
		if not self.isshowModel():
			self.setModelVisible( Define.MODEL_VISIBLE_TYPE_FALSE )

	def leaveWorld( self ) :
		"""
		�뿪����
		"""

		NPCObject.leaveWorld( self )
		CombatUnit.leaveWorld( self )
		self.am=None
		for linkEffect in self.linkEffect:
			linkEffect.stop()
		self.linkEffect = []
		if self.model is not None:
			self.model.OnActionStart = None
		self.model = None

	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		paths = NPCObject.prerequisites( self )
		paths.extend( rds.itemModel.getMSource( self.lefthandNumber ) )
		paths.extend( rds.itemModel.getMSource( self.righthandNumber ) )
		for i in paths[:]:
			if csol.isFileAtLocal(i) <= 0:
				paths.remove(i)
		vModelIDs = rds.npcModel.getVehicleModelIDs( self.modelNumber )
		for modelID in vModelIDs:
			paths.extend( rds.npcModel.getModelSources( modelID ) )
		return paths

	# ----------------------------------------------------------------
	# ģ�����
	# ----------------------------------------------------------------
	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		NPCObject.onModelChange( self, oldModel, newModel )
		CombatUnit.onModelChange( self, oldModel, newModel )
		if newModel is None: return

		am = self.am
		if am.owner != None: am.owner.delMotor( am )
		newModel.motors = ( am, )

		# ��̬ģ�͵ķŴ�������� action match ֮����������ᱻ��ԭ
		newModel.scale = ( self.modelScale, self.modelScale, self.modelScale )

		# ����������ģ��
		self.set_lefthandNumber()
		self.set_righthandNumber()

		# ��ȡ��ģ�͵��漴����
		self.getRandomActions()

		rds.areaEffectMgr.onModelChange( self )

	def fadeInModel( self ):
		"""
		����ģ��
		"""
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		if self.hasFlag( csdefine.ENTITY_FLAG_CLOSE_FADE_MODEL ): return
		alpha = rds.npcModel.getModelAlpha( self.modelNumber )
		if alpha != 1:
			rds.effectMgr.setModelAlpha( self.model, alpha, 1.0 )
		else:
			rds.effectMgr.fadeInModel( self.model )

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		# Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# ģ�͵�RolePitchYaw��Entity����һ��
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			# ģ�͵�����������
			self.am.boredNotifier = self.onBored
			self.am.patience = random.random() * 6 + 6.0
			self.am.fuse = random.random() * 6 + 6.0
			self.setArmCaps()
		# ΢��ģ��Ԥ���ش���
		modelSourceList = rds.npcModel.getModelSources( self.modelNumber )
		if modelSourceList:
			modelSource = modelSourceList[0]
		if len( modelSourceList ) == 1 and "avatar" not in modelSource :
			g_mlMgr.getSource( modelSource, self.id )
		self.isLoadModel = True
		self.delayActionNames = []   #�ı�ģ���зż��ܵ�ʩ������
		self.delayCastEffects = []     #�ı�ģ���м��ܵ�ʩ����Ч
		if self.model is not None:
			self.model.OnActionStart = None
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.onModelLoad, event ) )
	
	def onModelLoad( self, event, model ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		self.setModel( model, event )
		self.updateVisibility()
		# ��ֹ�д��������Ĺ������ģ�ͺ�ͷ�������޷���ʾ
		self.showNameUI()
		self.flushAttachments_()
		self.isLoadModel = False
		if self.firstHide:
			self.playStandbyAction()
		if self.delayActionNames:
			rds.actionMgr.playActions( self.getModel(), self.delayActionNames )
		for cb in self.delayCastEffects:
			if callable( cb ):
				cb()
		self.getSubModel()
		self.onActionStart( "stand" )
		if self.model is not None:
			self.model.OnActionStart = self.onActionStart

	def getSubModel( self ):
		"""
		����SubModel�����������NPC
		"""
		for index in xrange( 1, 11 ):
			if index < 10: hipKey = "hip_0%s" % index
			else: hipKey = "hip_%s" % index
			if not hasattr( self.model, hipKey ): continue
			model = getattr( self.model, hipKey )
			if model is None: continue
			self.hipModels.append( model )

		for index in xrange( 1, 11 ):
			if index < 10: panKey = "pan_0%s" % index
			else: panKey = "pan_%s" % index
			if not hasattr( self.model, panKey ): continue
			model = getattr( self.model, panKey )
			if model is None: continue
			self.panModels.append( model )
		
	def getUSelectSize( self ):
		"""
		��ȡѡ���Ȧ��С
		���ô�С�����ű�������
		"""
		uSelectSize = rds.npcModel.getUSelectSize( self.modelNumber )
		if uSelectSize != -1.0:
			uSelectSize *= self.modelScale
		return uSelectSize

	def onActionStart( self, actionName ):
		"""
		������������
		���������ģ�͵Ĵ���
		"""
		if actionName not in ACTION_MAPS: return
		if not self.inWorld: return
		for model in self.hipModels:
			rds.actionMgr.playAction( model, ACTION_MAPS[actionName][0] )
		for model in self.panModels:
			rds.actionMgr.playAction( model, ACTION_MAPS[actionName][1] )

	def resetWeaponType( self ):
		"""
		������������
		"""
		lefthandNum = self.lefthandNumber
		righthandNum = self.righthandNumber
		try:
			lNum = int( str( lefthandNum )[-6:-4] )
		except:
			lNum = Define.PRE_EQUIP_NULL
		try:
			rNum = int( str( righthandNum )[-6:-4] )
		except:
			rNum = Define.PRE_EQUIP_NULL
		# �������Ϊ�ջ���Ϊ���ƣ������entity�������������ж�
		if lNum == Define.PRE_EQUIP_NULL or lNum == Define.PRE_EQUIP_SHIELD:
			try:
				type = Define.WEAPON_TYPE_MODEL_MAP[ rNum ]
			except:
				ERROR_MSG( "Can't find WeaponType Define by(%s)" % rNum )
				type = Define.WEAPON_TYPE_NONE

		else:

			if lNum == Define.PRE_EQUIP_BOW:
				type = Define.WEAPON_TYPE_BOW
			elif rNum == Define.PRE_EQUIP_NULL:
				type = Define.WEAPON_TYPE_NONE
			else:
				type = Define.WEAPON_TYPE_DOUBLEHAND
		self.weaponType = type

	def resetArmorType( self ):
		"""
		���÷�������
		���ݲ߻����������ж�entity�����Ƿ�װ������
		���ж��Ƿ����ؼף����������ְҵ��Ӧ��������·��
		���û�����߲߻��Զ����������·��
		"""
		lefthandNum = self.lefthandNumber
		try:
			lNum = int( str( lefthandNum )[-6:-4] )
		except:
			lNum = Define.PRE_EQUIP_NULL
		if lNum == Define.PRE_EQUIP_SHIELD:
			type = Define.ARMOR_TYPE_SHIELD
		else:
			type = rds.spellEffect.getArmorTypeByNum( self.modelNumber )
		self.armorType = type

	def getWeaponType( self ):
		"""
		��ȡ��������
		"""
		return self.weaponType

	def getArmorType( self ):
		"""
		��ȡ��������
		"""
		return self.armorType

	def onSetLeftHandNumber( self, number ):
		"""
		define method.
		��������ģ��
		"""
		tnumber = self.lefthandNumber
		self.lefthandNumber = number
		self.set_lefthandNumber( tnumber )

	def onSetRightHandNumber( self, number ):
		"""
		define method.
		��������ģ��
		"""
		tnumber = self.righthandNumber
		self.righthandNumber = number
		self.set_righthandNumber( tnumber )

	def set_lefthandNumber( self, oldLefthandNumber = 0 ):
		"""
		����װ��ģ��
		"""
		if self.model is None: return
		if self.lefthandNumber == oldLefthandNumber: return

		# ����������������
		self.resetWeaponType()
		self.resetArmorType()

		rds.itemModel.createModelBG( self.lefthandNumber, Functor( self._onLefthandModel, self.lefthandNumber,oldLefthandNumber ) )

	def _onLefthandModel( self, itemModelID, oldLefthandNumber, model ):
		"""
		��������ģ�ͼ��ػص������ع�Ч
		"""
		if self.model is None: return
		lefthandModel = model
		oldType = ( oldLefthandNumber / 10000 ) % 100
		newType = ( self.lefthandNumber / 10000 ) % 100
		if oldType == Define.PRE_EQUIP_SHIELD or newType == Define.PRE_EQUIP_SHIELD:
			equipPart = "left_shield"
		else:
			equipPart = "left_hand"

		if hasattr( self.model, equipPart ):
			if lefthandModel and not hasattr( lefthandModel, equipPart ):
				ERROR_MSG( "Can't find node(HP_%s) in (%s)" % ( equipPart, lefthandModel.sources ) )
			else:
				setattr( self.model, equipPart, lefthandModel )
		else:
			ERROR_MSG( "Can't find node(HP_%s) in (%s)" % ( equipPart, self.model.sources ) )

		# ��Ч
		effectIDs = rds.itemModel.getMEffects( itemModelID )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, self.getParticleType(), self.getParticleType() )
			effect.start()

	def set_righthandNumber( self, oldRighthandNumber = 0 ):
		"""
		����װ��ģ��
		"""
		if self.model is None: return
		if self.righthandNumber == oldRighthandNumber: return

		# ������������
		self.resetWeaponType()
		rds.itemModel.createModelBG( self.righthandNumber, Functor( self._onRighthandModel, self.righthandNumber ) )

	def _onRighthandModel( self, itemModelID, model ):
		"""
		��������ģ�ͼ��ػص������ع�Ч
		"""
		if self.model is None: return
		righthandModel = model
		if hasattr( self.model, "right_hand" ):
			if righthandModel and not hasattr( righthandModel, "right_hand" ):
				ERROR_MSG( "Can't find node(HP_right_hand) in (%s)" % ( righthandModel.sources ) )
			else:
				setattr( self.model, "right_hand", righthandModel )
		else:
			ERROR_MSG( "Can't find node(HP_right_hand) in (%s)" % ( self.model.sources ) )

		# ��Ч
		effectIDs = rds.itemModel.getMEffects( itemModelID )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, self.getParticleType(), self.getParticleType() )
			effect.start()


	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		��ȡ���������������������������̶���
		��ȡ���������random1��ʼ��random2,random3....��ȡʧ���򷵻�
		"""
		#the range(1,10) is  provisional, because I can't find more than 2 randomActions for a entity
		for index in range(1,10):
			actName = "random"+str( index )
			if self.model.hasAction( actName ):
				self.randomActions.append( actName )
			else:
				return

	def onBored( self, actionName ):
		"""
		�˻ص����ڲ����������
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""

		if actionName != "stand": return
		self.playRandomAction()
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
		#��ȡ�������������
		randomActionCount = len( self.randomActions )
		if randomActionCount == 0:
			return
		else:
			matchCaps = [ Define.CAPS_RANDOM ]
			if self.righthandNumber or self.lefthandNumber:
				matchCaps.append(  Define.CAPS_WEAPON )
			else:
				matchCaps.append( Define.CAPS_NOWEAPON )
			if randomActionCount == 1:
				matchCaps.append( Define.CAPS_INDEX25 )
			else:
				index = random.randint( 0, randomActionCount - 1 )
				caps = Define.CAPS_INDEX25 + index
				matchCaps.append( caps )
			self.am.matchCaps = matchCaps

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
		# ֻ������������Ĺ���
		if Define.CAPS_RANDOM in self.am.matchCaps:
			self.setArmCaps()

	def onTargetFocus( self ):
		"""
		Ŀ�꽹���¼�
		"""
		if self.hasFlag(csdefine.ENTITY_FLAG_CAN_NOT_SELECTED):	#����ѡ��
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_CATCH ) and self.takeLevel == -1:
			self.canShowDescript = True
			self.cell.requestTakeLevel()
		else:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		NPCObject.onTargetFocus( self )
		if rds.ruisMgr.isMouseHitScreen():
			self.handleMouseShape()

	def handleMouseShape( self ):
		"""
		������궯��
		"""
		
		# ����״̬���޹���ͼ��
		player = BigWorld.player()
		if player.hasFlag( csdefine.ROLE_FLAG_FLY ): # ����״̬�µĲ���ʾ�ɹ�����ͼ��
			rds.ccursor.set( "normal" )
			return

		# ������Լ��ĳ�ս�������ʾ����ͼ�� by mushuang
		player = BigWorld.player()
		pet = player.pcg_getActPet()
		if pet and pet.id == self.id:
			rds.ccursor.set( "normal" )
			return

		if self.flags != 0:
			if self.hasFlag(csdefine.ENTITY_FLAG_SPEAKER):		# ���ԶԻ���
				rds.ccursor.set( "dialog" )
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_REPAIRER):	#����
				if self.isInteractionRange( BigWorld.player()):	#��������NPC�Ľӿ� �жϵ�ǰ�Ƿ��ܺ͸�NPCֱ�ӽ���  modified by hd(2008,9,16)
					rds.ccursor.set( "repair" )
				else:
					rds.ccursor.set( "repair" ,True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_BANK_CLERK):	#���а���Ա
				if self.isInteractionRange( BigWorld.player()):	#��������NPC�Ľӿ� �жϵ�ǰ�Ƿ��ܺ͸�NPCֱ�ӽ���  modified by hd(2008,9,16)
					rds.ccursor.set( "storage" )
				else:
					rds.ccursor.set( "storage" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_EQUIP_MAKER):#װ������
				if self.isInteractionRange( BigWorld.player()):	#��������NPC�Ľӿ� �жϵ�ǰ�Ƿ��ܺ͸�NPCֱ�ӽ���  modified by hd(2008,9,16)
					rds.ccursor.set( "calcine" )
				else:
					rds.ccursor.set( "calcine" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_SKILL_TRAINER):	#����ѵ��ʦ
				if self.isInteractionRange( BigWorld.player()):	#��������NPC�Ľӿ� �жϵ�ǰ�Ƿ��ܺ͸�NPCֱ�ӽ���  modified by hd(2008,9,16)
					rds.ccursor.set( "skill" )
				else:
					rds.ccursor.set( "skill" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_PET_CARE):	#���ﱣ��
				if self.isInteractionRange( BigWorld.player()):	#��������NPC�Ľӿ� �жϵ�ǰ�Ƿ��ܺ͸�NPCֱ�ӽ���  modified by hd(2008,9,16)
					rds.ccursor.set( "petFoster" )
				else:
					rds.ccursor.set( "petFoster" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_POSTMAN):	#�ʲ�
				if self.isInteractionRange( BigWorld.player()):	#��������NPC�Ľӿ� �жϵ�ǰ�Ƿ��ܺ͸�NPCֱ�ӽ���  modified by hd(2008,9,16)
					rds.ccursor.set( "mail" )
				else:
					rds.ccursor.set( "mail" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_CHAPMAN):	#����
				if self.isInteractionRange( BigWorld.player()):	#�����ֻ�������˵Ĺ�����ô��ʾ���� ���
					rds.ccursor.set( "trade" )
				else:
					rds.ccursor.set( "trade" , True)
				return



		if BigWorld.player().queryRelation( self ) == csdefine.RELATION_ANTAGONIZE :
			rds.ccursor.set( "attack" )
			return

		#������߱���������,��ô��ʾ����ͼ��
		rds.ccursor.set( "normal" )		# modified by hyw( 2008.08.29 )


	# Quitting as target
	def onTargetBlur( self ):
		"""
		�뿪Ŀ���¼�
		"""
		self.canShowDescript = False
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		NPCObject.onTargetBlur( self )
		if rds.ccursor.shape == "hand" or \
			rds.ccursor.shape == "attack" :		# modified by hyw( 2008.08.29 )
				rds.ccursor.set( "normal" )

	def receiveTakeLevel( self, takeLevel ):
		"""
		Define method.
		����Я���ȼ�

		@param takeLevel : Я���ȼ�
		@type takeLevel : UINT16
		"""
		self.takeLevel = takeLevel
		if self.canShowDescript:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )

	def getTakeLevel( self ):
		"""
		"""
		return  self.takeLevel

	def onTargetClick( self, player ):
		"""
		Ŀ�����¼�
		@type	player	:	instance
		@param	player	:	���ʵ��
		@rtype			:	int
		@return			:	TARGET_CLICK_FAIL ���ʧ��, TARGET_CLICK_SUCC ����ɹ�,TARGET_CLICK_MOVE ����ƶ�
		"""
		NPCObject.onTargetClick( self, player )

	def onReviviscence( self ):
		"""
		�����¼�
		"""
		rds.effectMgr.createParticleBG( self.getModel(), "HP_root", "particles/fuhuo/fuhuo.xml", detachTime = 3.0, type = Define.TYPE_PARTICLE_NPC )

	def onStateChanged( self, old, new ):
		"""
		virtual method.
		״̬�л���

		@param old	:	������ǰ��״̬
		@type old	:	integer
		@param new	:	�����Ժ��״̬
		@type new	:	integer
		"""
		CombatUnit.onStateChanged( self, old, new )
		if old == csdefine.ENTITY_STATE_HANG:
			self.setVisibility( True )
		if new == csdefine.ENTITY_STATE_HANG:
			self.setVisibility( False )
		return


	def set_state( self, oldState = None ):
		CombatUnit.set_state( self, oldState )
		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.onDieSound()	# ����������Ч jy
			self.onDie()
			for linkEffect in self.linkEffect:
				linkEffect.stop()
			self.linkEffect = []
		elif self.state == csdefine.ENTITY_STATE_FIGHT:
			print "%s %d fight." % (self.getName(), self.id)
			self.onFightSound()	# �������ս����Ч jy
			if self.hasFlag( csdefine.ENTITY_FLAG_ONLY_FACE_LEFT_OR_RIGHT ):
				self.am.turnModelToEntity = False
				self.startFaceTimer()
			ECenter.fireEvent( "EVT_ON_MONSTER_FIGHT_STATE_CHANGE", self )
		else:
			if self.hasFlag( csdefine.ENTITY_FLAG_ONLY_FACE_LEFT_OR_RIGHT ):
				self.stopFaceTimer()
			ECenter.fireEvent( "EVT_ON_NPC_QUEST_STATE_CHANGED", self, self.questStates )
		self.setArmCaps()

	def onDie( self ):
		"""
		"""
		print "%s %d dead." % (self.getName(), self.id)
		if not self.isBlastFlag: #�����ϲ�������Ч����add by wuxo 2011-11-18
			BigWorld.callback( 0.5, self.playDieEvent ) #�ӳٻص���Ϊ�������ظ�˳��
		self.setSelectable( False )
		rds.targetMgr.unbindTarget( self )	#��������ʱ��ʧĿ��modify by wuxo

	def playDieEvent(self):
		"""
		��AOI��Χ�����е���ҿͻ��˲���������ͷ�¼�
		"""
		if not self.inWorld : return
		actionNameL =  [ Const.MODEL_ACTION_DIE,Const.MODEL_ACTION_DEAD ]
		eventID = 0

		actionAndevent = rds.npcModel.getDieEvent( self.modelNumber )
		if actionAndevent != "" :
			ae = actionAndevent.split(";")
			if len( ae ) > 0:
				actionNameL =  [ ae[0], Const.MODEL_ACTION_DEAD ]
			if len( ae ) > 1:
				eventID = int( ae[1] )
		if eventID != 0:
			rds.cameraEventMgr.trigger( eventID )
		rds.actionMgr.playActions( self.getModel(), actionNameL, callbacks = [ self.onFinishDieAction ] )

	# ----------------------------------------------------------------
	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡĿ����Լ��Ĺ�ϵ

			��ɫ���Լ�--�Ѻ�
			��ɫ�����--�Ѻ�
			��ɫ���ɫ--�Ѻã��ݲ�����PKϵͳ��
			��ɫ��NPC--�Ѻ�
			��ɫ���������������--����
			��ɫ��������������--�ж�
			NPC��NPC����������֮�䣩--����

		@param entity: Ŀ�����
		@param entity: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		return : ��ϵ C_RELATION_FRIEND | C_RELATION_NEUTRALLY | C_RELATION_ANTAGONIZE
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			entity = entity.getRelationEntity()
			if entity:
				return self.queryCombatRelation( entity )
			else:
				return csdefine.RELATION_FRIEND
				
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			player = BigWorld.player()
			if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				pid = self.ownerVisibleInfos[ 0 ]
				tid = self.ownerVisibleInfos[ 1 ]
				if pid == player.id or tid == player.teamID:
					return csdefine.RELATION_ANTAGONIZE
				else:
					return csdefine.RELATION_NOFIGHT

		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		return csdefine.RELATION_NEUTRALLY

	def onFinishDieAction( self ):
		BigWorld.callback( random.uniform( 1.0, 4.0), self.hideEntitymodel )

	def hideEntitymodel( self ):
		if not self.inWorld: return
		if self.hasFlag( csdefine.ENTITY_FLAG_CLOSE_FADE_MODEL ): return
		rds.effectMgr.fadeOutModel( self.getModel(),0.5 )

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_FLY ):
			return  BigWorld.AvatarFilter()
		else:
			return BigWorld.AvatarDropFilter()

	def hideModelNow(self):
		"""
		ֱ������ģ�ͣ����ӳ٣��޵��뵭��
		"""
		model = self.getModel()
		if model:
			model.visible = False

	def showSkillName( self, skillID ):
		"""
		��ʾ��������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.id, skillID )	 # ��ʾ�ͷż��ܵ�����
		
	def playBlastEffect( self, effect ):	
		self.isBlastFlag = True #д�������ԭ����Ϊ���ݴ�  ��ʹ�ù�������������Ч��  ��������Ч��������/���� ����Ϊ������Ч��û��
		BigWorld.callback( 0.3, self.hideModelNow )
		self.hideNameUI()
		effect.start()

	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		�˺���ʾ
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skill : ����
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		CombatUnit.onReceiveDamage( self, casterID, skill, damageType, damage )
		#�����˺��жϺͼ���ID�ж� �Ƿ񲥷ű�ʬЧ��add by wuxo 2011-11-17
		sk = skill
		skillid = None
		try:
			skillid = int(str(sk.getID())[:6])
		except:
			skillid = sk.getID()
		if self.HP <= damage:	#��������
			if  skillid not in MONSTERBLASTDATAS[1]:	#���ܷ�������
				#�����Ƿ񲥷�����Ч�� add by wuxo 2011-11-17
				if self.className not in MONSTERBLASTDATAS[0]:
					model = self.getModel()
					if model:
						infos = rds.npcModel._datas[self.modelNumber]
						effectID = infos.get( "blast_effect", "" ) #Ч���ɵ���������Ч����Ϊ��Чmodify by wuxo 2011-12-22
						type = self.getParticleType()
						effect = rds.skillEffect.createEffectByID( effectID, model, model, type, type )
						if effect :
							if self.__class__.__name__ in ["YXLMBoss", "MiniMonster_Lol"]:
								BigWorld.callback( 0.5, Functor( self.playBlastEffect, effect ) )
							else:
								self.playBlastEffect( effect )
		player = BigWorld.player()
		petID = -1
		pet = player.pcg_getActPet()
		if pet:
			petID = pet.id
		if casterID != player.id and casterID != petID :
			return
		self.onDamageSound()	# �ܹ�����Ч jy
		if damage > 0:
			if self.className in [item["bossID"] for item in bossGetHitDatas]:	
				if skillid in [item["skillID"] for item in skillCauseDatas]:					#����ʹģ�͸����ļ���
					rds.effectMgr.setModelColor(self.model, (2.5,2.5,2.5,2.5), (1.0,1.0,1.0,1.0), 0.5)
				self.model.pitch = -0.5
				self.pitchModelcbid = BigWorld.callback( 0.3, self.disPitchModel )
			if ( damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
				# �����˺�
				ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
				if self.className in [item["bossID"] for item in bossGetHitDatas]:
					rds.effectMgr.setModelColor(self.model, (2.5,2.5,2.5,2.5), (1.0,1.0,1.0,1.0), 0.5)
			else:
				# ��ͨ�˺�
				ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
		else:
			# Miss
			ECenter.fireEvent( "EVT_ON_SHOW_MISS_ATTACK", self.id )

		# ���ܲ����˺�ʱ��ϵͳ��Ϣ�ȴ���
		if casterID == player.id:					# �Լ���ʩ����
			if damage > 0:
				if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s�м������%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM_SKILL, self.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# ���%s������%s���%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_TO, sk.getName(), self.getName(), damage )
				else:
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# %s�ܵ��㷴����%i�㷨���˺���
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, self.getName(), damage )
						else:
							# %s�ܵ��㷴����%i���˺���
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY_TO, self.getName(), damage )
					else:
						# ���%s��%s�����%i���˺���
						player.statusMessage( csstatus.SKILL_SPELL_DAMAGE_TO, sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s���������%s��
					player.statusMessage( csstatus.SKILL_SPELL_DODGE_FROM_SKILL, self.getName(), sk.getName() )
		elif casterID == petID: 					# ������ʩ����
			if damage > 0:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s�м�����ĳ����%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL, self.getName(), pet.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# �����%s������%s���%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_TO, pet.getName(), sk.getName(), self.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
					if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:

						# ����Ч���������Ե������%i�㷨���˺���
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_MAGIC_TO, damage )
					else:

						# ����Ч���������Ե������%i���˺���
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_PHY_TO, damage )
				else:
						# �����%s��%s�����%i���˺���
						player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_TO, pet.getName(), sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s�����˳����%s��
					player.statusMessage( csstatus.SKILL_SPELL_PET_DODGE_TO, self.getName(), pet.getName(), sk.getName() )
	
	def disPitchModel( self ):
		"""
		"""
		if self.pitchModelcbid > 0:
			BigWorld.cancelCallback( self.pitchModelcbid )
			self.pitchModelcbid = 0
		self.model.pitch = 0.0

	def getVisibility( self ) :
		"""
		��Щʵ������ʹ��self.models����Ϊ���֣����ʱ��visible�Ĵ����Ӧ�����models
		"""
		model = self.getModel()
		if model:
			return model.visible
		return False

	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		NPCObject.initCacheTasks( self )
		CombatUnit.initCacheTasks( self )
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_MONSTER0 )

# ------------------------------------------------------------------------------
# ������Ч by����
# ------------------------------------------------------------------------------
	def playSound( self, soundName ):
		"""
		���Ź�������
		@param entity	:	�������ŵ�λ��
		@type entity	:	entity
		@param soundName:	�����ļ���Ӧ���ֶ���
		@type soundName	:	string
		"""
		# rds.spellEffect.getNormalCastSound( weaponType )
		model = self.getModel()
		if model is None: return
		soundMgr.playVocality( soundName, model )

	def onFightSound( self ):
		"""
		�������ս����Ч
		"""
		if not self.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnFightSound( self.modelNumber )	# ��ȡ�������ս����Ч
		if len( soundNames ) <= 0 :
			print "get monster FightSound null"
			return
		soundName = random.choice( soundNames )
		self.playSound( soundName )	# ���Ź������ս����Ч

	def onDieSound( self ):
		"""
		����������Ч
		"""
		if not self.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnDieSound( self.modelNumber )	# ��ȡ����������Ч
		if len( soundNames ) <= 0 :
			print "get monster DieSound null"
			return
		soundName = random.choice( soundNames )
		self.playSound( soundName )	# ���Ź���������Ч

	def onDamageSound( self ):
		"""
		�����ܹ�����Ч
		"""
		if not self.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnDamageSound( self.modelNumber )	# ��ȡ�����ܹ�����Ч
		if len( soundNames ) <= 0 :
			print "get monster DamageSound null"
			return
		soundName = random.choice( soundNames )
		self.playSound( soundName )	# ���Ź����ܹ�����Ч

	def queryBootyOwner( self ) :
		"""
		�����������������Ȩ��Ϣ
		"""
		if self.state == csdefine.ENTITY_STATE_FIGHT :
			self.cell.queryBootyOwner()

	def onSetBootyOwner( self, bootyOwner ) :
		"""
		defined method
		@param	bootyOwner		: ����Ȩ��Ϣ
		@type	bootyOwner		: tuple of OBJECT_ID: ( ownerID, teamID )
		"""
		self.bootyOwner = bootyOwner
		player = BigWorld.player()
		if player.targetEntity and player.targetEntity.id == self.id :			# �����ҵ�ǰĿ����Ǹù���
			if ( bootyOwner[1] == player.teamID and bootyOwner[1] != 0 ) or \
			bootyOwner[0] in player.teamMember or bootyOwner[0] == player.id \
			or bootyOwner == ( 0, 0 ) :
				ECenter.fireEvent( "EVT_ON_SET_TARGET_BOOTY_OWNER", True )
			else :
				ECenter.fireEvent( "EVT_ON_SET_TARGET_BOOTY_OWNER", False )


	def onSetAsTarget( self ):
		"""
		define method
		"""
		rds.targetMgr.bindTarget( self )

	#----------------------------------------------------------------

	def outputCallback1( self, moveDir, needTime,a, dTime ):
		"""
		filter��λ��ˢ�»ص�����
		ģ���������ٶȣ��������ߵķ�ʽ�˶�
		"""
		yMoveDir =  Math.Vector3(0,1.0,0)
		self.moveTime += dTime
		if self.moveTime >= needTime:
			BigWorld.callback( 0.01, self._onMoveOver )
			return self.position
		else:
			return self.position + moveDir * dTime - yMoveDir * self.dertaHight( self.moveTime, dTime, a )

	def dertaHight( self, t1, t, a = 9.8 ):
		"""
		�߶Ȳh��a:���ٶ�Ĭ��Ϊ9.8��t1:����ʱ��,t:ʱ���
		"""
		return ( t1 - 0.5 * t ) * a * t

	def throwToPoint( self, position, speed ):
		"""
		�����ٶȵ��������˶��������
		"""
		yawDir = position - self.position
		xYawDir = Math.Vector3(yawDir[0],0,yawDir[2])
		xYawDir.normalise()
		xMoveDir = xYawDir * speed
		distance = self.position.flatDistTo( position )
		needTime = distance / speed
		a = 2 * abs(yawDir[1]) / ( needTime * needTime )
		func = Functor( self.outputCallback1, xMoveDir, needTime, a )
		self.moveTime = 0.0
		if not hasattr(self.filter,"outputCallback"):
			self.filter = BigWorld.AvatarDropFilter()
		self.filter.outputCallback = func

	def actionToPoint( self, position, speed ):
		"""
		���������
		"""
		rds.actionMgr.stopAction( self.model, rds.npcModel.getStandbyAction( self.modelNumber ) )
		vPosition = Math.Vector3( self.position - position )
		vPosition[1] = 0          # ֻ����XOZƽ����ƶ�
		self.throwToPoint( position, speed )
		time = vPosition.length/speed
		self.playAction( time-0.2 )

	def playAction( self,time2 ):
		"""
		����
		"""
		# 1 �ǳ�ʼ��2������������Ԥ��ʱ����ɣ�3��������������Ԥ��ʱ�����
		actionNames = rds.npcModel.getPreAction( self.modelNumber )
		preEffectIDs = rds.npcModel.getPreEffect( self.modelNumber )
		self.startOver = 1
		# ����д Ϊ��ʹ�������볡������start�����ܲ������
		def onStartActionCompleted():
			if self.startEffect:
				self.startEffect.stop()
			if self.startOver == 1:
				self.startOver = 2
				self.loopEffect = self.playEffect( preEffectIDs[1] )
			if self.startOver == 3:
				def stopEndEffect():
					if self.endEffect:
						self.endEffect.stop()
				rds.actionMgr.playAction( self.model, actionNames[2], 0, stopEndEffect )
				def shake():
					rds.worldCamHandler.cameraShell.camera_.shake(0.3,(0.1,0.2,0.1))
				BigWorld.callback( 0.2, shake )
				if self.loopEffect:
					self.loopEffect.stop()
				self.endEffect = self.playEffect( preEffectIDs[2] )  # ���Ž�����Ч

		def onEndActionStart():
			if self.startOver == 1:
				self.startOver = 3
			if self.startOver == 2:
				def stopEndEffect():
					if self.endEffect:
						self.endEffect.stop()
				rds.actionMgr.playAction( self.model, actionNames[2], 0 ,stopEndEffect )
				def shake():
					rds.worldCamHandler.cameraShell.camera_.shake(0.3,(0.1,0.2,0.1))
				BigWorld.callback( 0.2, shake )
				if self.startEffect:
					self.startEffect.stop()
				if self.loopEffect:
					self.loopEffect.stop()
				self.endEffect = self.playEffect( preEffectIDs[2] )

		rds.actionMgr.playActions( self.model, [actionNames[0],actionNames[1]], 0, [onStartActionCompleted,None])
		if preEffectIDs:
			self.startEffect = self.playEffect( preEffectIDs[0] )   # ����start��Ч
		BigWorld.callback( time2, onEndActionStart )

	def playEffect( self, effectID ):
		"""
		���Ź�Ч,�����ز��ŵĹ�Ч
		"""
		effect = rds.skillEffect.createEffectByID( effectID, self.model, self.model, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if effect:
			effect.start()
			return effect

	def playAdmissionAction( self ):
		"""
		������λ�Ƶ��볡����,ֹͣ���Ŵ�����Ч����ʼ�����볡��Ч
		"""
		rds.actionMgr.stopAction( self.model, rds.npcModel.getStandbyAction( self.modelNumber ) )   # ��ֹ�볡����
		if not self.admisActionFlag :
			self.admisActionFlag = True
			self.am.turnModelToEntity = False
			def callback():
				self.am.turnModelToEntity = True
				if self.adminEffect:
					self.adminEffect.stop()
				self.showNameUI( )
			preAction = rds.npcModel.getPreAction( self.modelNumber )
			self.adminEffect = self.playAdmissionEffect()
			rds.actionMgr.playAction( self.model, preAction,0,callback )


	def playAdmissionEffect( self ):
		"""
		ֹͣ������Ч����ʼ�����볡��Ч
		"""
		if self.standbyEffect:
			self.standbyEffect.stop()
		preEffectID = rds.npcModel.getPreEffect( self.modelNumber )
		admissionEffect = rds.skillEffect.createEffectByID( preEffectID, self.model, self.model, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if admissionEffect:
			admissionEffect.start()
			return admissionEffect

	def playStandbyAction( self ):
		"""
		���Ŵ�������,���������Ź�Ч
		"""
		standbyAction = rds.npcModel.getStandbyAction( self.modelNumber )
		standbyEffectID = rds.npcModel.getStandbyEffect( self.modelNumber )
		if not ( standbyAction or standbyEffectID ):return
		self.hideNameUI( )
		self.model.visible = False      # Ϊ�˷�ֹ����һ���ӵ��ϵ����������Ĺ���
		if standbyAction :
			rds.actionMgr.playAction( self.model, standbyAction )
		self.standbyEffect = rds.skillEffect.createEffectByID( standbyEffectID, self.model, self.model, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if self.standbyEffect:
			self.standbyEffect.start()
		def callback():
			if self.model:
				self.updateVisibility()
		BigWorld.callback( 0.5, callback )
	
	def hideNameUI( self ):
		"""
		����ͷ�����UI
		"""
		self.uiAttachsShow = False
		model = self.getModel()
		try:
			node = model.node("HP_title")
		except:
			node = None
		if not node : return
		for ui in node.attachments:
			ui.component.visible = False #��������Ѫ��UI
		
	def showNameUI( self ):
		"""
		��ʾͷ�����UI
		"""
		self.uiAttachsShow = True
		self.notifyAttachments_( "onEnterWorld" )

	def onPlayActionOver( self, actionNames ):
		"""
		����������ɻص�
		"""
		CombatUnit.onPlayActionOver( self, actionNames )
		if len( actionNames ) == 0: return
		if self.rotateTarget and self.rotateAction == actionNames[0]:
			self.rotateToTarget( self.rotateTarget )
			self.rotateTarget = None
			self.rotateAction = ""

	# ------------------------------------------------------------------------------
	# ��渱������
	# ------------------------------------------------------------------------------
	def getFaceYaw( self ):
		"""
		get the face yaw
		"""
		target = BigWorld.entities.get( self.targetID )
		if target is None: return Const.ENTITY_FACE_LEFT_YAW

		yaw = ( target.position - self.position ).yaw

		if math.fabs( yaw - Const.ENTITY_FACE_LEFT_YAW ) <= math.pi/2.0:
			return Const.ENTITY_FACE_LEFT_YAW
		return Const.ENTITY_FACE_RIGHT_YAW

	def startFaceTimer( self ):
		"""
		start the face to Timer
		"""
		return
		if not self.inWorld: return

		self.model.yaw = self.getFaceYaw()
		#self.filter.setYaw( self.getFaceYaw() )
		self.faceTimerID = BigWorld.callback( Const.ENTITY_FACE_TO_TIME, self.startFaceTimer )

	def stopFaceTimer( self ):
		"""
		stop the face to Timer
		"""
		return
		if self.faceTimerID == 0: return
		BigWorld.cancelCallback( self.faceTimerID )
		self.am.turnModelToEntity = True
		self.faceTimerID = 0
	
	def jumpBackFC( self ):
		"""
		Define Method
		������֪ͨ�����
		"""
		model = self.model
		if model:
			if model.hasAction( Const.MODEL_ACTION_MAGIC_CAST ):
				rds.actionMgr.playAction( model, Const.MODEL_ACTION_MAGIC_CAST )

	def set_flags( self, oldFlag ):
		"""
		Monster��flags��Ǳ�����ʱ����
		"""
		NPCObject.set_flags( self, oldFlag )
		self.setArmCaps()

	def setArmCaps( self ):
		"""
		����ƥ��caps
		"""
		if not self.inWorld: return
		armCaps = []
		if self.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_LIE_DOWN ):
			armCaps.append( Define.CAPS_LIE_DOWN )      # ����ͨ״̬��ƥ�����¶���,�����������ʵ����dead������ʵ��
		if self.hasFlag( csdefine.ENTITY_FLAG_RAD_FOLLOW_ACTION ) and self.state == csdefine.ENTITY_STATE_FIGHT:
			armCaps.append( Define.CAPS_RADIFOLLOW )	# �����ε���־λ��������ս��״̬�²Ż�ƥ���ε�Caps
		if self.findBuffByBuffID( Const.VERTIGO_BUFF_ID1 ) or self.findBuffByBuffID( Const.VERTIGO_BUFF_ID2 ): # ѣ��buff����
			armCaps.append( Define.CAPS_VERTIGO )

		stateCaps = Define.MONSTER_CAPS.get( self.state, 0 )
		self.am.matchCaps = [stateCaps] + armCaps

	def setFilterYaw( self, yaw ):
		"""
		define method
		�������ò�������ķ���
		//˲��ı䳯�򣬲����л������ csol-2739
		"""
		if not self.inWorld: return
		if hasattr( self.filter, "latency" ):
			self.filter.latency = 0.0
		NPCObject.setFilterYaw( self, yaw )

	def intonate( self, skillID, intonateTime, targetObject ):
		"""
		Define method.
		��������

		@type skillID: INT
		"""
		CombatUnit.intonate( self, skillID, intonateTime, targetObject )
		# ����������ʵʱת��
		sk = skills.getSkill( skillID )
		func = Functor( self.rotateToTarget, targetObject )
		if sk and not sk.isNotRotate:
			self.rotateTimerID = Timer.addTimer( 0.1, 0.1, func )

	def rotateToTarget( self, targetObject ):
		"""
		ת��Ŀ��
		"""
		if not self.inWorld: return

		if self.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			return

		effectState = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP
		if not ( self.effect_state & effectState ) == 0: #��ֹת����ж�
			return
		position = targetObject.getObjectPosition()
		disPos = position - self.position
		yaw = disPos.yaw
		if math.fabs( yaw ) > 0.0:
			if hasattr( self.filter, "setYaw" ):
				self.filter.setYaw( yaw )
			model = self.getModel()
			if model: model.yaw = yaw

	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		�����ж�

		@type reason: INT
		"""
		CombatUnit.spellInterrupted( self, skillID, reason )
		if self.rotateTimerID != 0:
			Timer.cancel( self.rotateTimerID )
			self.rotateTimerID = 0

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		��ʽʩ�ŷ�����������ʩ��������

		@type skillID: INT
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		CombatUnit.castSpell( self, skillID, targetObject )
		if self.rotateTimerID != 0:
			Timer.cancel( self.rotateTimerID )
			self.rotateTimerID = 0

# Monster.py

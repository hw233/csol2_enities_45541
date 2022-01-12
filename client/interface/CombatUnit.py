# -*- coding: gb18030 -*-

"""
��ս����λ

$Id: CombatUnit.py,v 1.25 2008-08-20 01:46:03 yangkai Exp $
"""

import BigWorld
from bwdebug import *
from SpellUnit import SpellUnit
import utils
import csdefine
import event.EventCenter as ECenter
import GUIFacade
import Define
import EntityCache
import csconst
import random
from gbref import rds
g_entityCache = EntityCache.EntityCache.instance()
import Const
from Function import Functor
from config.client.ModelColorConfig import Datas as MCData
import Math
from RelationStaticModeMgr import RelationStaticModeMgr
import RelationDynamicObjImpl

g_relationStaticMgr = RelationStaticModeMgr.instance()



class CombatUnit( SpellUnit ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpellUnit.__init__( self )
		# ��¼��ǰЧ��
		self.allEffects = {}
		# ��¼Buff����
		self.buffAction = {}
		# ��¼buffЧ��
		self.buffEffect = {}
		# ��ͨ������ǰorder
		self.nAttackOrder = 0
		# ��ͨ�����ϴι�����ID
		self.nAttackID = 0
		# Ǳ��
		self.isSnake = False
		self.weaponType = 0
		# ��ͼ����Ч��
		self.currAreaEffect = []
		# ��������Ч��
		self.homingEffect = None
		# ����������Ч��
		self.movingEffect = None
		#linkeffect��Ч
		self.linkEffect = []
		self.linkEffectModel = None
		self.castEffect = None
		
		self.isShowSelf = True      #�Ƿ���ʾ�Լ�,���ȼ���ߵ��ж� ���ڲ�������Ч��������ģ�� 
		self.isFlasColorEntity = False #���������в����صı�� False ��ʾ������
		# �ɷ�����֪ͨ�Ŀͻ����ƶ�����ʱ��
		self.moveTime = 0.0
		# �ɷ�����֪ͨ�Ŀͻ����ƶ�����¼����
		self.lastPos = Math.Vector3( 0, 0, 0 )
		self.homingTotalTime = 0.0  #�������˹����ж�����ʱ��
		self.homingDir = None #�������˹����г���
		self.castSounds = []	#cast��Ч
		self.rotateTarget = None
		self.rotateAction = ""

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		SpellUnit.onCacheCompleted( self )
		if self.checkFlasColor():
			self.setIsShowSelf( False )
		self.set_effect_state()
		#self.set_targetID(0)
		if self.hasFlag(csdefine.ENTITY_FLAG_SPECIAL_BOSS):  #���������49��־λ
			self.dealSpecialSign(0)


	def leaveWorld( self ) :
		"""
		it will be called, when character leave world
		"""
		SpellUnit.leaveWorld( self )
		self.allEffects = {}
		self.buffAction = {}
		self.buffEffect = {}
		self.nAttackOrder = 0
		self.nAttackID = 0
		self.isSnake = False
		self.currAreaEffect = []

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isAlive( self ) :
		"""
		indicate whether the character is alive
		"""
		return self.getState() != csdefine.ENTITY_STATE_DEAD

	def isDead( self ):
		"""
		virtual method.

		@return: BOOL�������Լ��Ƿ��Ѿ��������ж�
		@rtype:  BOOL
		"""
		# ��Ȼ��һ�������������ӿ�����Ҫ��
		return self.getState() == csdefine.ENTITY_STATE_DEAD

	def canFight( self ):
		"""
		virtual method.

		@return: BOOL�������Լ��Ƿ���ս�����ж�
		@rtype:  BOOL
		"""
		return not self.actionSign( csdefine.ACTION_FORBID_FIGHT )

	def onReceiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���

		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		self.onDamageModelColor( damageType, damage )
		caster = BigWorld.entities.get( casterID, None )
		if caster is None: return
		player = BigWorld.player()
		if player is None: return
		petID = -1
		pet = player.pcg_getActPet()
		if pet: petID = pet.id
		if casterID == player.id or casterID == petID: return
		if caster.hasFlag( csdefine.ENTITY_FLAG_SHOW_DAMAGE_VALUE ):
			if damage > 0:
				if ( damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# �����˺�
					ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
				else:
					# ��ͨ�˺�
					ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
			else:
				# Miss
				ECenter.fireEvent( "EVT_ON_SHOW_MISS_ATTACK", self.id )

	def onDamageModelColor( self, damageType, damage ):
		"""
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		�˺�����ģ�ͱ�ɫ
		"""
		if damage <= 0: return
		data = MCData.get( damageType )
		if data is None: return

		color, lastTime = data
		self.modelColorMgr.setModelColor( color, lastTime )

	def addModelColorBG( self, id, color, lastTime ):
		"""
		���ģ�͵ı�����ɫ
		@type id			Uint64
		@param id			Ψһ��ʶ��,ͨ����buffID
		@type color			Vector4
		@param color		��ɫ
		@type lastTime		Float
		@param lastTime		���뵭��ʱ��
		@return None
		"""
		self.modelColorMgr.addModelColorBG( id, color, lastTime )

	def removeModelColorBG( self, id ):
		"""
		�Ƴ�ģ�͵ı�����ɫ
		@type id			Uint64
		@param id			Ψһ��ʶ��,ͨ����buffID
		@return None
		"""
		self.modelColorMgr.removeModelColorBG( id )


	# ----------------------------------------------------------------
	# about actions
	# ----------------------------------------------------------------

	def getState( self ):
		"""
		��ȡ״̬��
		@return :	��ǰ״̬
		@rtype	:	integer
		"""
		return self.state

	def getActWord( self ):
		"""
		��ȡ�������ơ�Ӧ�ú����ã�һ���ʹ��actionSign()�������Ƿ�������
		@return	:	��ǰ��������
		@rtype	:	integer
		"""
		return self.actWord

	def actionSign( self, actionWord ):
		"""
		�Ƿ���ڱ�ǡ�

		@param actionWorld	:	�����, see also csdefine.ACTION_*
		@return	:	�����, see also csdefine.ACTION_*
		@rtype	:	bool
		"""
		return self.actWord & actionWord != 0

	def set_state( self, old = 0):
		"""
		�ӷ������յ�״̬�ı�֪ͨ
		"""
		self.onStateChanged( old, self.state )

	def set_actWord( self, old = 0):
		"""
		virtual method = 0;

		�ӷ������յ��������Ƹı�֪ͨ
		"""
		pass

	def onStateChanged( self, old, new ):
		"""
		virtual method.
		״̬�л���

		@param old	:	������ǰ��״̬
		@type old	:	integer
		@param new	:	�����Ժ��״̬
		@type new	:	integer
		"""
		pass

	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
		else:
			return csdefine.RELATION_NONE

	# ----------------------------------------------------------------
	# about attributes
	# ----------------------------------------------------------------
	def getHP( self ):
		"""
		@return: INT
		"""
		return self.HP

	def getHPMax( self ):
		"""
		@return: INT
		"""
		return self.HP_Max

	def getMP( self ):
		"""
		@return: INT
		"""
		return self.MP

	def getMPMax( self ):
		"""
		@return: INT
		"""
		return self.MP_Max

	def getLevel( self ):
		"""
		@return: INT
		"""
		return self.level

	def set_HP( self, oldValue ) :
		"""
		when hp changed, it will be called
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_HP_CHANGED", self, self.HP, self.HP_Max, oldValue )

	def set_HP_Max( self, oldValue ) :
		"""
		when the max hp value changed, it will be called
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_HP_MAX_CHANGED", self, self.HP, self.HP_Max, oldValue )

	def set_MP( self, oldValue ) :
		"""
		when the mp changed, it will be called
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_MP_CHANGED", self, self.MP, self.MP_Max )

	def set_MP_Max( self, oldValue ) :
		"""
		when the max mp value changed, it will be called
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_MP_MAX_CHANGED", self, self.MP, self.MP_Max )

	def set_level( self, oldValue ) :
		"""
		when level changed, it will be called
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_LEVEL_CHANGED", self, oldValue, self.getLevel() )


	# ----------------------------------------------------------------------------------------------------
	#  race, class, gender, faction
	# ----------------------------------------------------------------------------------------------------

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

	def set_targetID( self, old ):
		if old != self.targetID:
			if self.targetID != 0:
				target = BigWorld.entities.get( self.targetID, None )
				if target and not target.isCacheOver:
					g_entityCache.addUrgent( target )
		if self.hasFlag(csdefine.ENTITY_FLAG_SPECIAL_BOSS):
			self.dealSpecialSign(old)

	def dealSpecialSign(self, old):
		target = BigWorld.entities.get(self.targetID, None)
		oldTarget = BigWorld.entities.get(old, None)
		self.changeRoleSign(target, True)
		self.changeRoleSign(oldTarget, False)
		if target and  target.getEntityType() == csdefine.ENTITY_TYPE_PET:  #��������
			role = BigWorld.entities.get(target.ownerID, None)
			self.changeRoleSign(role, True)
		if oldTarget and oldTarget.getEntityType() == csdefine.ENTITY_TYPE_PET: #��������
			role = BigWorld.entities.get(target.ownerID, None)
			self.changeRoleSign(role, Flase)	
	
			
	def changeRoleSign(self, target, value):
		if target and target.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", target, "cityWarer", value )		
			
	def changePetOwnerSign(self, target, value):
		if target and  target.getEntityType() == csdefine.ENTITY_TYPE_PET:  #��������
			role = BigWorld.entities.get(target.ownerID, None)
			self.changeRoleSign(role, value)


	def getCamp( self ):
		"""
		ȡ��������Ӫ
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_CAMP ) >> 20

	#------------------------------------------------------------------------------------------------------
	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		pass

	#------------------------------------------------------------------------------------------------------
	# Ǳ�����
	#------------------------------------------------------------------------------------------------------
	def resetSnake( self ):
		"""
		�ڿͻ������player����Ǳ���Ƿ�ɹ�
		�ȼ���=(Ǳ���߽�ɫ�ȼ�*5+Ǳ�еȼ�ֵ����) �C (����߽�ɫ�ȼ�*5+���ȼ�ֵ����)
		���ռ���=( 1 �C (�ȼ���+25)/50)^2 + (��⼸������ �C Ǳ�б���⼸������)
		"""
		#���û����Ǳ��״̬
		if self.effect_state & csdefine.EFFECT_STATE_PROWL == 0:
			self.isSnake = False
			return

		# ����⼸�� ���㹫ʽ
		player = BigWorld.player()
		difLevel = ( self.level - player.level )*5 + self.sneakLevelAmend - player.realLookLevelAmend
		if difLevel > 25:
			odds = 0.0
		elif difLevel < -25:
			odds = 1.0
		else:
			odds = ( 1 - ( difLevel + 25 )/50.0 ) ** 2 + ( player.realLookAmend - self.lessRealLookAmend )/csconst.FLOAT_ZIP_PERCENT
		print "odds--->>>", odds, self.id
		# ����⵽��
		if random.random() <= odds:
			self.isSnake = False
			return
		self.isSnake = True

	def set_effect_state( self, oldEState = 0 ):
		"""
		"""
		# ˢ���Ƿ�Ǳ�гɹ�
		old_isSnake = self.isSnake
		self.resetSnake()
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_VEHICLE ]
		if self.getEntityType() in toggleTypes:
			self.updateVisibility()
			return
		if old_isSnake != self.isSnake:
			self.updateVisibility()
			return
	
	def setIsShowSelf( self, isShow ):
		"""
		�Ƿ���ʾģ��
		"""
		self.isShowSelf = isShow
		self.updateVisibility()
	
	def setFlasColorEntity( self, flag ):
		"""
		�������������ز����صı��
		"""
		self.isFlasColorEntity = flag

	def checkFlasColor( self ):
		"""
		����Ƿ���������
		"""
		for label, active, options in BigWorld.graphicsSettings():
			if label == "FLASH_COLOR":
				return active
			
	def isshowModel( self ):
		"""
		�ռ��жϣ������е����Ƿ�����ģ��
		"""
		if ( not self.isShowSelf ) and ( not self.isFlasColorEntity ) :
			return False
		return True
		
	def onSnakeStateChange( self, state ):
		"""
		Define Method
		Ŀ��Ǳ�лص���ȷ��������Ч����ͻ��˱���һ��
		"""
		model = self.getModel()
		if model is None: return
		if state:
			self.isSnake = True
			type = Define.MODEL_VISIBLE_TYPE_FALSE
		else:
			self.isSnake = False
			type = Define.MODEL_VISIBLE_TYPE_SNEAK
		self.setModelVisible( type )

	def setModelVisible( self, visibleType ):
		"""
		����ģ����ʾ��ʽ
		�μ� Define.MODEL_VISIBLE_TYPE_*
		"""
		# ����ʾģ��
		if visibleType == Define.MODEL_VISIBLE_TYPE_FALSE:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
		# ��ʾ����ģ��
		elif visibleType == Define.MODEL_VISIBLE_TYPE_TRUE:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 1.0, 1.0 )
		elif visibleType == Define.MODEL_VISIBLE_TYPE_SNEAK:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 0.5, 1.0 )

	def getWeaponType( self ):
		"""
		�������ͣ����������û�������ģ�
		"""
		return Define.WEAPON_TYPE_NONE

	def attachBubblesEffect( self ):
		"""
		���ˮ��Ч��
		"""
		player = BigWorld.player()
		if player is None: return
		currArea = player.getCurrArea()
		if currArea is None: return

		functor = Functor( self.onAreaEffectLoad, currArea, Const.MAP_AREA_SHUIPAO_HP )
		rds.effectMgr.createParticleBG( self.getModel(), Const.MAP_AREA_SHUIPAO_HP, Const.MAP_AREA_SHUIPAO_PATH, functor, type = Define.TYPE_PARTICLE_PLAYER )

	def detachBubblesEffect( self ):
		"""
		�Ƴ���ˮ��Ч��
		"""
		for hp, particle in self.currAreaEffect:
			rds.effectMgr.detachObject( self.getModel(), hp, particle )

		self.currAreaEffect = []

	def onAreaEffectLoad( self, area, hp, particle ):
		"""
		"""
		if not self.inWorld: return

		player = BigWorld.player()
		if player is None: return
		currArea = player.getCurrArea()
		if currArea is None: return
		if currArea != area: return

		self.currAreaEffect.append( ( hp, particle ) )

	def onMakeASound( self, soundEvent, flag ):
		"""
		Define Method
		����һ������
		"""
		if not flag:
			rds.soundMgr.playVocality( soundEvent, self.getModel() )
		else:
			rds.soundMgr.play2DSound( soundEvent )

	# ----------------------------------------------------------------
	# ��������
	# ----------------------------------------------------------------
	def onStartHomingSpell( self, persistent ):
		"""
		define method.
		��ʼ��������
		"""
		SpellUnit.onStartHomingSpell( self, persistent )

	def onFiniHomingSpell( self ):
		"""
		������������
		"""
		SpellUnit.onFiniHomingSpell( self )

	def isPosture( self, posture ):
		"""
		�Ƿ���ĳ����̬
		"""
		return self.posture == posture

	# ------------------------------------------------------------------------------
	# ����ͻ����ƶ�����
	# ------------------------------------------------------------------------------
	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.AvatarDropFilter()

	def outputCallback( self, moveDir, needTime, dTime ):
		"""
		filter��λ��ˢ�»ص�����
		"""
		self.moveTime += dTime
		if self.moveTime >= needTime:
			BigWorld.callback( 0.01, self._onMoveOver )
			return self.lastPos
		else:
			return self.position + moveDir * dTime

	def _onMoveOver( self ):
		"""
		�ƶ�����
		"""
		if not self.inWorld: return

		self.moveTime = 0.0
		self.filter.outputCallback = None
		# ͬ���������������ݣ���үֻ���������ˡ�
		self.filter.restartMoving()
		self.filter.latency = 0
		self.filter = BigWorld.PlayerAvatarFilter()
		self.filter = self.filterCreator()

	def lineToPoint( self, position, speed ):
		"""
		�ƶ��������
		"""
		if self.filter is None: return
		if not hasattr( self.filter, "outputCallback" ): return
		# �����ƶ�ʱ��
		self.moveTime = 0.0
		# ��¼����ƶ�λ��
		self.filter.setLastPosition( position )
		self.lastPos = Math.Vector3( position )
		# ���㵥λ�ٶȺ�����ʱ��
		yawDir = position - self.position
		yawDir.normalise()
		moveDir = yawDir * speed
		distance = self.position.flatDistTo( position )
		needTime = distance / speed
		# ���ûص�����
		func = Functor( self.outputCallback, moveDir, needTime )
		self.filter.outputCallback = func

	def moveToPosFC( self, pos, speed, dir ):
		"""
		Define Method
		������֪ͨ�ƶ���ĳ��
		@param pos : �ƶ��������
		@type pos : Math.Vector3
		@param speed : �ƶ��ٶ�
		@type speed : Float
		@param dir : �ƶ�����
		@type dir : Float
		"""
		dis = ( self.position - pos ).length
		if self.homingTotalTime > 0.0:
			speed = dis / self.homingTotalTime
		self.homingTotalTime = 0.0
		self.lineToPoint( pos, speed )

	def setFilterLatency( self ):
		"""
		define method.
		˲��ͬ��������Ϣ
		"""
		if not self.inWorld: return
		if hasattr( self.filter, "latency" ):
			self.filter.latency = 0.0

	def queryCombatRelation( self, entity ):
		"""
		��ѯս����ϵ�ӿ�
		"""
		relation = 0
		ownRelationInsList = self.getRelationInsList()
		if ownRelationInsList:
			for inst in ownRelationInsList:
				relation = inst.queryCombatRelation( entity )
				if relation != csdefine.RELATION_NONE:
					return relation
					
		entityRelationInsList = entity.getRelationInsList()
		if entityRelationInsList:
			for inst in entityRelationInsList:
				relation = inst.queryCombatRelation( self )
				if relation != csdefine.RELATION_NONE:
					return relation
					
		type = self.getRelationMode()
		relationIns = g_relationStaticMgr.getRelationInsFromType( type )
		relation = relationIns.queryCombatRelation( self, entity )
		if relation != csdefine.RELATION_NONE:
			return relation
		
		return csdefine.RELATION_NEUTRALLY
	
	def getRelationEntity( self ):
		"""
		��ȡ��ʵ�Ƚϵ�entityʵ��
		"""
		return self

	def getCombatCamp( self ):
		"""
		��ȡս����Ӫ
		"""
		return self.combatCamp
		
	def getIsUseCombatCamp( self ):
		"""
		��ȡ�Ƿ�ʹ��ս����Ӫ
		"""
		return self.isUseCombatCamp
	
	def getRelationMode( self ):
		"""
		��ȡս����ϵģʽ
		"""
		return self.relationMode
	
	def getRelationInsList( self ):
		"""
		��ȡ�����relationInsList��Ҳ���ǹ�ϵʵ���б�
		"""
		return self.relationInsList

	def isNeedQueryRelation( self, entity ):
		"""
		�Ƿ���Ҫ��ѯ����֮��Ĺ�ϵ������Ѿ����ٻ��߲���CombatUnit����
		�Ͳ���Ҫ���²�ѯ��
		"""
		if not isinstance( entity, CombatUnit ):
			return False
		else:
			return True
	
# CombatUnit.py

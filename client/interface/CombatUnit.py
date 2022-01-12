# -*- coding: gb18030 -*-

"""
可战斗单位

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
		# 记录当前效果
		self.allEffects = {}
		# 记录Buff动作
		self.buffAction = {}
		# 记录buff效果
		self.buffEffect = {}
		# 普通攻击当前order
		self.nAttackOrder = 0
		# 普通攻击上次攻击的ID
		self.nAttackID = 0
		# 潜行
		self.isSnake = False
		self.weaponType = 0
		# 地图区域效果
		self.currAreaEffect = []
		# 连续技能效果
		self.homingEffect = None
		# 作用区域技能效果
		self.movingEffect = None
		#linkeffect光效
		self.linkEffect = []
		self.linkEffectModel = None
		self.castEffect = None
		
		self.isShowSelf = True      #是否显示自己,优先级最高的判断 用于播放闪屏效果中隐藏模型 
		self.isFlasColorEntity = False #闪屏过程中不隐藏的标记 False 表示会隐藏
		# 由服务器通知的客户端移动表现时间
		self.moveTime = 0.0
		# 由服务器通知的客户端移动最后记录坐标
		self.lastPos = Math.Vector3( 0, 0, 0 )
		self.homingTotalTime = 0.0  #连击击退过程中动作总时间
		self.homingDir = None #连击击退过程中朝向
		self.castSounds = []	#cast音效
		self.rotateTarget = None
		self.rotateAction = ""

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		SpellUnit.onCacheCompleted( self )
		if self.checkFlasColor():
			self.setIsShowSelf( False )
		self.set_effect_state()
		#self.set_targetID(0)
		if self.hasFlag(csdefine.ENTITY_FLAG_SPECIAL_BOSS):  #处理怪物有49标志位
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

		@return: BOOL，返回自己是否已经死亡的判断
		@rtype:  BOOL
		"""
		# 虽然不一定会死亡，但接口是需要的
		return self.getState() == csdefine.ENTITY_STATE_DEAD

	def canFight( self ):
		"""
		virtual method.

		@return: BOOL，返回自己是否能战斗的判断
		@rtype:  BOOL
		"""
		return not self.actionSign( csdefine.ACTION_FORBID_FIGHT )

	def onReceiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。

		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: 伤害数值
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
					# 致命伤害
					ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
				else:
					# 普通伤害
					ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
			else:
				# Miss
				ECenter.fireEvent( "EVT_ON_SHOW_MISS_ATTACK", self.id )

	def onDamageModelColor( self, damageType, damage ):
		"""
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: 伤害数值
		@type      damage: INT
		伤害导致模型变色
		"""
		if damage <= 0: return
		data = MCData.get( damageType )
		if data is None: return

		color, lastTime = data
		self.modelColorMgr.setModelColor( color, lastTime )

	def addModelColorBG( self, id, color, lastTime ):
		"""
		添加模型的背景颜色
		@type id			Uint64
		@param id			唯一标识符,通常是buffID
		@type color			Vector4
		@param color		颜色
		@type lastTime		Float
		@param lastTime		淡入淡出时间
		@return None
		"""
		self.modelColorMgr.addModelColorBG( id, color, lastTime )

	def removeModelColorBG( self, id ):
		"""
		移除模型的背景颜色
		@type id			Uint64
		@param id			唯一标识符,通常是buffID
		@return None
		"""
		self.modelColorMgr.removeModelColorBG( id )


	# ----------------------------------------------------------------
	# about actions
	# ----------------------------------------------------------------

	def getState( self ):
		"""
		获取状态。
		@return :	当前状态
		@rtype	:	integer
		"""
		return self.state

	def getActWord( self ):
		"""
		获取动作限制。应该很少用，一般会使用actionSign()来测试是否动作可用
		@return	:	当前动作限制
		@rtype	:	integer
		"""
		return self.actWord

	def actionSign( self, actionWord ):
		"""
		是否存在标记。

		@param actionWorld	:	标记字, see also csdefine.ACTION_*
		@return	:	标记字, see also csdefine.ACTION_*
		@rtype	:	bool
		"""
		return self.actWord & actionWord != 0

	def set_state( self, old = 0):
		"""
		从服务器收到状态改变通知
		"""
		self.onStateChanged( old, self.state )

	def set_actWord( self, old = 0):
		"""
		virtual method = 0;

		从服务器收到动作限制改变通知
		"""
		pass

	def onStateChanged( self, old, new ):
		"""
		virtual method.
		状态切换。

		@param old	:	更改以前的状态
		@type old	:	integer
		@param new	:	更改以后的状态
		@type new	:	integer
		"""
		pass

	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
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
		是否为指定种族职业。
		@return: bool
		"""
		return self.raceclass & mask == rc

	def getClass( self ):
		"""
		取得自身职业
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def getGender( self ):
		"""
		取得自身性别
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getRace( self ):
		"""
		取得自身种族
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_RACE

	def getFaction( self ):
		"""
		取得自身所属的势力
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
		if target and  target.getEntityType() == csdefine.ENTITY_TYPE_PET:  #处理宠物的
			role = BigWorld.entities.get(target.ownerID, None)
			self.changeRoleSign(role, True)
		if oldTarget and oldTarget.getEntityType() == csdefine.ENTITY_TYPE_PET: #处理宠物的
			role = BigWorld.entities.get(target.ownerID, None)
			self.changeRoleSign(role, Flase)	
	
			
	def changeRoleSign(self, target, value):
		if target and target.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", target, "cityWarer", value )		
			
	def changePetOwnerSign(self, target, value):
		if target and  target.getEntityType() == csdefine.ENTITY_TYPE_PET:  #处理宠物的
			role = BigWorld.entities.get(target.ownerID, None)
			self.changeRoleSign(role, value)


	def getCamp( self ):
		"""
		取得自身阵营
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_CAMP ) >> 20

	#------------------------------------------------------------------------------------------------------
	def initCacheTasks( self ):
		"""
		初始化缓冲器任务
		"""
		pass

	#------------------------------------------------------------------------------------------------------
	# 潜行相关
	#------------------------------------------------------------------------------------------------------
	def resetSnake( self ):
		"""
		在客户端针对player重设潜行是否成功
		等级差=(潜行者角色等级*5+潜行等级值修正) – (侦测者角色等级*5+侦测等级值修正)
		最终几率=( 1 – (等级差+25)/50)^2 + (侦测几率修正 – 潜行被侦测几率修正)
		"""
		#玩家没有在潜行状态
		if self.effect_state & csdefine.EFFECT_STATE_PROWL == 0:
			self.isSnake = False
			return

		# 被侦测几率 计算公式
		player = BigWorld.player()
		difLevel = ( self.level - player.level )*5 + self.sneakLevelAmend - player.realLookLevelAmend
		if difLevel > 25:
			odds = 0.0
		elif difLevel < -25:
			odds = 1.0
		else:
			odds = ( 1 - ( difLevel + 25 )/50.0 ) ** 2 + ( player.realLookAmend - self.lessRealLookAmend )/csconst.FLOAT_ZIP_PERCENT
		print "odds--->>>", odds, self.id
		# 被侦测到了
		if random.random() <= odds:
			self.isSnake = False
			return
		self.isSnake = True

	def set_effect_state( self, oldEState = 0 ):
		"""
		"""
		# 刷新是否潜行成功
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
		是否显示模型
		"""
		self.isShowSelf = isShow
		self.updateVisibility()
	
	def setFlasColorEntity( self, flag ):
		"""
		闪屏过程中隐藏不隐藏的标记
		"""
		self.isFlasColorEntity = flag

	def checkFlasColor( self ):
		"""
		检测是否在闪屏中
		"""
		for label, active, options in BigWorld.graphicsSettings():
			if label == "FLASH_COLOR":
				return active
			
	def isshowModel( self ):
		"""
		终极判断，闪屏中到底是否隐藏模型
		"""
		if ( not self.isShowSelf ) and ( not self.isFlasColorEntity ) :
			return False
		return True
		
	def onSnakeStateChange( self, state ):
		"""
		Define Method
		目标潜行回调，确保服务器效果与客户端表现一致
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
		设置模型显示方式
		参见 Define.MODEL_VISIBLE_TYPE_*
		"""
		# 不显示模型
		if visibleType == Define.MODEL_VISIBLE_TYPE_FALSE:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
		# 显示整体模型
		elif visibleType == Define.MODEL_VISIBLE_TYPE_TRUE:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 1.0, 1.0 )
		elif visibleType == Define.MODEL_VISIBLE_TYPE_SNEAK:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 0.5, 1.0 )

	def getWeaponType( self ):
		"""
		武器类型（场景物件是没有武器的）
		"""
		return Define.WEAPON_TYPE_NONE

	def attachBubblesEffect( self ):
		"""
		添加水泡效果
		"""
		player = BigWorld.player()
		if player is None: return
		currArea = player.getCurrArea()
		if currArea is None: return

		functor = Functor( self.onAreaEffectLoad, currArea, Const.MAP_AREA_SHUIPAO_HP )
		rds.effectMgr.createParticleBG( self.getModel(), Const.MAP_AREA_SHUIPAO_HP, Const.MAP_AREA_SHUIPAO_PATH, functor, type = Define.TYPE_PARTICLE_PLAYER )

	def detachBubblesEffect( self ):
		"""
		移除当水泡效果
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
		发出一个声音
		"""
		if not flag:
			rds.soundMgr.playVocality( soundEvent, self.getModel() )
		else:
			rds.soundMgr.play2DSound( soundEvent )

	# ----------------------------------------------------------------
	# 引导技能
	# ----------------------------------------------------------------
	def onStartHomingSpell( self, persistent ):
		"""
		define method.
		开始引导技能
		"""
		SpellUnit.onStartHomingSpell( self, persistent )

	def onFiniHomingSpell( self ):
		"""
		结束引导技能
		"""
		SpellUnit.onFiniHomingSpell( self )

	def isPosture( self, posture ):
		"""
		是否处于某种姿态
		"""
		return self.posture == posture

	# ------------------------------------------------------------------------------
	# 怪物客户端移动表现
	# ------------------------------------------------------------------------------
	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return BigWorld.AvatarDropFilter()

	def outputCallback( self, moveDir, needTime, dTime ):
		"""
		filter的位置刷新回调函数
		"""
		self.moveTime += dTime
		if self.moveTime >= needTime:
			BigWorld.callback( 0.01, self._onMoveOver )
			return self.lastPos
		else:
			return self.position + moveDir * dTime

	def _onMoveOver( self ):
		"""
		移动结束
		"""
		if not self.inWorld: return

		self.moveTime = 0.0
		self.filter.outputCallback = None
		# 同步服务器坐标数据，大爷只能用这招了。
		self.filter.restartMoving()
		self.filter.latency = 0
		self.filter = BigWorld.PlayerAvatarFilter()
		self.filter = self.filterCreator()

	def lineToPoint( self, position, speed ):
		"""
		移动到坐标点
		"""
		if self.filter is None: return
		if not hasattr( self.filter, "outputCallback" ): return
		# 重置移动时间
		self.moveTime = 0.0
		# 记录最后移动位置
		self.filter.setLastPosition( position )
		self.lastPos = Math.Vector3( position )
		# 计算单位速度和所需时间
		yawDir = position - self.position
		yawDir.normalise()
		moveDir = yawDir * speed
		distance = self.position.flatDistTo( position )
		needTime = distance / speed
		# 设置回调函数
		func = Functor( self.outputCallback, moveDir, needTime )
		self.filter.outputCallback = func

	def moveToPosFC( self, pos, speed, dir ):
		"""
		Define Method
		服务器通知移动到某点
		@param pos : 移动到坐标点
		@type pos : Math.Vector3
		@param speed : 移动速度
		@type speed : Float
		@param dir : 移动朝向
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
		瞬间同步坐标信息
		"""
		if not self.inWorld: return
		if hasattr( self.filter, "latency" ):
			self.filter.latency = 0.0

	def queryCombatRelation( self, entity ):
		"""
		查询战斗关系接口
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
		获取真实比较的entity实体
		"""
		return self

	def getCombatCamp( self ):
		"""
		获取战斗阵营
		"""
		return self.combatCamp
		
	def getIsUseCombatCamp( self ):
		"""
		获取是否使用战斗阵营
		"""
		return self.isUseCombatCamp
	
	def getRelationMode( self ):
		"""
		获取战斗关系模式
		"""
		return self.relationMode
	
	def getRelationInsList( self ):
		"""
		获取自身的relationInsList，也就是关系实例列表
		"""
		return self.relationInsList

	def isNeedQueryRelation( self, entity ):
		"""
		是否需要查询两者之间的关系，如果已经销毁或者不是CombatUnit对象，
		就不需要往下查询了
		"""
		if not isinstance( entity, CombatUnit ):
			return False
		else:
			return True
	
# CombatUnit.py

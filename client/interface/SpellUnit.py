# -*- coding: gb18030 -*-

"""
施法单位

$Id: SpellUnit.py,v 1.27 2008-08-06 06:11:52 kebiao Exp $
"""

import BigWorld
from bwdebug import *
import skills
import GUIFacade
import Define
import csconst
import csdefine
import csstatus
import SkillTargetObjImpl
import event.EventCenter as ECenter
from ActionRule import ActionRule
from gbref import rds
from Function import Functor
from ItemsFactory import BuffItem

class SpellUnit:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.attrBuffs = []			# all buffs and duffs
		self.attrBuffItems = []
		self.triggerSkillDict = {}		#用于记录玩家客户端触发连续技能add by wuxo
		self.actionRule = ActionRule()
		self.beHomingCasterID = 0  #当前正在被谁连击
		self.actionCount = 0	   #播放动作调用次数

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		player = BigWorld.player()
		if self == player or self == player.pcg_getActPet():			# 玩家自己的放到进度条中统一初始化( hyw -- 2008.06.09 )
			return
		self.cell.requestBuffs()

	def leaveWorld( self ) :
		"""
		it will be called, when character leave world
		"""
		pass

	def useSpell( self, skillID, target ):
		"""
		使用技能
		"""
		self.interuptPendingBuff()
		for pid in BigWorld.player().triggerSkillDict:
			if BigWorld.player().triggerSkillDict[pid] == skillID:
				skillID = pid
				break
		if self.hasSpaceSkill( skillID ):
			self.cell.useSpaceSpell( skillID, target )
		else:
			self.cell.useSpell( skillID, target )

	def interuptPendingBuff( self ):
		"""
		向服务器申请移除未决buff
		"""
		for buffData in self.attrBuffs:
			if buffData[ "skill" ].getID() == csconst.PENDING_BUFF_ID:
				self.requestRemoveBuff( buffData[ "index" ] )

	# ----------------------------------------------------------------
	# about skill
	# ----------------------------------------------------------------
	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		法术中断

		@type reason: INT
		"""
		INFO_MSG( "%i: spell %i interrupted by %i" % ( self.id, skillID, reason ) )
		try:
			spell = skills.getSkill( skillID )
		except KeyError:
			WARNING_MSG( "%i: skill %i not found." % ( self.id, skillID ) )
			return

		spell.interrupt( self, reason )


	def intonate( self, skillID, intonateTime,targetObject ):
		"""
		Define method.
		吟唱法术

		@type skillID: INT
		"""
		INFO_MSG( "%i: intonate %i, time:%i" % ( self.id, skillID, intonateTime ) )
		spell = skills.getSkill( skillID )
		spell.intonate( self, intonateTime,targetObject )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		正式施放法术——该起施法动作了

		@type skillID: INT
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		spell = skills.getSkill( skillID )
		spell.cast( self, targetObject )

	def receiveSpell( self, casterID, skillID, damageType, damage ):
		"""
		Define method.
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		if skillID != 0:
			spell = skills.getSkill( skillID )
			spell.receiveSpell( self, casterID, damageType, damage )

	def onEndSpellMove(self, casterID):
		if BigWorld.entities.has_key( casterID ):
			caster = BigWorld.entities[ casterID ]
			rds.skillEffect.stopMovingEffects( caster )
	# ----------------------------------------------------------------
	# 引导技能
	# ----------------------------------------------------------------
	def onStartHomingSpell( self, persistent ):
		"""
		define method.
		开始引导技能
		"""
		pass

	def onFiniHomingSpell( self ):
		"""
		结束引导技能
		"""
		pass

	def onTriggerSpell(self, parentSkillID,skillID):
		"""
		连续技触发技能add by wuxo 2012-2-8
		"""
		self.triggerSkillDict[parentSkillID] = skillID
		ECenter.fireEvent( "EVT_ON_SKILL_TRIGGER_SPELL", parentSkillID, skillID )
	# ----------------------------------------------------------------
	# 对位置施法
	# ----------------------------------------------------------------
	def onSpellToPosition( self, skill ):
		"""
		virtual method.
		收到一个对位置施法的请求
		"""
		pass
		#ECenter.fireEvent( "EVT_ON_SHOW_SUPERADDTION_BOX" )

	# ----------------------------------------------------------------
	# about buffer
	# ----------------------------------------------------------------
	def onAddBuff( self, buffData ):
		"""
		Define method.
		增加一个buff，用于在获得一个buff时的通知。

		@param buffData: see also alias.xml <BUFF>
		@type  buffData: BUFF
		"""
		self._addBuff( buffData )

		if self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			return

		if buffData["isNotIcon"]: return

		# 获得buff时需要提示
		if BigWorld.player().id == self.id :
			self.statusMessage( csstatus.ACCOUNT_STATE_REV_BUFF, buffData["skill"].getName() )
		else:
			if buffData["caster"] == BigWorld.player().id:
				BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_ADD_BUFF_TO, self.getName(), buffData["skill"].getName() )

	def onReceiveBuff( self, buffData ):
		"""
		Define method.
		从服务器接收一个buff，用于接收在别的玩家enterWorld时向服务器申请对方的buff列表

		@param buffData: see also alias.xml <BUFF>
		@type  buffData: BUFF
		"""
		self._addBuff( buffData )

	def _addBuff( self, buffData ):
		"""
		添加一个buff
		"""
		sk = buffData["skill"]
		index = buffData["index"]

		# 检查客户端是否存在2个索引相同的buff， 出现这个现象的原因是
		# 当角色登陆后客户端还未向服务器索要buff列表时，这期间中了一个
		# buff， 受到常规规则这个buff会通知allclients， 于是我们客户端存在了一个
		# 这样的buff， 而这之后客户端角色初始化好了开始向服务器索要buff列表，这时
		# 客户端就会多出一个一样的buff。
		for buff in self.attrBuffs:
			if index == buff[ "index" ]:
				return
		self.attrBuffs.append( buffData )
		buffItem = BuffItem( buffData )
		self.attrBuffItems.append( buffItem )

		INFO_MSG( "%i: add buff: %i-%s, index:%i" % ( self.id , sk.getID(), sk.getBuffID(), index ) )

		caster = BigWorld.entities.get( buffData["caster"] )
		# 被保存到数据库的BUFF在玩家上线的时候是不能保证可以找到施法者的
		sk.cast( caster, self )	# buff光效播放

		self.setArmCaps()

		# 检测是否需要客户端显示BUFF图标
		if buffData["isNotIcon"]: return

		if BigWorld.player().targetEntity and self.id == BigWorld.player().targetEntity.id:
			# 更新选中者的BUFF
			ECenter.fireEvent( "EVT_ON_TARGET_BUFFS_CHANGED" )

		if sk.isMalignant() :
			GUIFacade.onAddDuff( self.id, buffData )
		else :
			GUIFacade.onAddBuff( self.id, buffData )

	def onUpdateBuffData( self, buffIndex, buffData ):
		"""
		Define method.
		对一个或多个已经存在的同类型BUFF or Duff 进行追加操作
		具体对BUFF数据追加什么由继承者决定
		@param buffsIndex: 玩家身上同类型的BUFF所在attrbuffs的位置
		@param buffData: 要修改的数据，一个buff数据字典
		"""
		for idx in range( len(self.attrBuffs) ):
			data = self.attrBuffs[ idx ]
			if data["skill"].getBuffID() == buffData["skill"].getBuffID():
				self.attrBuffs[ idx ] = buffData
				buffIndex = data["index"]
				break
		sk = buffData["skill"]

		# 检测是否需要客户端显示BUFF图标
		if buffData["isNotIcon"]: return

		if BigWorld.player().targetEntity and self.id == BigWorld.player().targetEntity.id:
			# 更新选中者的BUFF
			ECenter.fireEvent( "EVT_ON_TARGET_BUFFS_CHANGED" )
		GUIFacade.onUpdateBDuffData( self.id, buffIndex, buffData, sk.isMalignant() )

	def onRemoveBuff( self, index ):
		"""
		Define method.
		删除buff
		"""
		INFO_MSG( "%i: remove::find buff of index(%i)" % ( self.id, index ) )
		buffData = self.findBuffByIndex( index )
		if not buffData:
			INFO_MSG( "%i: remove::buff [ index:%i ] not found!" % ( self.id, index ) )
			return

		# 移除buff 时, 不管施法者是否存在,都移除效果
		sk = buffData["skill"]
		INFO_MSG( "%i: remove::buff found [ %s-%i ]" % ( self.id, sk.getBuffID(), sk.getID() ) )
		self.attrBuffs.remove( buffData )
		for buffItem in self.attrBuffItems:
			if buffItem.buffIndex == index:
				self.attrBuffItems.remove( buffItem )

		caster = None
		try:
			caster = BigWorld.entities[ buffData[ "caster" ] ]
		except Exception, e:
			WARNING_MSG( "not find the caster,id is", buffData[ "caster" ] )

		sk.end( caster, self )
		player = BigWorld.player()

		self.setArmCaps()

		# 检测是否需要客户端显示BUFF图标
		if buffData["isNotIcon"]: return

		if self.id == player.id:
			if not self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
				self.statusMessage( csstatus.SKILL_BUFF_END, sk.getName()  )

		if player.targetEntity and self.id == player.targetEntity.id:
			# 更新选中者的BUFF
			ECenter.fireEvent( "EVT_ON_TARGET_BUFFS_CHANGED" )

		if buffData["skill"].isMalignant() :
			GUIFacade.onRemoveDuff( self.id, index )
		else :
			GUIFacade.onRemoveBuff( self.id, index )


	def findBuffByUID( self, buffUID ):
		"""
		通过uid找到某个buff
		"""
		for buffData in self.attrBuffs:
			if buffData["skill"].getUID() == buffUID:
				return buffData
		return None

	def findBuffByIndex( self, index ):
		"""
		通过index找到某个buff
		"""
		for buffData in self.attrBuffs:
			if buffData["index"] == index:
				return buffData
		return None

	def findBuffByBuffID( self, buffID ):
		"""
		通过buffid找到某个buff
		@buffID: 整数
		"""
		# 原来的处理有点乱，服务器上的attrBuffs[x]["skill"].getBuffID()是整数，客户端的却是字符串，现在统一使用整数处理 by mushuang
		buffID = int( buffID )
		for buffData in self.attrBuffs:
			if int( buffData["skill"].getBuffID() ) == buffID:
				return buffData
		return None

	def findBuffByID( self, ID ):
		"""
		通过ID查找某个buff
		"""
		ID = int( ID )
		for buffData in self.attrBuffs:
			if buffData["skill"].getID() == ID :
				return buffData
		return None

	def getSourceTypeByBuffIndex( self, buffIndex ):
		"""
		获取buff的小类（buff来源）
		"""
		buffData = self.findBuffByIndex( buffIndex )
		if buffData:
			return buffData["sourceType"]
		else :
			return csdefine.BUFF_ORIGIN_NONE

	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		self.actionCount = 0  # 置空播放动作调用次数

	def playActions( self, actionNames ):
		"""
		播放动作
		param actionName	: 动作名列表
		type actionName		: list of string
		return				: None
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return
		delActionNames = []
		for actionName in actionNames:
			if model and not model.hasAction( actionName ):
				delActionNames.append( actionName )
		for actionName in delActionNames:
			actionNames.remove( actionName )
		if len( actionNames ) == 0: return
		func = Functor( self.onActionOver, actionNames )
		isPlay = self.actionRule.playActions( model, actionNames, functor = func )
		if isPlay:
			self.onPlayActionStart( actionNames )
		else:
			if hasattr( self, "className"):
				DEBUG_MSG( "Entity(className: %s ):action was stopped for priority! currActions:%s, newActions:%s"%( self.className, str(self.actionRule.currActionNames),str(actionNames) ) )

	def onPlayActionStart( self, actionNames ):
		"""
		开始播放动作的时候做点什么...
		"""
		if actionNames == []: return  # 空动作不计数
		self.actionCount += 1

	def onActionOver( self, actionNames ):
		"""
		动作播放完成回调
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return
		# 修正某些极端情况下动作回调的bug
		if actionNames == self.getActionNames() and self.actionCount >= 2:
			actionCount = self.actionCount
			self.onPlayActionOver( actionNames )
			self.actionCount = actionCount - 1  # 极端情况下不计入清零的序列
			return
		self.actionRule.onActionOver( actionNames )
		self.onPlayActionOver( actionNames )

	def onPlayActionOver( self, actionNames ):
		"""
		播放动作结束的时候做点什么...
		"""
		self.actionCount = 0

	def getActionNames( self ):
		"""
		返回当前播放动作列表
		"""
		if not self.inWorld: return []
		return self.actionRule.getActionNames()

	def stopActions( self ):
		"""
		define method.
		停止当前播放的动作
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return

		actionNames = self.getActionNames()
		for actionName in actionNames:
			rds.actionMgr.stopAction( model, actionName )

	def isActionning( self ):
		"""
		当前是否在播放动作
		"""
		if not self.inWorld: return False
		return self.actionRule.isActionning()

	def onHomingSpellResist( self, targetID ):
		"""
		define method.
		连击技能被抵抗的目标ID
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_REST_STATUS", targetID )

	def showSkillName( self, skillID ):
		"""
		显示技能名称
		"""
		pass
	
	def setArmCaps( self ) :
		"""
		动作匹配caps
		"""
		pass
	
	def actionStateMgr( self, state = Define.COMMON_NO ):
		"""
		动作播放管理(技能)
		state 当前的状态
		"""
		model = self.getModel()
		if model is None:
			return False
		
		#如果在跳跃状态就不播放受击动作
		for actionName in model.queue:
			if actionName.startswith( "jump" ):
				return False
		
		#无敌状态/霸体状态不播放任何受击
		if self.effect_state & (csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_HEGEMONY_BODY ) > 0:
			return  False
		
		#吟唱状态下忽视普通受击
		if state == Define.COMMON_BE_HIT and hasattr( self, "intonating" ) and self.intonating():
			return  False
		
		#连击攻击忽视普通受击
		if state == Define.COMMON_BE_HIT and hasattr( self, "isInHomingSpell" ) and self.isInHomingSpell:
			return False
		
		#连击受击忽视普通受击
		if state == Define.COMMON_BE_HIT and self.effect_state & csdefine.EFFECT_STATE_BE_HOMING: 
			return  False
		
		return True
		
# SpellUnit.py

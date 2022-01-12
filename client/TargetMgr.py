# -*- coding: gb18030 -*-
#
# $Id: TargetMgr.py,v 1.20 2008-07-08 09:27:59 yangkai Exp $

"""
implement target info class

2008/01/23: writen by huangyongwei
2008/12/28: modified by huangyongwei
			将 Tact.py 中的目标相关操作功能，全部移到这里
			将目标相关的快捷键功能全部放到这里
"""

import random
import weakref
import BigWorld
import csdefine
import csconst
import csarithmetic
import Const
import utils
import event.EventCenter as ECenter
import GUIFacade

from gbref import rds
from UnitSelect import UnitSelect
from ShortcutMgr import shortcutMgr
from Function import Functor


# --------------------------------------------------------------------
# implement target manager singleton class
# --------------------------------------------------------------------
class TargetMgr :
	__inst = None

	def __init__( self ) :
		assert TargetMgr.__inst is None
		self.__target = None
		self.__nearEnemyList = []															# 最近的一组敌人列表
		self.__nailKindnessList = []														# 最近的一组友好目标列表
		self.__nearTeammateList = []														# 最近的一组队友列表

		shortcutMgr.setHandler( "FIXED_UNBIND_TARGET", self.unbindTarget )					# 取消目标绑定
		shortcutMgr.setHandler( "FIXED_CLOSE_TO_TARGET", self.__closeTarget )				# 靠近指定目标
		shortcutMgr.setHandler( "FIXED_SPELL_TARGET", self.__spellTarget )					# 直接绑定并攻击右键选中的敌人
		shortcutMgr.setHandler( "COMBAT_NAIL_NEAR_ENEMY", self.__nailEnemy )				# 盯上最近的一个敌人
		shortcutMgr.setHandler( "COMBAT_NAIL_FORWARD_ENEMY", self.__nailForeEnemy )			# 选择前一个敌人
		shortcutMgr.setHandler( "COMBAT_NAIL_NEAR_KINDNESS", self.__nailKindness )			# 选择最近的一个友好目标
		shortcutMgr.setHandler( "COMBAT_NAIL_NEAR_TEAMMATE", self.__nailTeammate )			# 选择最近一个队友
		shortcutMgr.setHandler( "COMBAT_NAIL_FORWARD_TEAMMATE", self.__nailForeTeammate )	# 选择上一个队友
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE1", self.__nailTeammate1 )				# 选择第二个队友
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE2", self.__nailTeammate2 )				# 选择第三个队友
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE3", self.__nailTeammate3 )				# 选择第四个队友
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE4", self.__nailTeammate4 )				# 选择第一个队友
		shortcutMgr.setHandler( "COMBAT_NAIL_MY_PET", self.__nailMyPet )					# 选择自己的宠物
		shortcutMgr.setHandler( "COMBAT_NAIL_TARGET_OF_TARGET", self.__nailTargetOfTarget )	# 选择目标的目标

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = TargetMgr()
		return SELF.__inst

	def bindTargetCheck( self, target ) :
		"""
		绑定目标合法性检查
		"""
		if target is None :					# 空目标
			return False
		if not target.selectable :			# 不可选择目标
			return False
		if not target.getVisibility() :		# 目标不可见
			return False
		if getattr( target, "flags", 0 ) != 0 and not self.isRoleTarget( target ): 
			if target.hasFlag(csdefine.ENTITY_FLAG_CAN_NOT_SELECTED):								# 有不被角色鼠标选择标识
				return False
		return True

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __notifyServer( self, targetID ) :
		"""
		通知服务器选中目标
		"""
		player = BigWorld.player()
		if hasattr( player.cell, "changeTargetID" ) :
			player.cell.changeTargetID( targetID )

	def __bindTarget( self, target ) :
		"""
		内部绑定一个目标
		"""
		if not self.bindTargetCheck( target ) :
			return False

		if self.isVehicleTarget( target ) :								# 如果目标是骑宠
			target = target.getHorseMan()								# 则把目标转换为骑宠的主人

		oldTarget = self.getTarget()									# 记录下上一个目标
		self.__target = weakref.ref( target )							# 更换为新的目标
		if oldTarget and oldTarget != target :							# 如果上一个目标存在
			oldTarget.onLoseTarget()									# 则，触发上一个目标的失去选中回调
			ECenter.fireEvent( "EVT_ON_TARGET_UNBINDED", target )
		target.onBecomeTarget()											# 并触发新目标的选中回调
		self.__notifyServer( target.id )								# 通知服务器，目标改变

		if not isinstance( target.model, BigWorld.PyModelObstacle ):	# 静态模型不能添加选择光圈，否则客户端会崩溃（真正显示的是 target.models[0]。yk－－2008-7-8 ）
			bindTarget = target
			if hasattr( target, "emptyModel" ) and target.emptyModel:	# 死亡光圈处理
				bindTarget = target.emptyModel
				texture = UnitSelect().getTexture( target )
				UnitSelect().setTargetTexture( texture )
			UnitSelect().setTarget( bindTarget )						# 显示光圈
		ECenter.fireEvent( "EVT_ON_TARGET_BINDED", target )

		if self.isNPCTarget( target ) :									# 如果选中目标是 NPC
			rds.helper.courseHelper.interactive( "dianjiNPC_caozuo" )	# 则，触发第一次点击 NPC 帮助提示
		elif self.isRoleTarget( target ) :								# 如果选中的目标是角色
			rds.helper.courseHelper.interactive( "xuanzewanjia_caozuo" )# 则，触发第一次点击角色帮助提示
		elif self.isMonsterTarget( target ) :							# 如果选中的目标是怪物
			rds.helper.courseHelper.interactive( "xuanzeguaiwu_caozuo" )# 则，触发第一次点击怪物帮助提示
		return True


	# -------------------------------------------------
	@staticmethod
	def __isEntityInView( entID ) :
		"""
		判断指定的 entity 是否在相机视区内
		"""
		entity = BigWorld.entity( entID )
		if entity is None : return False
		x, y, z = utils.world2RScreen( entity.position )
		return x > -1 and x < 1 and y > -1 and y < 1

	def __bindEntityInList( self, entList, index ) :
		"""
		绑定指定 entity 列表中的指定索引的目标，绑定成功则返回 True，否则返回 False
		"""
		if index >= len( entList ) or \
			not self.__isEntityInView( entList[index] ) :			# 如果已经遍历完候选列表，或指定索引中的敌人已经离开了相机视野
				return False
		entID = entList[index]
		return self.__bindTarget( BigWorld.entity( entID ) )


	# ----------------------------------------------------------------
	# private shortcut implementer
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_ENEMY（自动选择最近的一个怪物）
	# -------------------------------------------------
	def __pickUpItem( self, item ) :
		"""
		捡起掉落物品
		"""
		def closedTarget( success ) :										# 靠近掉落物品处后的回调
			if success : player.startPickUp( item )

		space = 3.0
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_DEAD: return
		if player.affectAfeard : return										# 如果角色处于狂乱状态，不能自行走动
		ppos = player.position
		ipos = item.position
		dist = ppos.distTo( ipos )											# 角色与物品的距离
		if dist <= space :													# 如果小于 3 米
			player.startPickUp( item )										# 则，直接捡起物品
		else :
			pos = csarithmetic.getSeparatePoint3( ipos, ppos, space )
			player.moveTo( pos, closedTarget )

	def __talkWithTarget( self, target ) :
		"""
		与目标对话
		"""
		def clsedTarget( player, target, success ) :
			if not success : return											# 如果靠近对话目标失败，则返回
			if self.getTarget() == target :									# 如果中途没改变对话目标
				GUIFacade.gossipHello( target )								# 则进行对话
				rds.helper.courseHelper.interactive( "NPCjiaohu_caozuo" )	# 触发“与NPC对话”的过程帮助

		player = BigWorld.player()
		dist = player.position.distTo( target.position )
		space = csconst.COMMUNICATE_DISTANCE 								# 与对话目标之间的可对话距离
		if hasattr( target, "getRoleAndNpcSpeakDistance" ) :				# add by gjx 2009-4-2
			space = target.getRoleAndNpcSpeakDistance()						# 这里 -2 是为了防止角色离NPC距离比对话距离远一点点的时候，对话框会一出现就消失的问题>>> 取消减2操作，有些NPC四周有不可逾越的障碍，减2可能会导致走不到NPC身边，例如变身小丑。
		if dist < space :													# 如果在可对话距离内
			BigWorld.player().gossipVoices = 0
			GUIFacade.gossipHello( target )									# 则直接进行对话
#			if player.soundPriority > 0: return									#角色话优先级大于0，则不播放默认语音
#			self.__playNPCVoice( target )
		else :																# 否则
			dec = min( 2, space * 0.8 )
			space -= dec													# 缩短跟NPC的实际距离，保证能跑到NPC对话距离之内
			player.pursueEntity( target, space, clsedTarget )				# 跑到目标跟前再进行对话。

	def __playNPCVoice( self, target ):
		"""
		播放NPC发音
		"""
		if target.voiceBan:
			return
		model = target.getModel()
		if model is None:
			return
		voices = rds.npcVoice.getClickVoice( int(target.className) )
		if len( voices ) <= 0:
			return
		voice = random.choice( voices )
		rds.soundMgr.playVocality( voice, model )
		try:
			target.setVoiceDelate()
		except:
			return

	def __viewVend( self, target ) :
		"""
		察看角色摆摊物品
		"""
		def endPursue( player, target, success ) :							# 靠近结束回调
			if success :													# 如果靠近成功
				player.vend_buyerQueryInfo( target.id )						# 则察看目标摆摊

		player = BigWorld.player()
		if player.position.flatDistTo( target.position ) > \
			csconst.COMMUNICATE_DISTANCE:									# 如果距离过远，则先走过去
				dec = min( 2, csconst.COMMUNICATE_DISTANCE * 0.8 )
				space = csconst.COMMUNICATE_DISTANCE - dec
				player.pursueEntity( target, space, endPursue )				# 靠近摆摊玩家
		else :
			player.vend_buyerQueryInfo( target.id )							# 如果在交互距离内，则直接察看对方摆摊

	def __pickFruit( self, target ):
		"""
		拾取魅力果实
		"""
		def closedTarget( success ) :										# 靠近掉落物品处后的回调
			if success : player.pickFruit( target.id )

		space = 3.0
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_DEAD: return
		if player.affectAfeard : return										# 如果角色处于狂乱状态，不能自行走动
		ppos = player.position
		ipos = target.position
		dist = ppos.distTo( ipos )											# 角色与物品的距离
		if dist <= space :													# 如果小于 3 米
			player.pickFruit( target.id )									# 则，直接捡起物品
		else :
			pos = csarithmetic.getSeparatePoint3( ipos, ppos, space )
			player.moveTo( pos, closedTarget )

	def __closeTarget( self ) :
		"""
		选择/靠近目标
		注：第一次触发时，绑定鼠标击中的目标，第二次触发时，靠近目标
		"""
		target = BigWorld.target.entity
		if target is None : return False

		player = BigWorld.player()
		oldTarget = self.getTarget()										# 记录下原来的目标

		if self.isDropItemTarget( target ) :								# 如果目标是掉落物品
			self.__pickUpItem( target )										# 则捡起物品
		elif self.isDropBoxTarget( target ):								# 如果目标是掉落箱子
			self.__pickUpItem( target )										# 则，捡起物品
			self.bindTarget( target )										# 并绑定新的目标（问：为什么还要再次绑定他？hyw－－2009.06.13）
		elif self.isCollectPointTarget( target ):							# 如果是采集点，一点就触发 by 姜毅
			self.bindTarget( target )
			self.__talkWithTarget( target )
		elif oldTarget != target :											# 如果第一次点击目标
			self.bindTarget( target )										# 则，绑定新的目标
		elif self.isFruitTree( target ):
			self.__pickFruit( target )
		elif self.isDialogicTarget( target ) :								# 如果目标是可对话的
			self.__talkWithTarget( target )									# 则，与目标对话
		elif self.isEnemyTarget( target ) :									# 如果是可攻击目标
			if player.isPursueState():
				player.cancelAttackState()
			player.onLClickTargt()											# 则，对目标发动攻击
		elif self.isRoleTarget( target ) and \
			target.state == csdefine.ENTITY_STATE_VEND :					# 如果是处于摆摊状态下的角色（这是从 Tact 中原版复制过来的，这个判断很不好）
				self.__viewVend( target )
		elif self.isDanceSeatTarget( target ):  							# 如果是舞厅中的坐位
			player.canGetDancePosition( target.locationIndex )
		target.onTargetClick( player )										# 触发 target 被点击的回调
		return True

	# -------------------------------------------------
	# FIXED_SPELL_TARGET（直接攻击鼠标指定的敌人）
	# -------------------------------------------------
	def __spellTarget( self ) :
		"""
		直接攻击目标
		"""
		target = BigWorld.target.entity
		player = BigWorld.player()
		if target is None : return False									# 没有目标

		if self.isVehicleTarget( target ) :									# 如果目标是骑宠
			target = target.getHorseMan()									# 则，更换目标为其主人
		if player.queryRelation( target ) == csdefine.RELATION_ANTAGONIZE :	# 是否是敌对关系的目标
			self.bindTarget( target )										# 绑定新的目标
			player.onRClickTargt()											# 发起攻击
			return True
		return False

	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_ENEMY（自动选择最近的一个敌人）
	# -------------------------------------------------
	@staticmethod
	def __isNailEnemy( enemy ) :
		"""
		判断指定的敌人是否是自动选择时感兴趣的敌人
		"""
		player = BigWorld.player()
		if not TargetMgr.__isEntityInView( enemy.id ) : return False
		if not enemy.getVisibility() : return False											# 目标不可见
		if enemy.viewProjectionCull(): return False											# 被摄像机视野裁剪
		if getattr( enemy, "flags", 0 ) != 0 and not TargetMgr.isRoleTarget( enemy ):
			if enemy.hasFlag(csdefine.ENTITY_FLAG_CAN_NOT_SELECTED):
				return False

		if player.state == csdefine.ENTITY_STATE_RACER and TargetMgr.isRoleTarget( enemy ):
			# 赛马时可以随时选择角色
			return True

		if enemy.isEntityType( csdefine.ENTITY_TYPE_PET ) :									# 判断是否为宠物，
			enemy = enemy.getOwner()														# 是的话把目标转接给主人来做条件判断
			if enemy is None : return False 												# 找不到该宠物的主人 不能选择

		if player.qieCuoState == csdefine.QIECUO_READY or player.qieCuoState == csdefine.QIECUO_FIRE:  #处于切磋状态只TAB对方玩家或宠物
			if hasattr( enemy, "id" ) and player.qieCuoTargetID == enemy.id:
				return True
			else:
				return False

		if not ( player.canPk( enemy ) or TargetMgr.isMonsterTarget( enemy ) ):
			return False

		return TargetMgr.isEnemyTarget( enemy )

	def __nailEnemy( self ) :
		"""
		盯上离我最近的一个敌人
		"""
		player = BigWorld.player()
		isNewList = False														# 记录是否是重新搜索的候选列表
		if len( self.__nearEnemyList ) == 0 :
			enemys = player.entitiesInRange( csconst.ROLE_AOI_RADIUS, self.__isNailEnemy )
			self.__nearEnemyList = [ent.id for ent in enemys]
			isNewList = True
		ecount = len( self.__nearEnemyList )									# 候选列表中敌人的数量
		if ecount == 0 : return													# 如果没有候选敌人，则返回

		currTarget = self.getTarget()
		if isNewList or not currTarget or \
			currTarget.id not in self.__nearEnemyList :							# 如果候选列表是新生成的 或者 如果当前没有选中目标 或者 当前目标不在选中列表中
				if not self.__bindEntityInList( self.__nearEnemyList, 0 ) :		# 则，绑定列表中的第一个
					self.__nearEnemyList = []									# 则，清空候选列表
					self.__nailEnemy()											# 并重新刷新列表（注意：这里不会存在死递归）
		else :																	# 如果当前选中目标在候选列表中
			index = self.__nearEnemyList.index( currTarget.id )					# 则，计算当前目标在候选列表中的位置
			if not self.__bindEntityInList( self.__nearEnemyList, index + 1 ) :	# 并选中下一个目标
				self.__nearEnemyList = []										# 则，清空候选列表
				self.__nailEnemy()												# 并重新刷新列表（注意：这里不会存在死递归）

	# -------------------------------------------------
	# COMBAT_NAIL_FORWARD_ENEMY（自动选择前一个敌人）
	# -------------------------------------------------
	def __nailForeEnemy( self ) :
		"""
		选择目标列表中前一个敌人
		"""
		target = self.getTarget()
		if target is None : return													# 如果当前没有目标，则没有前一个可言
		if target.id not in self.__nearEnemyList : return							# 当前目标不在候选列表中，则意味着当前的候选列表已经废掉
		idx = self.__nearEnemyList.index( target.id ) - 1							# 当前目标在候选列表中的位置
		if idx <= 0 : return														# 当前目标已经是最前面一个
		targetID = self.__nearEnemyList[idx]
		target = BigWorld.entity( targetID )
		self.__bindTarget( target )

	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_KINDNESS（选择最近的一个 NPC）
	# -------------------------------------------------
	def __nailKindness( self ) :
		"""
		选择最近的一个 NPC
		"""
		player = BigWorld.player()
		isNewList = False															# 记录是否是重新搜索的候选列表
		if len( self.__nailKindnessList ) == 0 :
			verifier = lambda ent : self.isKindlyTarget( ent ) and ent.getVisibility()
			enemys = player.entitiesInRange( csconst.ROLE_AOI_RADIUS, verifier )
			self.__nailKindnessList = [ent.id for ent in enemys]
			isNewList = True
		ecount = len( self.__nailKindnessList )										# 候选列表中敌人的数量
		if ecount == 0 : return														# 如果没有候选敌人，则返回

		currTarget = self.getTarget()
		if isNewList or not currTarget or \
			currTarget.id not in self.__nailKindnessList :							# 如果候选列表是新生成的 或者 如果当前没有选中目标 或者 当前目标不在选中列表中
				if not self.__bindEntityInList( self.__nailKindnessList, 0 ) :		# 则，绑定列表中的第一个
					self.__nailKindnessList = []									# 则，清空候选列表
					self.__nailEnemy()												# 并重新刷新列表（注意：这里不会存在死递归）
		else :																		# 如果当前选中目标在候选列表中
			index = self.__nailKindnessList.index( currTarget.id )					# 则，计算当前目标在候选列表中的位置
			if not self.__bindEntityInList( self.__nailKindnessList, index + 1 ) :	# 并选中下一个目标
				self.__nailKindnessList = []										# 则，清空候选列表
				self.__nailEnemy()													# 并重新刷新列表（注意：这里不会存在死递归）

	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_TEAMMATE（自动选择最近一个队友）
	# -------------------------------------------------
	def __nailTeammate( self ) :
		"""
		选择最近一个队友
		"""
		player = BigWorld.player()
		isNewList = False															# 记录是否是重新搜索的候选列表
		if len( self.__nearTeammateList ) == 0 :
			verifier = lambda ent : self.isTeammateTarget( ent ) and \
				ent != player and ent.getVisibility()
			teammates = player.entitiesInRange( csconst.ROLE_AOI_RADIUS, verifier )
			self.__nearTeammateList = [ent.id for ent in teammates]
			isNewList = True
		ecount = len( self.__nearTeammateList )										# 候选列表中敌人的数量
		if ecount == 0 : return														# 如果没有候选敌人，则返回

		currTarget = self.getTarget()
		if isNewList or not currTarget or \
			currTarget.id not in self.__nearTeammateList :							# 如果候选列表是新生成的 或者 如果当前没有选中目标 或者 当前目标不在选中列表中
				if not self.__bindEntityInList( self.__nearTeammateList, 0 ) :		# 则，绑定列表中的第一个
					self.__nearTeammateList = []									# 则，清空候选列表
					self.__nailEnemy()												# 并重新刷新列表（注意：这里不会存在死递归）
		else :																		# 如果当前选中目标在候选列表中
			index = self.__nearTeammateList.index( currTarget.id )					# 则，计算当前目标在候选列表中的位置
			if not self.__bindEntityInList( self.__nearTeammateList, index + 1 ) :	# 并选中下一个目标
				self.__nearTeammateList = []										# 则，清空候选列表
				self.__nailEnemy()													# 并重新刷新列表（注意：这里不会存在死递归）

	# -------------------------------------------------
	# COMBAT_NAIL_FORWARD_TEAMMATE（自动选择前一个敌人）
	# -------------------------------------------------
	def __nailForeTeammate( self ) :
		"""
		选择目标列表中前一个敌人
		"""
		target = self.getTarget()
		if target is None : return
		if target.id not in self.__nearTeammateList : return
		idx = self.__nearTeammateList.index( target.id ) - 1
		if idx <= 0 : return
		targetID = self.__nearTeammateList[idx]
		target = BigWorld.entity( targetID )
		self.__bindTarget( target )

	# -------------------------------------------------
	# COMBAT_NAIL_TEAMMATE...（按索引选择队友）
	# -------------------------------------------------
	def __nailTeammate1( self ) :
		"""
		选择第一个队友
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) == 0 : return
		teammate = BigWorld.entity( ids[0] )
		if not teammate : return
		self.bindTarget( teammate )

	def __nailTeammate2( self ) :
		"""
		选择第二个队友
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) < 2 : return
		teammate = BigWorld.entity( ids[1] )
		if not teammate : return
		self.bindTarget( teammate )

	def __nailTeammate3( self ) :
		"""
		选择第三个队友
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) < 3 : return
		teammate = BigWorld.entity( ids[2] )
		if not teammate : return
		self.bindTarget( teammate )

	def __nailTeammate4( self ) :
		"""
		选择第四个队友
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) < 4 : return
		teammate = BigWorld.entity( ids[3] )
		if not teammate : return
		self.bindTarget( teammate )

	# -------------------------------------------------
	# COMBAT_NAIL_MY_PET（选择自己的宠物）
	# -------------------------------------------------
	def __nailMyPet( self ) :
		"""
		选择自己的宠物
		"""
		pet = BigWorld.player().pcg_getActPet()
		if pet is None : return
		self.bindTarget( pet )

	# -------------------------------------------------
	# COMBAT_NAIL_TARGET_OF_TARGET（选择当前目标的目标）
	# -------------------------------------------------
	def __nailTargetOfTarget( self ) :
		"""
		选择当前目标的目标
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target is None : return											# 玩家没有目标
		if not hasattr( target, "targetID" ) : return						# 目标没有目标属性
		targetOfTarget = BigWorld.entities.get( target.targetID, None )		# 获取目标的目标
		if targetOfTarget is None : return									# 如果目标没有目标，返回
		if targetOfTarget == target : return								# 如果目标的目标是自己，返回
		self.bindTarget( targetOfTarget )									# 绑定目标为当前目标的目标


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getTarget( self ) :
		"""
		获取当前绑定的目标 entity
		"""
		target = None
		if self.__target : target = self.__target()
		if target is not None and not target.inWorld :
			self.__target = None
			return None
		return target

	def bindTarget( self, entity ) :
		"""
		绑定一个目标 entity
		"""
		if not rds.statusMgr.isInWorld() : return
		assert entity is not None
		if self.__bindTarget( entity ) :
			self.__nearEnemyList = []
			self.__nailKindnessList = []
			self.__nearTeammateList = []

	def unbindTarget( self, entity = None ) :
		"""
		如果传入的 entity 为 None，则去掉当前目标，如果当前绑定的目标与传入的目标不一致，则不做任何事情
		"""
		if not rds.statusMgr.isInWorld() : return False
		if self.getTarget() == None:
			return False
		if entity is None or entity == self.getTarget() :
			if self.getTarget():
				self.getTarget().onLoseTarget()
			self.__target = None
			self.__notifyServer( 0 )
			UnitSelect().detachTarget()
			ECenter.fireEvent( "EVT_ON_TARGET_UNBINDED", entity )
			self.__nearEnemyList = []
			self.__nailKindnessList = []
			self.__nearTeammateList = []
			return True
		return False

	def talkWithTarget( self, target ):
		"""
		调用此方法将会把对话目标绑定为当前目标
		"""
		if target is None: return
		self.bindTarget( target )							# 绑定为当前目标
		self.__talkWithTarget( target )

	# -------------------------------------------------
	@staticmethod
	def isRoleTarget( target ) :
		"""
		判断指定目标是否是角色
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_ROLE )

	@staticmethod
	def isPetTarget( target ) :
		"""
		判断指定目标是否是宠物
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_PET )

	@staticmethod
	def isMonsterTarget( target ) :
		"""
		判断指定目标是否是怪物
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.utype in Const.ATTACK_MOSNTER_LIST

	@staticmethod
	def isNPCTarget( target ) :
		"""
		判断指定目标是否是 NPC
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_NPC )

	@staticmethod
	def isDropItemTarget( target ) :
		"""
		判断指定目标是否是掉落物品
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_DROPPED_ITEM )

	@staticmethod
	def isDropBoxTarget( target ) :
		"""
		判断指定目标是否是掉落物品
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_DROPPED_BOX ) or target.isEntityType( csdefine.ENTITY_TYPE_MONSTER_ATTACK_BOX )

	@staticmethod
	def isVehicleTarget( target ) :
		"""
		判断指定目标是否是掉落物品
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_VEHICLE )

	@staticmethod
	def isDanceSeatTarget( target ):
		"""
		判断指定目标是否是舞厅中坐位
		"""
		return target.__class__.__name__ == "DanceSeat"

	# ---------------------------------------
	@staticmethod
	def isTeammateTarget( target ) :
		"""
		判断指定的目标是否是队友
		"""
		return BigWorld.player().isTeamMember( target.id )

	@staticmethod
	def isEnemyTarget( target ) :
		"""
		判断指定目标是否是敌对目标
		"""
		# 如果选择目标是骑宠 则转化为主人 by姜毅
		# 防止类型获取上出现突然的空类型（玩家因某些错误消失）
		try:
			if target.getEntityType() == csdefine.ENTITY_TYPE_VEHICLE:					# 如果目标是骑宠
				target = target.getHorseMan()
		except:
			return False
		return BigWorld.player().queryRelation( target ) == csdefine.RELATION_ANTAGONIZE

	@staticmethod
	def isKindlyTarget( target ) :
		"""
		判断指定目标是否是友好目标
		"""
		if TargetMgr.isNPCTarget( target ) :
			return True
		elif TargetMgr.isRoleTarget( target ) or \
			TargetMgr.isPetTarget( target ) :
				return BigWorld.player().queryRelation( target ) == csdefine.RELATION_NEUTRALLY
		return False

	@staticmethod
	def isDialogicTarget( target ) :
		"""
		判断指定目标是否是可对话目标
		"""
		if TargetMgr.isRoleTarget( target ):
			return False
		return target.hasFlag( csdefine.ENTITY_FLAG_SPEAKER )


	@staticmethod
	def isSelfDartTarget( target ) :
		"""
		判断指定目标是否是角色
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) and ( target.ownerID == BigWorld.player().id )

	@staticmethod
	def isCollectPointTarget( target ) :
		"""
		判断指定目标是否是采集点 by 姜毅
		"""
		return target.getEntityType() == csdefine.ENTITY_TYPE_COLLECT_POINT

	@staticmethod
	def isFruitTree( target ):
		"""
		目标是否魅力果树
		"""
		return target.getEntityType() == csdefine.ENTITY_TYPE_FRUITTREE

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
targetMgr = TargetMgr.instance()

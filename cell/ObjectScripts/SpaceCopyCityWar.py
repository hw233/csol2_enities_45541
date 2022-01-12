# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.2 2008-08-28 00:52:47 kebiao Exp $

"""
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csstatus
import csdefine
import random
import time
import csconst
import Const
from bwdebug import *
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.SkillLoader import g_skills

WAR_TIMER_CHECK_OVER 	 = 100	# 检测战争是否结束
WAR_TIMER_QUEST			 = 104	# 战场任务发放
WAR_TIMER_CHILD_MONSTER	 = 105	# 战场小怪刷新

BOSS_NAME = { False : cschannel_msgs.TONGCITYWAR_SHOU_FANG_JIANG_LING, True : cschannel_msgs.TONGCITYWAR_GONG_FANG_JIANG_LING }

class SpaceCopyCityWar( SpaceCopy ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		# 战场房间级别
		self.roomLevel = section[ "Space" ][ "roomLevel" ].asInt
		self.roomName  = section[ "Space" ][ "roomName" ].asString
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt

		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )

		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )

		if self.roomLevel == 1:
			data = section[ "Space" ][ "defend_playerEnterPoint" ]
			pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
			self.defend_playerEnterPoint = ( pos, direction )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		# 房间等级1级为决赛房间
		if self.roomLevel > 0:
			self.initFinal( selfEntity )

	def initFinal( self, selfEntity ):
		# 决赛初始化
		if not selfEntity.params.has_key( "defend" ):
			return
		pass

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'tongDBID' : entity.tong_dbID, "ename" : entity.getName(), "dbid" : entity.databaseID }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "ename" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		packDict = SpaceCopy.packedSpaceDataOnLeave( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "ename" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		buff = g_skills[ 122155001 ].getBuffLink( 0 ).getBuff()	# 战场逃离惩罚buff
		if entity.tong_grade <= 0 or entity.tong_dbID <= 0:
			return csstatus.SPACE_MISS_NOTTONG
		elif entity.level < self.enterLimitLevel:
			return csstatus.FAMILY_NO_WAR_LEVEL
		elif len( entity.findBuffsByBuffID( buff.getBuffID() ) ) > 0:
			return csstatus.TONG_CITY_WAR_ESCAPE
		return csstatus.SPACE_OK

	def getAllSpaceEntities( self, selfEntity ):
		"""
		16:41 2011-3-3 by wsf
		如果在脚本中使用类似于“for entity in BigWorld.entities.values(): ...”的代码，则服务器有一定的概率（通常是服务器越忙概率越高）会宕机，
		这个问题至今仍存在，按bigworld的话来说，为了效率的原因，不建议我们这样使用，也不考虑修改这个问题。
		当前重写帮会城战规则时间不允许，风险也大，暂时采用临时解决方案来解决此问题，使用entitiesInRangeExt来搜索一定范围的entity，需保证此范围>=当前副本面积
		"""
		return selfEntity.entitiesInRangeExt( 800, None, selfEntity.position )

	def kickAllPlayer( self, selfEntity ):
		"""
		将副本所有玩家踢出
		"""
		for mailbox in selfEntity._players:
			if BigWorld.entities.has_key( mailbox.id ):
				BigWorld.entities[ mailbox.id ].tong_onCityWarOver()
			else:
				mailbox.cell.tong_onCityWarOver()

	def findBossID( self, selfEntity ):
		"""
		寻找副本里的守方BOSSID
		我们假设副本在同一个cell
		"""
		for e in self.getAllSpaceEntities( selfEntity ):
			if e.spaceID == selfEntity.spaceID and e.__class__.__name__ == "BossCityWar":
				return e.id
		return 0

	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		if userArg == WAR_TIMER_CHECK_OVER:
			if selfEntity.isOverCityWar():
				self.spellCommonBuffAllPlayer( selfEntity, 122156002 )
				selfEntity.cancel( id )
				self.kickAllPlayer( selfEntity )
		else:
			SpaceCopy.onTimer( self, selfEntity, id, userArg )

	def onCityWarMemberLeave( self, selfEntity, memberID ):
		"""
		帮会家族有成员离退出或被踢出家族 我们在这里需要判断副本中是否有该成员
		如果 有 则把他传出去 在副本中是不允许解散的 所以不会担心解散问题
		"""
		for mailbox in selfEntity._players:
			if memberID == mailbox.id:	# 既然都不是帮会的人了  那么他应该返回城市复活点
				player = self.getMBEntity( mailbox )
				player.tong_leaveCityWar()

	def getMBEntity( self, baseMailbox ):
		"""
		通过mailbox转换到一个entity
		"""
		e = baseMailbox.cell
		if BigWorld.entities.has_key( baseMailbox.id ):
			e = BigWorld.entities[ baseMailbox.id  ]
		return e

	def isRightBossLive( self, selfEntity ):
		"""
		是否是防守方boss活着
		"""
		return selfEntity.queryTemp( "currentBossIsRight", False )

	def setBossLive( self, selfEntity, isRight ):
		selfEntity.setTemp( "currentBossIsRight", isRight )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		player = self.getMBEntity( baseMailbox )
		player.setTemp( "lastPkMode", player.pkMode )
		player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )	# 强制玩家进入帮会pk 状态
		player.lockPkMode()														# 锁定pk模式，不能设置

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onLeaveCityWarSpace()
		player = self.getMBEntity( baseMailbox )
		player.unLockPkMode()		# 解锁pk模式
		player.setSysPKMode( 0 )	# 解除默认pkMode

		if not selfEntity.isOverCityWar():	# 如果战争没有结束时离开，加上惩罚buff，2分钟内不允许再进入
			player.spellTarget( 122155001, player.id )

	def onBossDied( self, selfEntity ):
		"""
		战场 将领或者统帅死亡
		"""
		if selfEntity.isOverCityWar():
			return

		# 统帅被击败了
		selfEntity.setTemp( "isBossDie", True )
		selfEntity.base.closeCityWarRoom()
		self.spellCommonBuffAllPlayer( selfEntity, 122156002 )

	def closeCityWarRoom( self, selfEntity ):
		"""
		提前结束掉某场战争 由tongmanager 关闭所有房间
		副本里面的守方统帅提前被击败
		"""
		selfEntity.setTemp( "isCurrentCityWarOver", True )
		self.kickAllPlayer( selfEntity )
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )

	def spellCommonBuffAllPlayer( self, selfEntity, skillID ):
		"""
		对所有人施放本战场内的公共BUFF效果
		"""
		for mailbox in selfEntity._players:
			if BigWorld.entities.has_key( mailbox.id ):
				BigWorld.entities[ mailbox.id ].spellTarget( skillID, mailbox.id )
			else:
				mailbox.cell.spellTarget( skillID, mailbox.id )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		DEBUG_MSG( "Role %i kill a enemy." % role.id )
		# 杀人者找不到发生几率非常小，可以忽略这次记录
		if not killer:
			return

		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				return
			killer = owner.entity

		if killer.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ):
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.belong, 0, role.tong_dbID, role.databaseID )
		else:
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.tong_dbID, killer.databaseID, role.tong_dbID, role.databaseID )
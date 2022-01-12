# -*- coding: gb18030 -*-

# $Id: AIInterface.py,v 1.27 2008-07-30 01:26:44 kebiao Exp $

import csstatus
import csdefine
import Const
import BigWorld
import ECBExtend
import random
import time
from bwdebug import *
from Resource.AI.AIBase import AIBase
from optimize_with_cpp.interface import AIInterface_func as AI_CPP_OPTIMIZE
import Resource.AIData
g_aiDatas = Resource.AIData.aiData_instance()

class AIInterface:
	"""
	entity AI 接口
	"""
	def __init__( self ):
		"""
		初始化属性
		"""
		aiDefLevel = self.getScript().attrAIDefLevel
		self.attrAINowLevel = aiDefLevel
		self.attrAINowLevelTemp = self.attrAINowLevel
		self.setDefaultAILevel( aiDefLevel )

	def getAIDataMapping( self ):
		"""
		AI数据类型影射
		"""
		d = {
				csdefine.AI_TYPE_GENERIC_FREE	: self.attrFreeStateGenericAIs,
				csdefine.AI_TYPE_GENERIC_ATTACK : self.attrAttackStateGenericAIs,
				csdefine.AI_TYPE_SCHEME 		: self.attrSchemeAIs,
				csdefine.AI_TYPE_SPECIAL 		: self.attrSpecialAIs,
			}
		return d

	def addAI( self, level, ai, type ):
		"""
		define method.
		向该entity添加 ai
		@param ai  : ai of instance
		@param type: csdefine.AI_TYPE_SCHEME ...
		@param level: 设定此AI的运行级别, 既 AI系统在此级别时才会运行该AI
		"""
		if type == csdefine.AI_TYPE_GENERIC_FREE:
			self.noFightStateAICount += 1
		else:
			self.fightStateAICount += 1

		aimapping = self.getAIDataMapping()
		if isinstance( ai, AIBase ):
			if aimapping[ type ].has_key( level ):
				aimapping[ type ][ level ].append( ai )
			else:
				aimapping[ type ][ level ] = [ ai ]
		else:
			ERROR_MSG( "addAI only receive an AIBase of instance." )

	def removeAI( self, level, aid, type ):
		"""
		define method.
		删除一个ai（通过ai的id和级别以及类别来删除）
		@param aid: ai of id
		@param type: csdefine.AI_TYPE_SCHEME ...
		"""
		ais = self.getAIDataMapping()[ type ].get( level )
		if ais:
			for idx, ai in enumerate( ais ):
				if ai.getID() == aid:
					ais.pop( idx )
					if type == csdefine.AI_TYPE_GENERIC_FREE:
						self.noFightStateAICount -= 1
					else:
						self.fightStateAICount -= 1
					return

	def addEventAI( self, event, level, ai ):
		"""
		define method.
		向该entity添加 ai
		@param ai   : ai of instance
		@param event: 事件
		@param level: 设定此AI的运行级别, 既 AI系统在此级别时才会运行该AI
		"""
		if isinstance( ai, AIBase ):
			if self.triggersTable.has_key( event ):
				if self.triggersTable[ event ].has_key( level ):
					self.triggersTable[ event ][ level ].append( ai )
				else:
					self.triggersTable[ event ][ level ] = [ ai ]
			else:
				self.triggersTable[ event ] = { level : [ ai ] }
		else:
			ERROR_MSG( "addEventAI only receive an AIBase of instance." )

	def removeEventAI( self, event, level, aid ):
		"""
		删除一个事件ai（通过ai的id和级别以及事件来删除）
		@param   aid: ai of id
		@param event: 事件
		"""
		ais = self.triggersTable[ event ].get( level )
		if ais:
			for idx, ai in enumerate( ais ):
				if ai.getID() == aid:
					ais.pop( idx )
					return

	def setDefaultAILevel( self, level ):
		"""
		AI的默认级别
		@param level: 要设置的级别
		@type  level: int8
		"""
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    设置默认等级AI %i to %i"%(  self.attrAIDefLevel, level ), "AI_DEBUG_LOG:setDefaultAILevel ( NPCID %i className %s) ) from %i to %i" % ( self.id, self.className, self.attrAIDefLevel, level ) )
		self.attrAIDefLevel = level

	def setNextRunAILevel( self, level ):
		"""
		设置AI下一次运行的级别
		@param level: 要设置的级别
		@type  level: int8
		"""
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    设置下一等级AI %i to %i"%(  self.attrAINowLevelTemp, level ), "AI_DEBUG_LOG:setNextRunAILevel ( NPCID %i className %s) ) from %i to %i" % ( self.id, self.className, self.attrAINowLevelTemp, level ) )
		self.attrAINowLevelTemp = level

	def getDefaultAILevel( self ):
		"""
		获得 AI的默认级别
		"""
		return self.attrAIDefLevel

	def getNextRunAILevel( self ):
		"""
		获得 AI下一次运行的级别
		"""
		return self.attrAINowLevelTemp

	def getNowAILevel( self ):
		"""
		获得 AI当前运行的级别
		"""
		return self.attrAINowLevel

	def addSAI( self, aid ):
		"""
		设置SAI SAI的意义是在下一次循环时 强制执行此AI
		@param type: AI的类型 如AI_TYPE_GENERIC_FREE
		@param aid: ai of id.
		"""
		if not g_aiDatas.has( aid ):
			ERROR_MSG( "className %s:sai %i not found! please to check in config the ai of file." % ( self.className, aid ) )
			return
		self.saiArray.append( g_aiDatas[ aid ] )

	def insertSAI( self, aid ):
		"""
		插入一条SAI，添加到SAI列表的最前面,优先执行
		"""
		if not g_aiDatas.has( aid ):
			ERROR_MSG( "className %s:sai %i not found! please to check in config the ai of file." % ( self.className, aid ) )
			return
		self.saiArray.insert( 0, g_aiDatas[ aid ] )

	def addEAI( self, aiID ):
		"""
		设置EAI EAI意义是在AI被重置前 永久不再运行
		@param aiID: id
		"""
		if aiID != 0 and not( aiID in self.eaiIDArray ):
			nTitle=getattr(self,"title")
			if nTitle == "debug" or self.queryTemp("debug",0) == 1:
				DEBUG_MSG_FOR_AI( self, "    加入eai: %i"%aiID, "AI_DEBUG_LOG:( NPCID %i className %s) addEAI %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, aiID, self.attrAINowLevel,self.aiTargetID, self.targetID ) )
			self.eaiIDArray.append( aiID )

	def clearAllEAI( self ):
		"""
		清空所有eai记录
		"""
		self.eaiIDArray = []

	def isEAI( self, aid ):
		"""
		判断此aid是否是E级AI
		"""
		return aid in self.eaiIDArray

	def addSAIInst( self, ai, force = False ):
		"""
		直接将一个AI设置为SAI
		@param ai	: ai of instance
		@param force: bool 是否强制设置
		"""
		if not force in self.saiArray: # 不允许重复设置
			return
		self.saiArray.append( ai )

	def setInsertAI( self, ai ):
		"""
		define method.
		设置插入AI实例， 通常由外部设置
		"""
		self.insert_ai = ai

	def doAllAI( self ):
		"""
		主动触发所有AI 主要原因是 某些地方可能需要及时反映，无需等待AItimer
		"""
		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			self.onFightAIHeartbeat_AIInterface_cpp()
		else:
			self.onNoFightAIHeartbeat()

	def onFightAIHeartbeat( self ):
		"""
		战斗状态下AI 的 心跳。

		注意：为提高效率，此脚本方法逻辑已使用c++来实现为onFightAIHeartbeat_AIInterface_cpp，此方法已失效，如果需要修改此方法，请联系wangshufeng。15:01 2012-12-7 by wsf。

		禁止直接编辑该方法，请到下层模块中修改。
		"""
		AI_CPP_OPTIMIZE.onFightAIHeartbeat(self)

	def onNoFightAIHeartbeat( self ):
		"""
		AI 的 心跳
		"""
		if self.noFightStateAICount <= 0:
			return
		elif self.intonating() or self.inHomingSpell():
			return

		# 匹配AI运行等级
		if self.attrAINowLevelTemp != self.attrAINowLevel:
			self.attrAINowLevel = self.attrAINowLevelTemp
		nTitle=getattr(self,"title")
		aiDebug = self.queryTemp("debug",0)
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "开始普通AI", "" )
		# 执行通用AI的循环
		for ai in self.attrFreeStateGenericAIs.get( self.attrAINowLevel, [] ):
			if self.isDestroyed or not self.isReal(): return
			if self.aiCommonCheck( ai ):
				if nTitle == "debug" or aiDebug == 1:
					DEBUG_MSG_FOR_AI( self, "  开始AI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) )  FreeStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
				ai.do( self )
				if nTitle == "debug" or aiDebug == 1:
					DEBUG_MSG_FOR_AI( self, "  结束AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) FreeStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "结束普通AI", "" )
		if self.isDestroyed:
			return

		self.setAITargetID( 0 )					# 清空本轮AI对象, 下一轮由下一轮去设置

	def onSpecialAINotDo( self ):
		"""
		virtual method.
		特殊AI执行失败要做的处理
		"""
		pass

	def aiCommonCheck( self, ai ):
		"""
		AI 的公共判断条件
		禁止直接编辑该方法，请到下层模块中修改。
		"""
		return AI_CPP_OPTIMIZE.aiCommonCheck(self, ai)

	def resetAI( self ):
		"""
		重置AI
		"""
		self.clearAllEAI()
		self.saiArray = []
		self.setInsertAI( None )
		self.fightStartTime = 0.0
		self.aiTargetID = 0
		aimapping = self.getAIDataMapping()
		aiDefLevel = self.getScript().attrAIDefLevel

		# 还原默认AI等级为配置生成的等级
		self.attrAINowLevel = aiDefLevel
		self.attrAINowLevelTemp = aiDefLevel
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ai重置回到0级", "AI_DEBUG_LOG:set ( NPCID %i className %s) )AILevel from %i to %i" % ( self.id, self.className, self.attrAIDefLevel, aiDefLevel ) )
		self.setDefaultAILevel( aiDefLevel )

		# 清空连续AI
		self.comboAIArray = []
		self.comboAIState = False

		for aiItems in aimapping.itervalues():
			for aiList in aiItems.itervalues():
				for ai in aiList:
					ai.reset( self )

		for aiData in self.triggersTable.itervalues():
			for aiList in aiData.itervalues():
				for ai in aiList:
					ai.reset( self )

	def getEventTriTable( self, event ):
		"""
		获取某事件触发的ai表
		@param event: 事件ID
		@return type: success to return the table, fail to return the []
		"""
		if not self.triggersTable.has_key( event ):
			return {}
		return self.triggersTable[ event ]

	def doAllEventAI( self, event ):
		"""
		执行某事件所有AI
		@param event: 事件ID
		"""
		if self.isDestroyed:
			return
		nTitle=getattr(self,"title")
		aiDebug = self.queryTemp("debug",0)
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "******开始事件AI", "" )
		aidata = self.getEventTriTable( event )
		if aidata.has_key( self.attrAINowLevel ):
			for ai in aidata[ self.attrAINowLevel ]:
				if self.isDestroyed or not self.isReal(): return
				if self.aiCommonCheck( ai ):
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "******开始AI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) at event %i, do %i, attrAINowLevel %i" % ( self.id, self.className, event, ai.getID(), self.attrAINowLevel ) )
					ai.do( self )
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "******结束AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) at event %i, do %i, attrAINowLevel %i" % ( self.id, self.className, event, ai.getID(), self.attrAINowLevel ) )
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "******结束事件AI", "" )

	def onAICommand( self, entityID, className, cmd ):
		"""
		< Define Method >
		ai 命令， 由其他单位通知该entity的一个命令，必须有对应的AI来处理该命令，否则不会有影响
		@param entityID : 命令者ID
		@param cmd		: 命令 uint16
		"""
		self.setTemp( "AICommand", ( entityID, className, cmd ) )
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    接收到来自%s的指令%i"%( className, cmd ), "AI_DEBUG_LOG:( NPCID %i className %s) )get a AICommand from ( id:%i, className:%s, cmd:%i ), attrAINowLevel %i" % ( self.id, self.className, entityID, className, cmd, self.attrAINowLevel ) )
		self.doAllEventAI( csdefine.AI_EVENT_COMMAND )

	def sendAICommand( self, entityID, cmd ):
		"""
		ai 命令， 由其他单位通知该entity的一个命令，必须有对应的AI来处理该命令，否则不会有影响
		@param entityID : 命令者ID
		@param cmd		: 命令 uint16
		"""
		try:
			entity = BigWorld.entities[ entityID ]
		except:
			return
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    发送AI指令%i"%cmd, "AI_DEBUG_LOG:( NPCID %i className %s) ) sed a AICommand to ( id:%i, className:%s, cmd:%i ), attrAINowLevel %i" % ( self.id, self.className, entityID, entity.className, cmd, self.attrAINowLevel ) )
		entity.onAICommand( self.id, self.className, cmd )

	def setAITargetID( self, entityID ):
		"""
		define method.
		设置AI当前所选择出的entityID
		"""
		self.aiTargetID = entityID

	def comboAICheck( self ):
		"""
		能否执行连续AI检测,如果能执行，则返回能执行的comboID
		"""
		nTitle=getattr( self, "title" )
		if len( self.getScript().comboAITable ) == 0 or len( self.getScript().comboAITable[ self.attrAINowLevel ] ) == 0:
			return 0

		# 连续AI执行概率
		comboActiveRate = self.getScript().comboActiveRate
		randomRate = random.randint( 0, 100 )
		if comboActiveRate < randomRate:
			if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
				DEBUG_MSG_FOR_AI( self, "能够执行comboAI检测，返回False", "combAI check False, comboActiveRate %f, randomRate %f" % ( comboActiveRate, randomRate ) )
			return 0

		# 检测能执行哪一组AI
		for comboID, item in self.getScript().comboAITable[ self.attrAINowLevel ].iteritems():
			activeRate = item["activeRate"]
			if random.randint( 1, 100 ) <= activeRate:
				return comboID

		return 0

	def addComboAI( self, comboID ):
		"""
		执行连续AI
		"""
		for id, item in self.getScript().comboAITable[ self.attrAINowLevel ].iteritems():
			if id == comboID:
				self.comboAIArray = item["aiDatas"]

	def doComboAI( self, comboID = 0 ):
		"""
		执行连续AI, comboID 不为0表示需要添加连续AI
		"""
		nTitle=getattr( self, "title" )

		if comboID:			# 需要添加连续AI
			self.addComboAI( comboID )
			array = []
			for ai in self.comboAIArray:
				array.append( ai.getID() )
			if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
				DEBUG_MSG_FOR_AI( self, "添加comboAI, comboID %i, array %s" % ( comboID, array ), "%s addcomboAI,comboID %i, array %s" % ( self.className, comboID, array ))

		if len( self.comboAIArray ):
			ai = self.comboAIArray.pop( 0 )
			if self.aiCommonCheck( ai ):
				ai.do( self )
				self.comboAIState = True
				if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
					DEBUG_MSG_FOR_AI( self, "执行comboAI,ai%i" % ( ai.getID() ), "%s, %i do comboAI %i " % ( self.className, self.id, ai.getID() ) )
			else:
				if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
					DEBUG_MSG_FOR_AI( self, "重置comboAI" , "%s, %i reset comboAI" % ( self.className, self.id ) )
				self.comboAIArray = []
				self.comboAIState = False
			if len( self.comboAIArray ) == 0:
				if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
					DEBUG_MSG_FOR_AI( self, "结束comboAI ", " %s, %i finish comboAI " % ( self.className, self.id ) )
		else:
			self.comboAIState = False

# $Log: not supported by cvs2svn $
# Revision 1.26  2008/07/30 01:14:06  kebiao
# fix a bug
#
# Revision 1.25  2008/07/30 01:03:58  kebiao
# ai_timer -> ai_fight_timer
#
# Revision 1.24  2008/07/21 03:51:24  kebiao
# 优化空AI时的消耗
#
# Revision 1.23  2008/07/19 07:44:25  kebiao
# fight_timer --> ai_fight_timer
#
# Revision 1.22  2008/07/09 03:18:05  kebiao
# 增加aiTargetID 重置时为0
#
# Revision 1.21  2008/07/02 07:55:11  kebiao
# 在AI被重置时 临时运行等级也重置为0
#
# Revision 1.20  2008/05/31 03:13:25  kebiao
# 修正AI 在怪物死亡后执行错误
#
# Revision 1.19  2008/05/26 04:18:52  kebiao
# 增加insert_ai 处理外部强行插入 强行执行一件事情
#
# Revision 1.18  2008/05/14 01:10:55  kebiao
# 修正一个打包传输后产生的BUG
#
# Revision 1.17  2008/05/05 07:16:00  kebiao
# 将几出计算量优化了
#
# Revision 1.16  2008/05/04 09:02:31  kebiao
# 改变self.aiTargetID 重置位置
#
# Revision 1.15  2008/04/21 00:59:23  kebiao
# 修改事件循环BUG，修改addAI接口等参数
#
# Revision 1.14  2008/04/19 01:31:29  kebiao
# 默认AI移动到monster自身加载
#
# Revision 1.13  2008/04/18 07:15:39  kebiao
# ADD : setAITargetID
#
# Revision 1.12  2008/04/16 03:41:58  kebiao
# add:onAICommand, sendAICommand
#
# Revision 1.11  2008/04/10 08:51:11  kebiao
# 调整AI第一次反应的速度
#
# Revision 1.10  2008/04/07 08:56:17  kebiao
# 继续调整AI接口功能
#
# Revision 1.1  2008/03/25 07:42:07  kebiao
# 添加AI相关
#
#
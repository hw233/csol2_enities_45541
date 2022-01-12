# -*- coding: gb18030 -*-
#
# $Id: RoleCredit.py,v 1.5 2008-09-02 02:49:05 songpeifang Exp $


import BigWorld
import time
from bwdebug import *
import csdefine
import csconst
import csstatus
import ECBExtend

import SkillTargetObjImpl
from TitleMgr import TitleMgr
from Resource.SkillLoader import g_skills
from FactionMgr import factionMgr						# npc势力配置

g_titleLoader = TitleMgr.instance()



class RoleCredit:
	"""
	角色的声望、称号、荣誉interface
	"""
	def __init__( self ):
		"""
		"""
		# self.prestige
		# self.prestigeSwitch	# 声望开关，UINT32数据，前25位每一位对应一个势力的声望是否开启，1为开启，0为关闭。
		if len( self.prestige ) > 0: return
		self.prestige.initPrestigeDefalut()

	def addPrestige( self, factionID, value ):
		"""
		增加声望

		@param factionID : 势力id
		@type factionID : UINT8
		@param value : 增加的声望值
		@type value : INT32
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		gameYield = self.wallow_getLucreRate()
		if value >=0:
			value = value * gameYield
		#--------- 以上为防沉迷系统的判断 --------#

		if not self.prestige.has_key( factionID ):
			self.prestige.turnOnPrestige( factionID, value )
			self.client.turnOnPrestige( factionID, self.prestige.getPrestige( factionID ) )
			return

		oldprestigeValue = self.prestige.getPrestige( factionID )

		if not self.prestige.addPrestige( factionID, value ):
			self.statusMessage( csstatus.PRESTIGE_UPPER_LIMIT, factionMgr.getName( factionID ) )
			return
		self.client.prestigeUpdate( int( factionID ), value )
		if factionID == 37 or factionID == 38:
			self.updateDartTitle( factionID, self.title == 0 )	# 更新镖局称号
		else:
			self.updateConfigTitle( factionID, oldprestigeValue, self.title == 0 )	# 更新配置称号

		self.onPlayerPrestigeChanged()

	def updateConfigTitle( self, factionID, oldprestigeValue, directSelect ):
		"""
		更新通过配置控制的称号 by姜毅
		"""
		titleID = g_titleLoader.getTitleIDByCredit( factionID, self.prestige.getPrestige( factionID ) )
		if titleID < 0: return
		elif titleID == 0:
			self.checkAndRemoveTitle( factionID, oldprestigeValue )
			return
		self.addTitle( titleID )
		self.checkAndRemoveTitle( factionID, oldprestigeValue )
		if directSelect: self.selectTitle( self.id, titleID )


	def isPrestigeOpen( self, factionID ):
		"""
		玩家是否开启了相应势力的声望
		"""
		return self.prestige.has_key( factionID )


	def getPrestige( self, factionID ):
		"""
		获得对应factionID的势力声望

		@param factionID : 势力id
		@type factionID : STRING
		"""
		if not self.isPrestigeOpen( factionID ):		# 如果玩家还没有开启该势力声望，则开启该势力声望 2008-11-12 gjx
			self.prestige.turnOnPrestige( factionID, 0 )
			self.client.turnOnPrestige( factionID, self.prestige.getPrestige( factionID ) )
		return self.prestige.getPrestige( factionID )


	def requestSelfPrestige( self ):
		"""
		请求发送声望数据到客户端
		"""
		for factionID, value in self.prestige.iteritems():
			self.client.receivePrestige( factionID, value )
		self.client.onInitialized( csdefine.ROLE_INIT_PRESTIGE )


	def getPretigeLevel( self, factionID ):
		"""
		获得对应factionID的势力声望等级

		PRESTIGE_ENEMY				=			1	# 仇敌
		PRESTIGE_STRANGE			=			2	# 冷淡
		PRESTIGE_NEUTRAL			=			3	# 中立
		PRESTIGE_FRIENDLY			=			4	# 友善
		PRESTIGE_RESPECT			=			5	# 尊重
		PRESTIGE_ADMIRE				=			6	# 崇敬
		PRESTIGE_ADORE				=			7	# 崇拜
		"""
		value = self.getPrestige( factionID )
		return value < -3000 and csdefine.PRESTIGE_ENEMY \
			or value < 1    and csdefine.PRESTIGE_STRANGE \
			or value < 3000  and csdefine.PRESTIGE_NEUTRAL \
			or value < 9000  and csdefine.PRESTIGE_FRIENDLY \
			or value < 21000 and csdefine.PRESTIGE_RESPECT \
			or value < 42000 and csdefine.PRESTIGE_ADMIRE \
			or csdefine.PRESTIGE_ADORE


	# --------------------------------------------------------------------
	# about title
	# --------------------------------------------------------------------
	def addTitle( self, titleID ):
		"""
		给玩家增加一个称号

		@param titleID : 称号的ID
		@type titleID : UINT8
		"""
		if titleID in self.titles or titleID == csdefine.TITLE_NONE : return
		titleData = g_titleLoader.getData( titleID )
		order = titleData[ "order" ]
		for title in self.titles[:]:
			if order == g_titleLoader.getOrder( title ):
				self.removeTitle( title )
		self.titles.append( titleID )
		self.client.onTitleAdded( titleID )
		if g_titleLoader.isTimeLimit( titleID ):	# 如果是个有时限的称号，开始计时
			tempTime = titleData[ "limitTime" ] + time.time()
			timerID = self.addTimer( titleData[ "limitTime" ], 0, ECBExtend.TITLE_TIMER_CBID )
			self.titleLimitTime.append( { "titleID":titleID, "time":tempTime, "timerID":timerID } )

	def setTitleLimitTime( self, titleID, limitTime ):
		"""
		设置玩家某一个有时限称号的时限。
		有些称号需要在玩家获得时方能知道多长时间移除，需要在玩家获得称号时设置移除时限。

		@param titleID : 称号的ID
		@type titleID : UINT8
		@param limitTime : 称号的获得时限
		@type limitTime : INT64
		"""
		hasTimeTitle = False
		for tempDict in self.titleLimitTime:
			if tempDict[ "titleID" ] == titleID:
				hasTimeTitle = True
				self.cancel( tempDict[ "timerID" ] )
				tempDict[ "timerID" ] = self.addTimer( limitTime, 0, ECBExtend.TITLE_TIMER_CBID )
				tempDict[ "time" ] = limitTime + time.time()
		if not hasTimeTitle:
			tempDict = {}
			tempDict[ "titleID" ] = titleID
			tempDict[ "timerID" ] = self.addTimer( limitTime, 0, ECBExtend.TITLE_TIMER_CBID )
			tempDict[ "time" ] = limitTime + time.time()
			self.titleLimitTime.append( tempDict )

	def selectTitle( self, srcEntityID, titleID ):
		"""
		Exposed method.
		玩家选择一个称号

		@param titleID : 称号的ID
		@type titleID : UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "self.id != srcEntityID" )
			return
		if titleID == self.title:
			return
		if titleID == 0:	# 取消称号
			self._changeTitle( self.title, titleID, "" )
		if titleID not in self.titles:	# 判断titleID参数是否合法
			HACK_MSG("")
			return
		if g_titleLoader.getSkillID( titleID ) and self.intonating():	# 如果此称号有buff但此时正吟唱别的技能，那么不允许更换称号。
			self.statusMessage( csstatus.TITLE_CANT_CHANGE_SKILL_BUSY )
			return

		oldTitle = self.title
		# 给玩家加上对应的buff，buffID读配置，读配置获得玩家的titleString
		titleType = g_titleLoader.getType( titleID )
		titleName = g_titleLoader.getName( titleID )

		# 可变称号处理，需要到base去取称号数据
		if titleID in[csdefine.TITLE_TEACH_PRENTICE_ID, csdefine.TITLE_ALLY_ID, csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]:
			self.setTemp( "title_isWield", True )
			self.base.sendTitleName( titleID )
			return

		self._changeTitle( oldTitle, titleID, titleName )


	def _changeTitle( self, oldTitle, titleID, titleName ):
		"""
		改变称号，所有改变称号的入口。

		对于一些需要base数据才能生成的称号，可以避免异步问题

		@param oldTitle : 旧称号的ID
		@type oldTitle : UINT16
		@param titleID : 称号的ID
		@type titleID : UINT16
		@param titleName : 称号
		@type titleName : STRING
		"""
		self.titleName = titleName
		self.title = titleID
		if oldTitle != 0:	# 如果旧称号不为空
			# 打断旧称号的buff
			oldSkillID = g_titleLoader.getSkillID( oldTitle )
			if oldSkillID:
				self.clearBuff( [ csdefine.BUFF_INTERRUPT_CHANGE_TITLE ] )

		if titleID == 0:	# 取消选择当前称号，恢复到未选择称号状态
			return

		skillID = g_titleLoader.getSkillID( titleID )
		if skillID:		# 添加当前称号相关buff
			skill = g_skills[ skillID ]
			if skill is None:
				self.statusMessage( csstatus.SKILL_NOT_EXIST )
				return
			target = SkillTargetObjImpl.createTargetObjEntity( self )
			state = skill.useableCheck( self, target )
			if state != csstatus.SKILL_GO_ON:
				self.statusMessage( state )
				return
			skill.use( self, target )


	def removeTitle( self, titleID ):
		"""
		移除玩家的一个称号

		@param titleID : 称号的ID
		@type titleID : UINT8
		"""
		if not titleID in self.titles:
			ERROR_MSG( "Could not remove such title id %i because it does not exist in player( %s )'s titles!" % ( titleID, self.getName() ) )
			return
		self.titles.remove( titleID )
		self.client.onTitleRemoved( titleID )
		if self.title == titleID:
			self._changeTitle( self.title, 0, "" )
		for temp in self.titleLimitTime:
			if temp[ "titleID" ] == titleID:
				self.cancel( temp[ "timerID" ] )
				self.titleLimitTime.remove( temp )
				break


	def onTitleAddTimer( self, controllerID, userData ):
		"""
		添加有时间限制的称号的回调
		"""
		for temp in self.titleLimitTime:
			if temp[ "time" ] - time.time() < 1.0:		# 考虑误差在1秒以内
				self.removeTitle( temp[ "titleID" ] )
				break

	def title_onLogin( self ):
		"""
		玩家上线，重置称号
		"""
		isCurTitle = False					# 是否当前使用的称号到期了
		for temp in self.titleLimitTime:	# 检察称号是否到期
			temp["timerID"] = 0
			if temp[ "time" ] - time.time() < 0.3:		# 考虑误差在0.3秒以内
				if temp["titleID"] == self.title:
					isCurTitle = True
				self.removeTitle( temp[ "titleID" ] )
			else:
				timerID = self.addTimer( temp[ "time" ] - time.time(), 0, ECBExtend.TITLE_TIMER_CBID )
				temp["timerID"] = timerID

		if not self.title or isCurTitle:	# 当前没有选择称号 或者 当前选中的称号到期了，返回
			DEBUG_MSG( "player( %s ) have not wielded title." % ( self.getName() ) )
			return

		# 可变称号处理，需要到base去取称号数据
		if self.title in[csdefine.TITLE_TEACH_PRENTICE_ID, csdefine.TITLE_ALLY_ID, csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID]:
			self.setTemp( "title_isWield", False )
			self.base.sendTitleName( self.title )
		else:
			self.titleName = g_titleLoader.getName( self.title )

	def getDartTitleID( self, factionID, questStyle ):
		"""
		根据玩家的镖局声望得到玩家在镖局中的称号ID
		@param id : 镖局势力的id
		@type id : STRING
		"""
		if questStyle == csdefine.QUEST_TYPE_ROB:
			titleID = [ csdefine.TITLE_NOVICIATE_LANLUHU_X, csdefine.TITLE_NOVICIATE_LANLUHU_C ]
			return titleID[factionID-37]
		if not self.isPrestigeOpen( factionID ):
			titleID = [ csdefine.TITLE_NOVICIATE_NEW_DART_X, csdefine.TITLE_NOVICIATE_NEW_DART_C ]
			return titleID[factionID-37]
		# self.dartRepuValue = self.getPrestige( factionID )		#玩家镖局声望
		titleID = [csdefine.TITLE_NONE, csdefine.TITLE_NONE]

		presLevel_X = self.getPretigeLevel( 37 )
		presLevel_C = self.getPretigeLevel( 38 )
		presLevel = presLevel_X > presLevel_C and presLevel_X or presLevel_C
		factionID = presLevel_X > presLevel_C and 37 or 38
		if presLevel == csdefine.PRESTIGE_NEUTRAL:		#"趟子手"
			titleID = [ csdefine.TITLE_NOVICIATE_CHANGZISHOU_X, csdefine.TITLE_NOVICIATE_CHANGZISHOU_C ]
		if presLevel == csdefine.PRESTIGE_FRIENDLY:		#"新手镖师"
			titleID = [ csdefine.TITLE_NOVICIATE_NEW_DART_X, csdefine.TITLE_NOVICIATE_NEW_DART_C ]
		elif presLevel == csdefine.PRESTIGE_RESPECT:	#"武师"
			titleID = [ csdefine.TITLE_NOVICIATE_WUSHI_X, csdefine.TITLE_NOVICIATE_WUSHI_C ]
		elif presLevel == csdefine.PRESTIGE_ADMIRE:		#"镖头"
			titleID = [ csdefine.TITLE_NOVICIATE_DART_HEAD_X, csdefine.TITLE_NOVICIATE_DART_HEAD_C ]
		elif presLevel >= csdefine.PRESTIGE_ADORE:		#"镖王"
			titleID = [ csdefine.TITLE_NOVICIATE_DART_KING_X, csdefine.TITLE_NOVICIATE_DART_KING_C ]

		if factionID == 37:return titleID[0]	# 兴隆镖局势力是37
		elif factionID == 38:return titleID[1]	# 昌平镖局势力是38
		else:return csdefine.TITLE_NONE

	def removeDartTitle( self ):
		"""
		清除玩家的镖局称号（所有镖局的称号都清除）
		"""
		if not self.titles:
			return
		for titleID in self.titles:
			if titleID >= csdefine.TITLE_NOVICIATE_LANLUHU_X and titleID <= csdefine.TITLE_NOVICIATE_LANLUHU_C:
				self.removeTitle( titleID )

	def getMyTeachTitle( self ):
		"""
		获得自己最高级别的师父称号
		"""
		teachTitle = {}
		for titleID in self.titles:
			if g_titleLoader.isTeachTitle( titleID ):
				teachTitle[titleID] = g_titleLoader.getTeachCreditRequire( titleID )

		if teachTitle == {}: return 0
		list = sorted( teachTitle.values(), reverse = True )  #从大到小排序
		myTeachTitle = list[0]	#取最大的
		for id in teachTitle.keys():
			if teachTitle.get( id ) == myTeachTitle:
				return id
		return 0

	def getOpposeDartPrestige( self, id ):
		"""
		获得对立镖局的id
		@param id : 镖局势力的id
		@type id : STRING
		"""
		if id == 38:
			return 37
		return 38

	def setPrestige( self,  factionID, value ):
		"""
		设置声望值
		"""
		currentPrestige = self.getPrestige( factionID )
		self.addPrestige( factionID, value - currentPrestige )

	def checkAndRemoveTitle( self, factionID, oldprestigeValue ):
		"""
		降级时，去除高级称号 by姜毅
		"""
		nowpreValue = self.prestige.getPrestige( factionID )
		if nowpreValue == oldprestigeValue: return
		oldTitleID = g_titleLoader.getTitleIDByCredit( factionID, oldprestigeValue )
		titleID = g_titleLoader.getTitleIDByCredit( factionID, nowpreValue )
		if oldTitleID not in self.titles or oldTitleID == titleID: return
		if abs( oldprestigeValue ) > abs( nowpreValue ) :
			self.removeTitle( oldTitleID )

	def updateDartTitle( self, factionID, directSelect = False ):
		"""
		增加运镖称号
		"""
		titleID = self.getDartTitleID( factionID, csdefine.QUEST_TYPE_DART )	#取得玩家在镖局中的运镖称号ID
		if titleID in self.titles:
			return
		self.removeDartTitle()
		#titleID = self.getDartTitleID( factionID, csdefine.QUEST_TYPE_DART )	#取得玩家在镖局中的运镖称号ID
		self.addTitle( titleID )												#增加运镖称号
		if directSelect:
			self.selectTitle( self.id, titleID )

	def onPlayerPrestigeChanged( self ):
		"""
		声望改变后的触发
		"""
		self.client.onPrestigeChange()

	def hasTitle( self, titleID ):
		"""
		"""
		return titleID in self.titles

	def receiveTitleName( self, titleID, titleString ):
		"""
		Define method.
		接收可变称号数据
		"""
		oldTitle = self.title
		try:
			titleName = g_titleLoader.getName( titleID ) % titleString
		except:
			ERROR_MSG( "不存在的titleID( %i )." % titleID )
			return
		if self.queryTemp( "title_isWield", False ):
			self._changeTitle( oldTitle, titleID, titleName )
		else:
			self.titleName = titleName
		self.removeTemp( "title_isWield" )

	def getPrestigeByName( self, name ):
		"""
		根据声望名字获取声望，目前只用于GM命令
		"""
		factionID = factionMgr.getIDByName( name )
		if factionID:
			return self.getPrestige( factionID )
		return None

	def addPrestigeByName( self, name, value ):
		"""
		根据声望名字增加声望，目前只用于GM命令
		"""
		factionID = factionMgr.getIDByName( name )
		if factionID:
			self.addPrestige( factionID, value )
	
	def resetPrestige( self ):
		"""
		重置所有声望，目前只用于GM命令
		"""
		self.prestige.clear()


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/08/30 10:17:04  wangshufeng
# 声望数据结构调整，相应调整代码
#
# Revision 1.3  2008/08/22 09:09:27  songpeifang
# 添加了获得运镖和劫镖的称号的接口
#
# Revision 1.2  2008/07/19 01:57:16  wangshufeng
# 添加称号系统
#
# Revision 1.1  2008/07/14 04:13:33  wangshufeng
# add new interface：RoleCredit
#
#
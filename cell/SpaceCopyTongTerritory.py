# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
标准场景，也可以作为场景基类
"""

import BigWorld
import Language
from bwdebug import *
import time
import Const
import csstatus
import csdefine
import csconst
from SpaceCopy import SpaceCopy

SPACE_LAST_TIME  = 15*60

class SpaceCopyTongTerritory( SpaceCopy ):
	"""
	帮会领地
	@ivar domainMB:			一个声明的属性，记录了它的领域空间mailbox，用于某些需要通知其领域空间的操作，此接口如果为None则表示当前不可使用
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.setTemp( "playerDatas", {} )
		
		self._isRobWarOn = False # 帮会掠夺战是否正在进行的标志
		self._enemyTongDBID = 0 # 帮会掠夺战中敌对帮会的DBID
		
		# 此列表作为一个self._players的扩充，因为后者提供的信息太有限，对于帮会领地这种有各种活动的公共空间
		# 理应需要比较详细的玩家信息（这样才有利于区分不同的活动，并对特定需求编程）。这个列表中是一个字典，
		# 用于保存每个玩家的各种信息，可以按需动态添加各种信息。需要保存某个统计信息时请参考registerPlayer中
		# 的实现。 by mushuang
		self._detailedPlayerInfo = [] #[ { 玩家1的信息 },{ 玩家2的信息 }, ... ] 

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		self.queryTemp( "playerDatas" )[ baseMailbox.id ] = ( params[ "tongDBID" ], baseMailbox )
		SpaceCopy.onEnter( self, baseMailbox, params )
		
		## 如果在帮会掠夺战起期间，自动将玩家的PK模式设为“帮会模式” 参见： CSOL-9842
		playerTongDBID = params.get( "tongDBID", None )
		if not playerTongDBID:
			ERROR_MSG( "Can't find player tongDBID in params!" )
			return
		self.__setRobWarPkMode( playerTongDBID, baseMailbox )
		
	def __setRobWarPkMode( self, playerTongDBID, baseMailbox ):
		"""
		根据实际情况设定玩家在掠夺战中的PK模式
		"""
		# if 不在掠夺战中 then return
		if not self._isRobWarOn: return
		
		
		spaceTongDBID = self.params.get( "tongDBID", None )
		if spaceTongDBID == None :
			ERROR_MSG( "Can't find space tongDBID in self.params!" )
			return
		
		# if 玩家是自己人 或者 玩家是敌对帮会的人
		if playerTongDBID == spaceTongDBID or playerTongDBID == self._enemyTongDBID:
			#保存玩家当前的PK模式 并 将玩家的PK模式设定为“帮会模式”
			baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG ) # 设置默认PK模式为帮会模式
			baseMailbox.cell.lockPkMode()
			
	def __restoreRobWarPkMode( self, playerTongDBID, baseMailbox ):
		"""
		恢复玩家在进入副本之前的PK模式
		"""
		# if 不在掠夺战中 then return
		if not self._isRobWarOn: return
			
		spaceTongDBID = self.params.get( "tongDBID", None )
		if not spaceTongDBID:
			ERROR_MSG( "Can't find space tongDBID in self.params!" )
			return
		
		# if 玩家是自己人 或者 玩家是敌对帮会的人
		if playerTongDBID == spaceTongDBID or playerTongDBID == self._enemyTongDBID:
			# 将玩家的pk模式恢复到进入领地之前的状态
			baseMailbox.cell.unLockPkMode()
			baseMailbox.cell.setSysPKMode( 0 ) # 取消默认PK模式设置
			
	def registerPlayer( self, baseMailbox, params = {} ): # 对于帮会领地这种公共空间，但是又有N多活动的对象，多保存一点信息有助于对不同活动进行编程 by mushuang
		"""
		注册进入此space的mailbox和玩家名称
		"""
		SpaceCopy.registerPlayer( self, baseMailbox, params )
		playerInfo = {}
		playerInfo[ "tongDBID" ] = params[ "tongDBID" ]
		playerInfo[ "id" ] = baseMailbox.id
		playerInfo[ "baseMailbox" ] = baseMailbox
		
		self._detailedPlayerInfo.append( playerInfo )
		
	def unregisterPlayer( self, baseMailbox, params = {} ):
		"""
		取消该玩家的记录
		"""
		SpaceCopy.unregisterPlayer( self, baseMailbox, params = {} )
		
		playerID = baseMailbox.id
		length = len( self._detailedPlayerInfo )
		for i in xrange( length ):
			id = self._detailedPlayerInfo[i].get( "id", 0 )
			if id == playerID:
				del self._detailedPlayerInfo[ i ]
				break
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeave( self, baseMailbox, params )
		self.queryTemp( "playerDatas" ).pop( baseMailbox.id )
		
		## 如果在帮会掠夺战期间，自动将玩家的PK模式还原 参见： CSOL-9842
		playerTongDBID = params.get( "tongDBID", None )
		if playerTongDBID == None :
			ERROR_MSG( "Can't find player tongDBID in params!" )
			return
		self.__restoreRobWarPkMode( playerTongDBID, baseMailbox )
	#------------------------------------处理神兽 玩家进入后获得神兽BUFF------------------------------------------

	def getNagualBuffID( self, nagualLevel, nagualType ):
		"""
		获得神兽的对应光环BUFF技能ID
		"""
		if nagualLevel <= 0:
			nagualLevel = 1

		if csdefine.TONG_SHENSHOU_TYPE_1 == nagualType:
			return 730017000 + nagualLevel
		elif csdefine.TONG_SHENSHOU_TYPE_2 == nagualType:# 白毛虎神
			return 730018000 + nagualLevel
		elif csdefine.TONG_SHENSHOU_TYPE_3 == nagualType:# 玄武圣君
			return 730015000 + nagualLevel
		elif csdefine.TONG_SHENSHOU_TYPE_4 == nagualType:# 炽焰朱雀
			return 730016000 + nagualLevel

	def castNagualBuffToTongMember( self, nagualLevel, nagualType ):
		"""
		对领地内的本帮会成员添加神兽的光环BUFF
		"""
		self.setTemp( "nagualData", ( nagualLevel, nagualType ) )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			if tongDBID == self.params[ "tongDBID" ]:
				pMB.cell.setTemp( "nagualOver", 0 )
				pMB.cell.spellTarget( self.getNagualBuffID( nagualLevel, nagualType ), pMB.id )

	def onNagualCreated( self, nagualLevel, nagualType ):
		"""
		神兽被创建了
		"""
		self.castNagualBuffToTongMember( nagualLevel, nagualType )

	def onNagualUpdateLevel( self, nagualLevel, nagualType ):
		"""
		神兽级别更新了
		"""
		self.castNagualBuffToTongMember( nagualLevel, nagualType )

	def onShenShouDestroy( self ):
		"""
		神兽被销毁了
		"""
		self.removeTemp( "nagualData" )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			if tongDBID == self.params[ "tongDBID" ]:
				pMB.cell.setTemp( "nagualOver", 1 )

	#--------------------------------------帮会祭祀活动-----------------------------------------------------------------------

	def onStartTongFete( self ):
		"""
		define method.
		开始帮会祭祀活动了，  领地可以为该活动做一些相应的准备
		如：投放好场景物件。。
		"""
		self.setTemp( "feteData", 0 )

	def onOverTongFete( self ):
		"""
		define method.
		结束帮会祭祀活动
		"""
		self.removeTemp( "feteData" )

	#--------------------------------------保护帮会活动-----------------------------------------------------------------------
	def checkProtectTongStart( self ):
		"""
		检查保护帮派活动是否已经开始了
		这种情况产生主要是因为可能保护帮派开始了，但这个帮会的领地
		还没有加载， 那么活动会在globaldata设置一个标记， 所有帮会领地
		启动后都会检查这个标记， 如果标记的值等于自己帮会的id那么说明
		这次活动是与本帮会有关。
		"""
		tongDBID = 0
		if BigWorld.globalData.has_key( "AS_ProtectTong" ):
			tongDBID = BigWorld.globalData[ "AS_ProtectTong" ][ 0 ]

		if self.params[ "tongDBID" ] == tongDBID:
			self.base.onProtectTongStart( BigWorld.globalData[ "AS_ProtectTong" ][ 2 ] )

	#--------------------------------------魔物来袭活动-----------------------------------------------------------------------
	def startCampaign_monsterRaid( self ):
		"""
		魔物来袭开启
		"""
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		self.setTemp( "startCampaingnTime", time.time() )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			pMB.client.onOpenCopySpaceInterface( [ 0 ] )
	
	def endCampaign_monsterRaid( self ):
		"""
		魔物来袭结束，显示个时间这么麻烦！
		"""
		self.removeTemp( "startCampaingnTime" )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			pMB.client.onCloseCopySpaceInterface()

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
		]
		"""
		if self.queryTemp( "startCampaingnTime", 0 ) > 0:	# 如果startCampaingnTime>0，说明开启了魔物来袭，则打开副本界面
			return [ 0 ]
		else:
			return []
			
	#--------------------------------------帮会掠夺战--------------------------------------#
	def onStartRobWar( self, enemyTongDBID ):
		"""
		defined method
		Base通过此接口通知掠夺战开始
		"""
		self._isRobWarOn = True
		self._enemyTongDBID = enemyTongDBID
		
		# 将所有已经在帮会领地中的我方人员和敌对帮会人员的pk模式锁定为帮会模式
		self.__setAllPlayersPkModeOnRobWar()
		
	def onEndRobWar( self ):
		"""
		defined method
		Base通过此接口通知掠夺战结束
		"""
		# 将所有还在帮会领地中的我方人员和敌对帮会人员的pk模式还原并解锁
		self.__restoreAllPlayersPkModeAfterRobWar()
		
		self._isRobWarOn = False
		self._enemyTongDBID = 0
		
		
	def __setAllPlayersPkModeOnRobWar( self ):
		"""
		在帮会掠夺战开始时将此领地中的所有我方人员和敌对帮会人员的pk模式锁定为帮会模式
		"""
		
		# for player in 所有在此领地的成员
		for playerInfo in self._detailedPlayerInfo:
			# 如果此人是我方或是敌对方的人员，那么改变其pk模式为帮会模式并锁定
			playerTongDBID = playerInfo.get( "tongDBID", 0 )
			playerBaseMB = playerInfo.get( "baseMailbox", None )
			if not playerTongDBID: continue
			if not playerBaseMB: continue
			self.__setRobWarPkMode( playerTongDBID, playerBaseMB )
			
						
	def __restoreAllPlayersPkModeAfterRobWar( self ):
		"""
		在帮会掠夺战结束时将此领地中的所有我方人员和敌对帮会人员的pk模式解锁并恢复为原先的模式
		"""
		# for player in 所有在领地人员:
		for playerInfo in self._detailedPlayerInfo:
			# if player是我方人员或者是敌对帮会人员 then 解锁 并 恢复其PK模式
			playerTongDBID = playerInfo.get( "tongDBID", 0 )
			playerBaseMB = playerInfo.get( "baseMailbox", None )
			if not playerTongDBID: continue
			if not playerBaseMB: continue
			self.__restoreRobWarPkMode( playerTongDBID, playerBaseMB )
		

#
# $Log: not supported by cvs2svn $
#
#
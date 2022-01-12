# -*- coding: gb18030 -*-
#

import BigWorld
import cPickle
from Function import Functor
import ItemTypeEnum
from bwdebug import *
import csstatus

"""
一键换装数据管理器
"""

class OneKeySuitMgr( BigWorld.Base ):
	"""
	一键换装数据管理器
	"""
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "OneKeySuitMgr", self._onRegisterManager )
		
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register OneKeySuitMgr Fail!" )
			# again
			self.registerGlobally( "OneKeySuitMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["OneKeySuitMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("OneKeySuitMgr Create Complete!")
		
		self.oneKeySuitDatas = {}
		self._loadDatas()
		
	def _loadDatas( self ):
		"""
		从数据库加载数据
		"""
		query = "SELECT * FROM custom_oneKeySuit"
		BigWorld.executeRawDatabaseCommand( query, self._onLoadDatas )
		
	def _onLoadDatas( self, result, rows, errstr ):
		"""
		初始化oneKeySuitDatas
		"""
		if errstr:
			ERROR_MSG( "load custom_oneKeySuit failed! %s"%errstr  )
			return
		# （头盔、胸甲、手套、左戒指、裤子、法宝、
		# 武器（盾牌）、项链、腰带、手腕、右戒指、鞋子。）
		"""
		suitPartDict = {
			ItemTypeEnum.CWT_HEAD :0, # 头     —— 头盔
			ItemTypeEnum.CWT_NECK :0, # 颈     —— 项链
			ItemTypeEnum.CWT_BODY :0, # 身体   —— 身甲
			ItemTypeEnum.CWT_BREECH :0, # 臀部   —— 裤子
			ItemTypeEnum.CWT_VOLA :0, # 手     —— 手套
			ItemTypeEnum.CWT_HAUNCH :0, # 腰     —— 腰带
			ItemTypeEnum.CWT_CUFF :0, # 腕     —— 护腕
			ItemTypeEnum.CWT_LEFTHAND :0, # 左手   —— 盾牌
			ItemTypeEnum.CWT_RIGHTHAND :0, # 右手   —— 武器
			ItemTypeEnum.CWT_FEET :0, # 脚     —— 鞋子
			ItemTypeEnum.CWT_LEFTFINGER :0, # 左手指 —— 戒指
			ItemTypeEnum.CWT_RIGHTFINGER :0, # 右手指 —— 戒指
			ItemTypeEnum.CWT_TALISMAN :0, # 法宝
			}
		"""
		for i in result:
			roleDBID = int(i[1])
			if not roleDBID in self.oneKeySuitDatas:
				self.oneKeySuitDatas[roleDBID] = {}
			suitOrder = int(i[2])
			self.oneKeySuitDatas[roleDBID][suitOrder] = {}
			self.oneKeySuitDatas[roleDBID][suitOrder]["suitName"] = str(i[3])
			self.oneKeySuitDatas[roleDBID][suitOrder]["suitList"] = [int(t) for t in i[4:]]
			
	def addSuit( self, playerDBID, suitOrder, newSuitName, newSuit, playerMB ):
		"""
		define method
		增加新套装
		@param playerDBID : UINT32
		@param suitOrder : UINT8
		@param newSuitName : STRING
		@param newSuit : LIST OF UID
		@param playerMB : MAILBOX
		"""
		query = "INSERT INTO custom_oneKeySuit SET sm_roleDBID = %d,sm_suitOrder = %d,sm_suitName = \'%s\',sm_head = %d,\
					sm_neck = %d,sm_body = %d,sm_breach = %d,\
					sm_vola = %d,sm_haunch = %d,sm_cuff = %d,\
					sm_lefthand = %d,sm_righthand = %d,sm_feet = %d,\
					sm_leftfinger = %d,sm_rightfinger = %d,sm_talisman = %d"%( playerDBID, suitOrder, newSuitName, newSuit[0], \
			newSuit[1], newSuit[2], newSuit[3], newSuit[4], newSuit[5],\
			newSuit[6], newSuit[7], newSuit[8], newSuit[9], newSuit[10],\
			newSuit[11], newSuit[12] )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onAddSuit, playerDBID, suitOrder, newSuitName, newSuit, playerMB ) )
		
	def _onAddSuit( self, playerDBID, suitOrder, newSuitName, newSuit, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "add one key suit failed! %s"%errstr  )
			return
		try:
			if playerDBID not in self.oneKeySuitDatas:
				self.oneKeySuitDatas[playerDBID] = {}
			self.oneKeySuitDatas[playerDBID][suitOrder] = {}
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitName"] = newSuitName
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitList"] = newSuit
			playerMB.client.onStatusMessage( csstatus.OKS_RENAME_SUCCESSED, "" )
		except:
			ERROR_MSG( "add one key suit error. DBID(%d)Order(%d)"%(playerDBID, suitOrder) )
		
	def updateSuitName( self, playerDBID, suitOrder, newSuitName, playerMB ):
		"""
		define method
		更改套装名称
		@param playerDBID : UINT32
		@param suitOrder : UINT8
		@param newSuitName : STRING
		@param playerMB : MAILBOX
		"""
		query = "UPDATE custom_oneKeySuit SET sm_suitName = \'%s\' WHERE sm_roleDBID = %d AND sm_suitOrder = %d"%( newSuitName, playerDBID, suitOrder )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onUpdateSuitName, playerDBID, suitOrder, newSuitName, playerMB ) )
		
	def _onUpdateSuitName( self, playerDBID, suitOrder, newSuitName, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "update one key suit name failed! %s"%errstr  )
			return
		try:
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitName"] = newSuitName
			playerMB.client.onStatusMessage( csstatus.OKS_RENAME_SUCCESSED, "" )
		except:
			ERROR_MSG( "update one key suit name error. DBID(%d)Order(%d)"%(playerDBID, suitOrder) )
		
	def updateSuit( self, playerDBID, suitOrder, newSuit, playerMB ):
		"""
		define method
		更改套装
		@param playerDBID : UINT32
		@param suitOrder : UINT8
		@param newSuit : LIST OF UID
		@param playerMB : MAILBOX
		"""
		query = "UPDATE custom_oneKeySuit SET sm_head = %d,\
					sm_neck = %d,sm_body = %d,sm_breach = %d,\
					sm_vola = %d,sm_haunch = %d,sm_cuff = %d,\
					sm_lefthand = %d,sm_righthand = %d,sm_feet = %d,\
					sm_leftfinger = %d,sm_rightfinger = %d,sm_talisman = %d \
			WHERE sm_roleDBID = %d AND sm_suitOrder = %d"%( newSuit[0], \
			newSuit[1], newSuit[2], newSuit[3], newSuit[4], newSuit[5],\
			newSuit[6], newSuit[7], newSuit[8], newSuit[9], newSuit[10],\
			newSuit[11], newSuit[12], playerDBID, suitOrder )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onUpdateSuit, playerDBID, suitOrder, newSuit, playerMB ) )
		
	def _onUpdateSuit( self, playerDBID, suitOrder, newSuit, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "update one key suit failed! %s"%errstr  )
			return
		try:
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitList"] = newSuit
			playerMB.client.onStatusMessage( csstatus.OKS_SAVE_SUCCESSED, "" )
		except:
			ERROR_MSG( "update one key suit error. DBID(%d)Order(%d)"%(playerDBID, suitOrder) )
			
	def getSuitDatas( self, playerDBID, playerMB ):
		"""
		define method
		玩家获得其一键套装数据
		"""
		if not playerDBID in self.oneKeySuitDatas:
			return
		playerMB.client.onGetSuitDatas( self.oneKeySuitDatas[playerDBID] )
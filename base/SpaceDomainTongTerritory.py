# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
Space domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
import csstatus
from SpaceDomain import SpaceDomain
import csdefine

# 领域类
class SpaceDomainTongTerritory(SpaceDomain):
	"""
	城市战场副本领域 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		
		# 以玩家的dbid来映射SpaceItem实例，以提高副本同一条件的进入判断速度，
		# 玩家的dbid也标示与之相对应的SpaceItem例实的拥有者，
		# 使用玩家的dbid而不使用entityID的原因是为了防止玩家下（断）线后重上时找不到原来的所属space，
		# 也是为了防止玩家以下（断）线的方式绕过副本短时间内可进入的次数
		# 此表与self.spaceItems_对应，如果在self.spaceItems_删除一项，也应该在这里删除，创建亦然
		# key = player's dbid, value = spaceNumber
		self.reset()
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		
	def reset( self ):
		"""
		"""
		self.tempData = {}
		self.tempData[ "waitEnterPlayers" ] = {}	# 记录等待进入领地的人
		self.tempData[ "waitLoginPlayers" ] = {}

	def createSpaceItem( self, param ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
		"""
		# 由于当前的规则是创建者不会（也不可能）随着队长的改变而改变，
		# 如果当前副本的创建者离开了队伍，然后自己另外创建副本时，
		# 新的副本就会覆盖旧的副本，由于旧的副本保存的创建者还是现在的玩家，
		# 当旧的副本比该玩家新创建的副本先关闭时，必然会导致新的副本映射被删除，
		# 因此，为了避免这种bug，在创建新的副本时，我们必须先查找当前玩家是否已创建了副本，
		# 如果有则需要先把旧副本的创建者置0（即没有创建者或创建者丢失），才可以创建新的副本。
		tongDBID = param.get( "tongDBID" )		# dbid参数来自与之相关的ObjectScripts/SpaceCopy.py的相关接口
		assert tongDBID is not None, "the param tongDBID is necessary."
		
		spaceItem = self.getSpaceItem( tongDBID )
		if spaceItem:
			spaceItem.params["tongDBID"] = ""
		spaceItem = SpaceDomain.createSpaceItem( self, param )
		self.keyToSpaceNumber[ tongDBID ] = spaceItem.spaceNumber
		return spaceItem

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		空间关闭，space entity销毁通知。
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		SpaceDomain.onSpaceCloseNotify( self, spaceNumber )
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		# 这里取了个巧， 方向一般是设置为0的， 如果里面包含了数据 则是其他帮会的DBID
		if params[ "enter_tong_territory_datas" ].has_key( "enterOtherTong" ):
			params[ "tongDBID" ] = params[ "enter_tong_territory_datas" ][ "enterOtherTong" ]
			
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			if position[0] == 0 and position[1] == 0  and position[2] == 0:
				position = self.getScript().enterPoint[0]
				direction = self.getScript().enterPoint[1]
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			# 创建一个等待队列， 可能在副本未被创建出来时 会有好几个人请求进入
			tongDBID = params[ "tongDBID" ]
			if tongDBID in self.tempData[ "waitEnterPlayers" ]:
				self.tempData[ "waitEnterPlayers" ][ tongDBID ].append( baseMailbox )
			else:
				self.tempData[ "waitEnterPlayers" ][ tongDBID ] = [ baseMailbox ]
			BigWorld.globalData[ "TongManager" ].onRequestCreateTongTerritory( self, tongDBID )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			# 创建一个等待队列， 可能在副本未被创建出来时 会有好几个人请求进入
			tongDBID = params[ "tongDBID" ]
			if tongDBID in self.tempData[ "waitLoginPlayers" ]:
				self.tempData[ "waitLoginPlayers" ][ tongDBID ].append( baseMailbox )
			else:
				self.tempData[ "waitLoginPlayers" ][ tongDBID ] = [ baseMailbox ]
			BigWorld.globalData[ "TongManager" ].onRequestCreateTongTerritory( self, tongDBID )
			
	def onCreateTongTerritory( self, tongDBID, ysdt_level, jk_level, ssd_level, ck_level, tjp_level, sd_level, yjy_level, shenshouType, shenshouReviveTime ):
		"""
		define method.
		创建帮会领地
		"""
		# 构件一个帮会领地参数
		params = { "tongDBID" : tongDBID, "ysdt_level": ysdt_level, "jk_level" : jk_level, "ssd_level" : ssd_level, "ck_level" : ck_level, "tjp_level" : tjp_level, \
		"sd_level" : sd_level, "yjy_level" : yjy_level, "shenshouType" : shenshouType, "shenshouReviveTime" : shenshouReviveTime,"spaceKey":tongDBID }
		
		spaceItem = self.findSpaceItem( params, True )
		if spaceItem:
			if tongDBID in self.tempData[ "waitEnterPlayers" ]:
				pickData = self.pickToSpaceData( None, params )
				for baseMailbox in self.tempData[ "waitEnterPlayers" ].pop( tongDBID ):
					spaceItem.enter( baseMailbox, self.getScript().enterPoint[0], self.getScript().enterPoint[1], pickData )
					
			if tongDBID in self.tempData[ "waitLoginPlayers" ]:		
				for baseMailbox in self.tempData[ "waitLoginPlayers" ].pop( tongDBID ):
					spaceItem.logon( baseMailbox )				
		else:
			self.onCreateTongTerritoryError( tongDBID )
			
	def onCreateTongTerritoryError( self, tongDBID ):
		"""
		define method.
		创建帮会领地失败
		"""
		if tongDBID in self.tempData[ "waitEnterPlayers" ]:		
			for baseMailbox in self.tempData[ "waitEnterPlayers" ].pop( tongDBID ):
				baseMailbox.client.onStatusMessage( csstatus.TONG_TARGET_INVALID, "" )
				
		if tongDBID in self.tempData[ "waitLoginPlayers" ]:			
			for baseMailbox in self.tempData[ "waitLoginPlayers" ].pop( tongDBID ):
				baseMailbox.tong_logonInTerritoryError()
			
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""	
		pass
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/01 08:04:17  kebiao
# 增加玩家复活点规则
#
# Revision 1.1  2008/07/31 09:03:41  kebiao
# add:SpaceDomainFamilyWar
#
#
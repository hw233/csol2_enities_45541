# -*- coding: gb18030 -*-
import BigWorld

import cschannel_msgs
import csstatus
from bwdebug import *

class TongFengHuoLianTianMember:
	def __init__( self ):
		self.tongDBID = 0
		self.dbid = 0
		self.rname = ""
		self.mailBox = None
		self.kill = 0
		self.bekill = 0
		self.isIn = False
	
	def init( self, tongDBID, dbid, rname, mailBox, kill, bekill, isIn ):
		self.tongDBID = tongDBID
		self.dbid = dbid
		self.rname = rname
		self.mailBox = mailBox
		self.kill = kill
		self.bekill = bekill
		self.isIn = isIn
	
	def leavelSpace( self ):
		self.isIn = False
	
	def enterSpace( self ):
		self.isIn = True
		
	def addKill( self ):
		self.kill += 1
	
	def addDead( self ):
		self.bekill += 1
		
	def getDictFromObj( self, obj ):
		dict = {
			"dbid" 		: obj.dbid,
			"rname" 	: obj.rname,
			"mailBox"	: obj.mailBox,
			"kill" 		: obj.kill,
			"bekill"	: obj.bekill,
			"isIn" 		: obj.isIn
		}
		return dict
	
	def createObjFromDict( self, dict ):
		self.dbid = dict[ "dbid" ]
		self.rname = dict[ "rname" ]
		self.mailBox = dict[ "mailBox" ]
		self.kill = dict[ "kill" ]
		self.bekill = dict[ "bekill" ]
		self.isIn = dict[ "isIn" ]
		
	def isSameType( self, obj ):
		return isinstance( obj, TongFengHuoLianTianMember )
		
class TongFengHuoLianTianInfo:
	# 帮会城市战副本数据
	def __init__( self ):
		self.tongDBID = 0
		self.integral = 0
		self.members = {}
	
	def init( self, tongDBID, integral = 0 ):
		self.tongDBID = tongDBID
		self.integral = integral
	
	def getMember( self, dbid ):
		return self.members[ dbid ]
	
	def addMember( self, dbid, rname, mailBox, kill, bekill, isIn ):
		if self.members.has_key( dbid ):
			m = self.members[ dbid ]
			m.mailBox = mailBox
			m.isIn = True
		else:
			m = TongFengHuoLianTianMember()
			m.init( self.tongDBID, dbid, rname, mailBox, kill, bekill, isIn )
			self.members[ dbid ] = m
	
	def addKill( self, dbid ):
		self.members[ dbid ].addKill()
	
	def addDead( self, dbid ):
		self.members[ dbid ].addDead()
	
	def addIntegral( self, integral ):
		self.integral += integral
		
	def decIntegral( self, integral ):
		self.integral -= integral
	
	def leaveMember( self, dbid ):
		if self.members.has_key( dbid ):
			self.members[ dbid ].isIn = False
	
	def instance( self, dict ):
		self.tongDBID = dict[ "tongDBID" ]
		self.integral = dict[ "integral" ]
		for m in  dict[ "members" ]:
			self.members[ m[ "dbid" ] ] = m
	
	def getEnter( self ):
		return len( self.members )
	
	def upInfoToClient( self, info ):
		for m in self.members.itervalues():
			# 把战报发给玩家
			if m.isIn:
				m.mailBox.client.tong_onFHLTReport( info.tongDBID, info.rname, info.kill, info.bekill, info.isIn )
				pass
	
	def upInfoAllToClient( self, playerMailbox ):
		for m in self.members.itervalues():
			playerMailbox.client.tong_onFHLTReport( m.tongDBID, m.rname, m.kill, m.bekill, m.isIn )
			pass
		
	def upIntegralToClient( self, tongDBID, integral ):
		# 更新帮会城战积分到客户端
		for m in self.members.itervalues():
			m.mailBox.client.tong_onUpdateFHLTPoint( tongDBID, integral )
			pass
	
	def upIntegralAllToClient( self, playerMailBox ):
		playerMailBox.client.tong_onUpdateFHLTPoint( self.tongDBID, self.integral )
		pass
	
	def notifyPlayerLeave( self, memInfo ):
		if memInfo.tongDBID == self.tongDBID:
			for m in self.members.itervalues():
				if m.isIn:
					m.mailBox.client.onStatusMessage( csstatus.TONG_CITY_ENTER_LEAVE_MSG, str( ( cschannel_msgs.TONGCITYWAR_WO, memInfo.rname, cschannel_msgs.TONGCITYWAR_LI_KAI ) ) )
		else:
			for m in self.members.itervalues():
				if m.isIn:
					m.mailBox.client.onStatusMessage( csstatus.TONG_CITY_ENTER_LEAVE_MSG, str( ( cschannel_msgs.TONGCITYWAR_DI, memInfo.rname, cschannel_msgs.TONGCITYWAR_LI_KAI ) ) )
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "tongDBID" ] = obj.tongDBID
		dict[ "integral" ] = obj.integral
		dict[ "members" ] = obj.members.values()
		return dict
	
	def createObjFromDict( self, dict ):
		obj = TongFengHuoLianTianInfo()
		obj.instance( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, TongFengHuoLianTianInfo )

class TongFengHuoLianTianInfos:
	def __init__( self ):
		self.infos = {}
		self.winner = 0
	
	def instance( self, dict ):
		for tInfos in dict[ "infos" ]:
			self.infos[ tInfos.tongDBID ] = tInfos
	
	def addMember( self, tongDBID, dbid, rname, mailBox, kill = 0, bekill = 0, isIn = True ):
		if self.infos.has_key( tongDBID ):
			self.infos[ tongDBID ].addMember( dbid, rname, mailBox, kill, bekill, isIn )
		else:
			warInfo = TongFengHuoLianTianInfo()
			warInfo.init( tongDBID )
			warInfo.addMember( dbid, rname, mailBox, kill, bekill, isIn )
			self.infos[ tongDBID ] = warInfo
		
		self.upInfoToClient( tongDBID, dbid ) # 更新其它玩家战报
		self.upInfoAllToClient( mailBox )	  # 往新加入玩家身上发战报
		self.upIntegralToClient( tongDBID )   # 更新所有帮会积分
		self.upIntegralAllToClient( mailBox ) # 把所有帮会的积分再往新加入人员身上写一次
		
	def addKill( self, tongDBID, dbid ):
		self.infos[ tongDBID ].addKill( dbid )
		self.upInfoToClient( tongDBID, dbid )
	
	def addDead( self, tongDBID, dbid ):
		self.infos[ tongDBID ].addDead( dbid )
		self.upInfoToClient( tongDBID, dbid )
		
	def leaveMember( self, tongDBID, dbid ):
		if self.infos.has_key( tongDBID ):
			self.infos[ tongDBID ].leaveMember( dbid )
		
		self.upInfoToClient( tongDBID, dbid )
		self.notifyPlayerLeave( tongDBID, dbid )
	
	def addIntegral( self, tongDBID, integral ):
		# 添加帮会积分
		maxIntegral = self.getMaxIntegral()
		self.infos[ tongDBID ].addIntegral( integral )
		if self.infos[ tongDBID ].integral > maxIntegral:
			self.winner = tongDBID
			
		self.upIntegralToClient( tongDBID )
	
	def decIntegral( self, tongDBID, integral ):
		self.infos[ tongDBID ].decIntegral( integral )
		self.upIntegralToClient( tongDBID )
	
	def getIntegral( self, tongDBID ):
		if self.infos.has_key( tongDBID ):
			return self.infos[ tongDBID ].integral
		else:
			return -1
	
	def getMaxIntegral( self ):
		maxIntegral = 0
		for item in self.infos.itervalues():
			if item.integral > maxIntegral:
				maxIntegral = item.integral
		return maxIntegral
	
	def getEnter( self, tongDBID ):
		return self.infos[ tongDBID ].getEnter()
	
	def upInfoToClient( self, tongDBID, dbid ):
		# 更新一条信息到所有客户端
		info =  self.infos[ tongDBID ].getMember( dbid )
		for item in self.infos.itervalues():
			item.upInfoToClient( info )
	
	def upInfoAllToClient( self, playerMailbox ):
		# 更新所有战报到指定客户端
		for item in self.infos.itervalues():
			item.upInfoAllToClient( playerMailbox )
	
	def upIntegralToClient( self, tongDBID ):
		# 更新帮会积分到客户端面
		upItem = self.infos[ tongDBID ]
		for item in self.infos.itervalues():
			item.upIntegralToClient( upItem.tongDBID, upItem.integral )
		
	def upIntegralAllToClient( self, playerMailbox ):
		# 更新所有帮会积分到指定客户端
		for item in self.infos.itervalues():
			item.upIntegralAllToClient( playerMailbox )
	
	def notifyPlayerLeave( self, tongDBID, playerDBID ):
		# 广播有人离开的消息
		memInfo = self.infos[ tongDBID ].getMember( playerDBID )
		for item in self.infos.itervalues():
			item.notifyPlayerLeave( memInfo )
	
	def getIntegralMax( self ):
		max = 0
		maxTong = 0
		for item in self.infos.itervalues():
			if item.integral > max:
				max = item.integral
				maxTong = item.tongDBID
		
		return maxTong
	
#	def rewardWinMember( self, winTongDBID ):
#		if self.infos.has_key( winTongDBID ):
#			memInfos = self.infos[ winTongDBID ].members
#			for member in memInfos.itervalues():
#				if member.isIn:
#					#member.mailBox.cell.tong_onCityWarOverReward()
#					pass
	
	def countInSpacePlayer( self, tongDBID ):
		count = 0
		if not self.infos.has_key( tongDBID ):
			return count
		
		memInfos = self.infos[ tongDBID ].members
		for member in memInfos.itervalues():
			if member.isIn:
				count += 1
		
		return count
		
	def __getitem__( self, tongDBID ):
		return self.infos[ tongDBID ]
	
	def __setitem__( self, tongDBID, members ):
		self.infos[ tongDBID ] = members
			
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "infos" ] = obj.infos.values()
		return dict
		
	def createObjFromDict( self, dict ):
		obj = TongFengHuoLianTianInfos()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, TongFengHuoLianTianInfos )

		
		
fengHuoLianTianMemberIns = TongFengHuoLianTianMember()
fengHuoLianTianInfoIns = TongFengHuoLianTianInfo()
fengHuoLianTianInfosIns = TongFengHuoLianTianInfos()
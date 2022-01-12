# -*- coding: gb18030 -*-
import BigWorld

import cschannel_msgs
import csstatus
from bwdebug import *

class CampFengHuoLianTianMember:
	def __init__( self ):
		self.dbid = 0
		self.rname = ""
		self.mailBox = None
		self.kill = 0
		self.bekill = 0
		self.isIn = False
	
	def init( self, dbid, rname, mailBox, kill, bekill, isIn ):
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
		return isinstance( obj, CampFengHuoLianTianMember )
		
class CampFengHuoLianTianInfo:
	# 帮会城市战副本数据
	def __init__( self ):
		self.camp = 0
		self.integral = 0
		self.members = {}
	
	def init( self, camp, integral = 0 ):
		self.camp = camp
		self.integral = integral
	
	def getMember( self, dbid ):
		return self.members[ dbid ]
	
	def addMember( self, dbid, rname, mailBox, kill, bekill, isIn ):
		if self.members.has_key( dbid ):
			m = self.members[ dbid ]
			m.mailBox = mailBox
			m.isIn = True
		else:
			m = CampFengHuoLianTianMember()
			m.init( dbid, rname, mailBox, kill, bekill, isIn )
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
		self.camp = dict[ "camp" ]
		self.integral = dict[ "integral" ]
		for m in  dict[ "members" ]:
			self.members[ m[ "dbid" ] ] = m
	
	def getEnter( self ):
		return len( self.members )
	
	def upInfoToClient( self, camp, info ):
		for m in self.members.itervalues():
			# 把战报发给玩家
			if m.isIn:
				m.mailBox.client.camp_onFHLTReport( camp, info.rname, info.kill, info.bekill, info.isIn )
				pass
	
	def upInfoAllToClient( self, playerMailbox ):
		for m in self.members.itervalues():
			playerMailbox.client.camp_onFHLTReport( self.camp, m.rname, m.kill, m.bekill, m.isIn )
			pass
		
	def upIntegralToClient( self, camp, integral ):
		# 更新帮会城战积分到客户端
		for m in self.members.itervalues():
			m.mailBox.client.camp_onUpdateFHLTPoint( camp, integral )
			pass
	
	def upIntegralAllToClient( self, playerMailBox ):
		playerMailBox.client.camp_onUpdateFHLTPoint( self.camp, self.integral )
		pass
	
	def notifyPlayerLeave( self, memInfo, camp ):
		if camp == self.camp:
			for m in self.members.itervalues():
				if m.isIn:
					m.mailBox.client.onStatusMessage( csstatus.TONG_CITY_ENTER_LEAVE_MSG, str( ( cschannel_msgs.TONGCITYWAR_WO, memInfo.rname, cschannel_msgs.TONGCITYWAR_LI_KAI ) ) )
		else:
			for m in self.members.itervalues():
				if m.isIn:
					m.mailBox.client.onStatusMessage( csstatus.TONG_CITY_ENTER_LEAVE_MSG, str( ( cschannel_msgs.TONGCITYWAR_DI, memInfo.rname, cschannel_msgs.TONGCITYWAR_LI_KAI ) ) )
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "camp" ] = obj.camp
		dict[ "integral" ] = obj.integral
		dict[ "members" ] = obj.members.values()
		return dict
	
	def createObjFromDict( self, dict ):
		obj = CampFengHuoLianTianInfo()
		obj.instance( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, CampFengHuoLianTianInfo )

class CampFengHuoLianTianInfos:
	def __init__( self ):
		self.infos = {}
		self.winner = 0
	
	def instance( self, dict ):
		for tInfos in dict[ "infos" ]:
			self.infos[ tInfos.camp ] = tInfos
	
	def addMember( self, camp, dbid, rname, mailBox, kill = 0, bekill = 0, isIn = True ):
		if self.infos.has_key( camp ):
			self.infos[ camp ].addMember( dbid, rname, mailBox, kill, bekill, isIn )
		else:
			warInfo = CampFengHuoLianTianInfo()
			warInfo.init( camp )
			warInfo.addMember( dbid, rname, mailBox, kill, bekill, isIn )
			self.infos[ camp ] = warInfo
		
		self.upInfoToClient( camp, dbid ) # 更新其它玩家战报
		self.upInfoAllToClient( mailBox )	  # 往新加入玩家身上发战报
		self.upIntegralToClient( camp )   # 更新所有帮会积分
		self.upIntegralAllToClient( mailBox ) # 把所有帮会的积分再往新加入人员身上写一次
		
	def addKill( self, camp, dbid ):
		self.infos[ camp ].addKill( dbid )
		self.upInfoToClient( camp, dbid )
	
	def addDead( self, camp, dbid ):
		self.infos[ camp ].addDead( dbid )
		self.upInfoToClient( camp, dbid )
		
	def leaveMember( self, camp, dbid ):
		if self.infos.has_key( camp ):
			self.infos[ camp ].leaveMember( dbid )
		
		self.upInfoToClient( camp, dbid )
		self.notifyPlayerLeave( camp, dbid )
	
	def addIntegral( self, camp, integral ):
		# 添加帮会积分
		maxIntegral = self.getMaxIntegral()
		self.infos[ camp ].addIntegral( integral )
		if self.infos[ camp ].integral > maxIntegral:
			self.winner = camp
			
		self.upIntegralToClient( camp )
	
	def decIntegral( self, camp, integral ):
		self.infos[ camp ].decIntegral( integral )
		self.upIntegralToClient( camp )
	
	def getIntegral( self, camp ):
		if self.infos.has_key( camp ):
			return self.infos[ camp ].integral
		else:
			return -1
	
	def getMaxIntegral( self ):
		maxIntegral = 0
		for item in self.infos.itervalues():
			if item.integral > maxIntegral:
				maxIntegral = item.integral
		return maxIntegral
	
	def getEnter( self, camp ):
		return self.infos[ camp ].getEnter()
	
	def upInfoToClient( self, camp, dbid ):
		# 更新一条信息到所有客户端
		info =  self.infos[ camp ].getMember( dbid )
		for item in self.infos.itervalues():
			item.upInfoToClient( camp, info )
	
	def upInfoAllToClient( self, playerMailbox ):
		# 更新所有战报到指定客户端
		for item in self.infos.itervalues():
			item.upInfoAllToClient( playerMailbox )
	
	def upIntegralToClient( self, camp ):
		# 更新帮会积分到客户端面
		upItem = self.infos[ camp ]
		for item in self.infos.itervalues():
			item.upIntegralToClient( upItem.camp, upItem.integral )
		
	def upIntegralAllToClient( self, playerMailbox ):
		# 更新所有帮会积分到指定客户端
		for item in self.infos.itervalues():
			item.upIntegralAllToClient( playerMailbox )
	
	def notifyPlayerLeave( self, camp, playerDBID ):
		# 广播有人离开的消息
		memInfo = self.infos[ camp ].getMember( playerDBID )
		for item in self.infos.itervalues():
			item.notifyPlayerLeave( memInfo, camp )
	
	def getIntegralMax( self ):
		max = 0
		maxCamp = 0
		for item in self.infos.itervalues():
			if item.integral > max:
				max = item.integral
				maxCamp = item.camp
		
		return maxCamp
	
#	def rewardWinMember( self, winTongDBID ):
#		if self.infos.has_key( winTongDBID ):
#			memInfos = self.infos[ winTongDBID ].members
#			for member in memInfos.itervalues():
#				if member.isIn:
#					#member.mailBox.cell.tong_onCityWarOverReward()
#					pass
	
		
	def findMaxKillPlayerName( self ):
		maxKill = 0
		maxPlayerName = ""
		for item in self.infos.itervalues():
			memInfos = item.members
			for member in memInfos.itervalues():
				if member.kill > maxKill:
					maxKill = member.kill
					maxPlayerName = member.rname
		return maxPlayerName
		
	def __getitem__( self, camp ):
		return self.infos[ camp ]
	
	def __setitem__( self, camp, members ):
		self.infos[ camp ] = members
			
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "infos" ] = obj.infos.values()
		return dict
		
	def createObjFromDict( self, dict ):
		obj = CampFengHuoLianTianInfos()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, CampFengHuoLianTianInfos )

		
		
campFengHuoMemberIns = CampFengHuoLianTianMember()
campFengHuoInfoIns = CampFengHuoLianTianInfo()
campFengHuoInfosIns = CampFengHuoLianTianInfos()

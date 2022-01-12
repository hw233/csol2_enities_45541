# -*- coding: gb18030 -*-

# bigworld
import BigWorld
# common
import csdefine
import csconst
import ItemTypeEnum
from bwdebug import *
import CombatUnitConfig
# cell
import Const
import items
from Love3 import g_skills
from Love3 import g_npcBaseAttr
from ObjectScripts.GameObjectFactory import g_objFactory
from NPCAccumLoader import NPCAccumLoader
g_npcAccum = NPCAccumLoader.instance()

from Resource.NPCExcDataLoader import NPCExcDataLoader
g_npcExcData = NPCExcDataLoader.instance()

from MonsterIntensifyPropertyData import MonsterIntensifyPropertyData
g_monsterIntensifyAttr = MonsterIntensifyPropertyData.instance()

import ECBExtend
# config 
import csstatus

REQ_READY_TIME = 60#(秒)

PVE_SPACE_CLASS_NAME = "ying_xiong_lian_meng_01"
PVP_SPACE_CLASS_NAME = "ying_xiong_lian_meng_pvp"
CAMP_SPACE_CLASS_NAME = "camp_ying_xiong_wang_zuo"

class RobotAttr:
	def __init__( self ):
		self.className = ""
		self.name = ""
		self.strength = 0
		self.corporeity = 0
		self.dexterity = 0
		self.intellect = 0
		
		self.HP_Max = 0
		self.damage = 0
		self.accumPoint = 0.0
		self.robotClass = 0
		self.level = 0
		self.MP_Max = 0
	
	def initData( self, className, level ):
		self.className = className
		self.level = level
		objScript = g_objFactory.getObject( className )
		self.name = objScript.getName()
		baseAtt = objScript.getEntityProperty( "baseAtt" )
		raceclass = objScript.getEntityProperty( "raceclass" )
		self.robotClass = raceclass & csdefine.RCMASK_CLASS
		
		attrDict = g_npcBaseAttr.get( self.robotClass, level )
		self.strength = attrDict[ "strength_base" ] * baseAtt
		self.corporeity = attrDict[ "corporeity_base" ] * baseAtt
		self.intellect = attrDict[ "intellect_base" ] * baseAtt
		self.dexterity = attrDict[ "dexterity_base" ] * baseAtt
		
		self.HP_Max = self.corporeity * 10
		
		excDict = g_npcExcData.get( self.robotClass, self.level )
		excAtt = objScript.getEntityProperty( "excAtt" )
		self.damage = int( excDict["data_dps"] * excAtt )
		
		self.accumPoint = g_monsterIntensifyAttr.getAttr( self.className, -1, "accumPoint" )
	
	def getDict( self ):
		dict = {}
		dict[ "className" ] = self.className
		dict[ "robotName" ] = self.name
		dict[ "damage" ] = self.damage
		dict[ "hp_max" ] = self.HP_Max
		dict[ "accumPoint" ] = self.accumPoint
		dict[ "robotClass" ] = self.robotClass
		dict[ "level" ] = self.level
		return dict

class BaoZangCopyInterface:
	#宝藏副本接口( 英雄王座 )
	def __init__( self ):
		pass
	
	# ----------------------
	#  PVE
	#-----------------------
	def baoZangReqRobotInfos( self, exposed ):
		"""
		define method.
		请求怪物信息
		"""
		robotsInfos = self.getBaoZangReqRobotInfos()
		self.client.baoZangOnReqRobotInfos( robotsInfos )
	
	def getBaoZangReqRobotInfos( self ):
		"""
		获取机器人信息
		"""
		robotsInfos = []
		for cn in csconst.YXLM_ROBOT_1:
			ra = RobotAttr()
			ra.initData( cn, self.level )
			robotsInfos.append( ra.getDict() )
		
		for cn in csconst.YXLM_ROBOT_2:
			ra = RobotAttr()
			ra.initData( cn, self.level )
			robotsInfos.append( ra.getDict() )
		return robotsInfos
	
	def baoZangPVESetRobot( self, exposed, robotInfos ):
		"""
		exposed method
		"""
		if not self.hackVerify_( exposed ):
			return
		
		if not self.isTeamCaptain():
			self.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
		
		for p in self.getTeamMemberMailboxs():
			p.client.baoZangPVEonSetRobot( robotInfos )
			
	def baoZangReqPVE( self, robotsInfos, rbtCls ):
		"""
		define method
		申请进入英雄联盟PVE模式
		"""
		for p in self.getTeamMemberMailboxs():
			p.client.baoZangReqPVE( robotsInfos, rbtCls )
	
	def baoZangOnReqPVE( self, exposed, robotInfos ):
		"""
		define method.
		申请进入英雄联盟PVP模式回调
		robotInfos ： 机器信息
		"""
		if not self.hackVerify_( exposed ):
			return
		
		if not self.isTeamCaptain():
			self.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
				
		memberList = self.getAllMemberInRange( 30.0 )
		self.setTemp( "YX_robotInfos", robotInfos )
		pos, direction = g_objFactory.getObject( PVE_SPACE_CLASS_NAME ).getEnterInf( self )
		self.gotoSpace( PVE_SPACE_CLASS_NAME, pos, direction )
		for m in memberList:
			if m.id == self.id:
				continue 
				
			m.setTemp( "YX_robotInfos", robotInfos )
	
	# ----------------------
	#  PVP
	#-----------------------
	def baoZangGetRivalTeamIDs( self ):
		return self.baoZangRivalMembers
	
	def baoZangSetRivalTeamIDs( self, teamMembers, countDown ):
		"""
		define method
		设置对手队伍的ID
		countDown 倒计时
		"""
		self.baoZangRivalMembers = teamMembers
		if self.queryTemp( "BAO_ZANG_PVP_IS_READY", False ):
			self.removeTemp( "BAO_ZANG_PVP_IS_READY" )
			self.addTimer( 3.0, 0, ECBExtend.ENTER_BAO_ZANG_PVP )
			
		for p in self.getTeamMemberMailboxs():
			p.client.baoZangOpenPVPTeamInfos( self.baoZangGetRivalTeamIDs(), 4, False )
	
	def baoZangPVPInfosReset( self ):
		"""
		define method
		清除队伍匹配信息信息
		"""
		self.baoZangRivalTMB = None
		self.baoZangRivalMembers = []
		self.removeTemp( "BAO_ZANG_REQ_TIME" )
		
	def baoZangReqPVP( self ):
		"""
		define method
		申请进入英雄联盟PVP模式
		"""
		BigWorld.globalData[ "BaoZangCopyMgr" ].req( self.base, self.teamMailbox, self.level )
	
	def baoZangPVPcancel( self, exposed ):
		"""
		expose method.
		取消PVP排队
		"""
		if not self.hackVerify_( exposed ):
			return
		
		if not self.isTeamCaptain():
			self.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
			
		BigWorld.globalData[ "BaoZangCopyMgr" ].cancel( self.teamMailbox.id, False )

	def baoZangReqSucceed( self, teamMB ):
		"""
		define method.
		匹配成功
		"""
		self.baoZangRivalTMB = teamMB
		self.client.baoZangReqSucceed( teamMB.id )
		self.addTimer( REQ_READY_TIME, 0, ECBExtend.READY_BAO_ZANG_PVP )
		self.setTemp( "BAO_ZANG_REQ_TIME", time.time() )
	
	def baoZangGetRivalTeam( self ):
		"""
		获取宝藏副本敌对队伍
		"""
		return self.baoZangRivalTMB
	
	def baoZangGotoNPC( self, exposed ):
		"""
		exposed mothod
		传送到进入NPC
		"""
		#进入NPC位置
		if not self.hackVerify_( exposed ):
			return
			
		if not self.baoZangRivalTMB:
			return
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YXLM_PVP:
			self.statusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_IN_SPACE )
		else:
			self.gotoSpace( "fengming", ( 57.370, 12.069, 147.031 ), ( 0.007, 0.999, 0.034 ) )
	
	def baoZangEnterReady( self ):
		"""
		队伍已经准备好
		"""
		self.baoZangRivalTMB.baoZangSetRivalTeamIDs( self.getTeamMemberIDs(), time.time() )
		
		countDown = 0
		if len( self.baoZangRivalMembers ):
			countDown = 3
			self.addTimer( 4.0, 0, ECBExtend.ENTER_BAO_ZANG_PVP )
		else:
			countDown = REQ_READY_TIME -( time.time() - self.queryTemp( "BAO_ZANG_REQ_TIME", time.time() ) )
		
		for p in self.getTeamMemberMailboxs():
			p.client.baoZangOpenPVPTeamInfos( self.baoZangGetRivalTeamIDs(), countDown, True )
		
		self.setTemp( "BAO_ZANG_PVP_IS_READY", True )
		
	def baoZangEnterReadyEnd( self, controllerID, userData  ):
		"""
		准备结束
		"""
		self.baoZangPVPInfosReset()
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YXLM_PVP:
			return 
		
		self.client.baoZangClosePVPTeamInfos()
				
		if self.queryTemp( "BAO_ZANG_PVP_IS_READY" ) and self.isTeamCaptain():
			self.baoZangReqPVP()
	
	def baoZangEnterCopy( self, controllerID, userData ):
		"""
		进入副本
		"""
		memberList = self.getAllMemberInRange( 30.0 )
		teamInfos = [ self.teamMailbox.id, self.baoZangRivalTMB.id ]
		teamInfos.sort()
		t_index = teamInfos.index( self.teamMailbox.id )
		self.set( "YXLM_PVP_TEAM_INDEX", t_index )
		self.setTemp( "YX_teamInofs", tuple( teamInfos ) )
		pos, direction = g_objFactory.getObject( PVP_SPACE_CLASS_NAME ).getEnterInf( self )
		self.gotoSpace( PVP_SPACE_CLASS_NAME, pos, direction )
		for m in memberList:
			if m.id == self.id:
				continue
				
			m.set( "YXLM_PVP_TEAM_INDEX", t_index )
			m.setTemp( "YX_teamInofs", tuple( teamInfos ) )
	
	def baoZangTeamIndex( self ):
		"""
		宝藏副本复活
		"""
		return self.query( "YXLM_PVP_TEAM_INDEX", 0 )
	
	# ----------------------
	#  阵营英雄王座
	#-----------------------
	def yingXiongCampGetRivalTeamIDs( self ):
		return self.yingXiongCampRivalMembers
	
	def yingXiongCampSetRivalTeamIDs( self, teamMembers, countDown ):
		"""
		define method
		设置对手队伍的ID
		countDown 倒计时
		"""
		self.yingXiongCampRivalMembers = teamMembers
		if self.queryTemp( "CAMP_YING_XIONG_IS_READY", False ):
			self.removeTemp( "CAMP_YING_XIONG_IS_READY" )
			self.addTimer( 3.0, 0, ECBExtend.ENTER_CAMP_YING_XIONG_COPY )
			
		for p in self.getTeamMemberMailboxs():
			p.client.yingXiongCampOpenTeamInfos( self.yingXiongCampGetRivalTeamIDs(), 4, False )
	
	def yingXiongCampInfosReset( self ):
		"""
		define method
		清除队伍匹配信息信息
		"""
		self.yingXiongCampRivalTMB = None
		self.yingXiongCampRivalMembers = []
		self.removeTemp( "CAMP_YING_XIONG_REQ_TIME" )
		
	def yingXiongCampReq( self ):
		"""
		define method
		申请进入阵营英雄王座
		"""
		BigWorld.globalData[ "CampMgr" ].yingXiong_req( self.base, self.teamMailbox, self.level, self.getCamp() )
	
	def yingXiongCampCancel( self, exposed ):
		"""
		expose method.
		取消排队
		"""
		if not self.hackVerify_( exposed ):
			return
		
		if not self.isTeamCaptain():
			self.statusMessage( csstatus.SPACE_COOY_YE_WAI_MUST_TEAM_CAPTIAN )
			return
			
		BigWorld.globalData[ "CampMgr" ].yingXiong_cancel( self.teamMailbox.id, False )

	def yingXiongCampReqSucceed( self, teamMB ):
		"""
		define method.
		匹配成功
		"""
		self.yingXiongCampRivalTMB = teamMB
		self.client.yingXiongCampReqSucceed( teamMB.id )
		self.addTimer( REQ_READY_TIME, 0, ECBExtend.READY_CAMP_YING_XIONG_COPY )
		self.setTemp( "CAMP_YING_XIONG_REQ_TIME", time.time() )
	
	def yingXiongCampGetRivalTeam( self ):
		"""
		获取宝藏副本敌对队伍
		"""
		return self.yingXiongCampRivalTMB
	
	def yingXiongCampGotoNPC( self, exposed ):
		"""
		exposed mothod
		传送到进入NPC
		"""
		#进入NPC位置
		if not self.hackVerify_( exposed ):
			return
			
		if not self.yingXiongCampRivalTMB:
			return
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YXLM_PVP:
			self.statusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_IN_SPACE )
		else:
			self.gotoSpace( "fengming", ( 189.167, 10.400, 186.329 ), ( 0.007, 0.999, 0.034 ) )
	
	def yingXiongCampEnterReady( self ):
		"""
		队伍已经准备好
		"""
		self.yingXiongCampRivalTMB.yingXiongCampSetRivalTeamIDs( self.getTeamMemberIDs(), time.time() )
		
		countDown = 0
		if len( self.yingXiongCampRivalMembers ):
			countDown = 3
			self.addTimer( 4.0, 0, ECBExtend.ENTER_CAMP_YING_XIONG_COPY )
		else:
			countDown = REQ_READY_TIME -( time.time() - self.queryTemp( "CAMP_YING_XIONG_REQ_TIME", time.time() ) )
		
		for p in self.getTeamMemberMailboxs():
			p.client.yingXiongCampOpenTeamInfos( self.yingXiongCampGetRivalTeamIDs(), countDown, True )
		
		self.setTemp( "CAMP_YING_XIONG_IS_READY", True )
		
	def yingXiongCampEnterReadyEnd( self, controllerID, userData  ):
		"""
		准备结束
		"""
		self.yingXiongCampInfosReset()
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YXLM_PVP:
			return 
		
		self.client.yingXiongCampCloseTeamInfos()
				
		if self.queryTemp( "CAMP_YING_XIONG_IS_READY" ) and self.isTeamCaptain():
			self.yingXiongCampReqPVP()
	
	def yingXiongCampEnterCopy( self, controllerID, userData ):
		"""
		进入副本
		"""
		memberList = self.getAllMemberInRange( 30.0 )
		teamInfos = [ self.teamMailbox.id, self.yingXiongCampRivalTMB.id ]
		teamInfos.sort()
		t_index = teamInfos.index( self.teamMailbox.id )
		self.set( "CAMP_YING_XIONG_TEAM_INDEX", t_index )
		self.setTemp( "CYX_teamInofs", tuple( teamInfos ) )
		pos, direction = g_objFactory.getObject( CAMP_SPACE_CLASS_NAME ).getEnterInf( self )
		self.gotoSpace( CAMP_SPACE_CLASS_NAME, pos, direction )
		for m in memberList:
			if m.id == self.id:
				continue
				
			m.set( "CAMP_YING_XIONG_TEAM_INDEX", t_index )
			m.setTemp( "CYX_teamInofs", tuple( teamInfos ) )
	
	def yingXiongCampTeamIndex( self ):
		"""
		宝藏副本复活
		"""
		return self.query( "CAMP_YING_XIONG_TEAM_INDEX", 0 )
# -*- coding:gb18030 -*-

from bwdebug import *
import csdefine
import csconst
from Love3 import g_objFactory
import math
import Math
import BigWorld
import random
import csstatus
class RoleEidolonHandler:
	"""
	角色小精灵操作接口
	"""
	def __init__( self ):
		"""
		"""
		pass

	def manageEidolon4Login( self ):
		"""
		玩家登陆，处理小精灵相关事务

		player Level <= 30，召唤小精灵
		"""
		if self.getLevel() > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
			return
		if not self.canConjureEidolon(): # 不允许召唤
			return
		if self.queryTemp( "conjuringEidolon", False ):	# 正在召唤中
			return
		if self.queryTemp( "eidolonNPCMB", None ):		# 已经召唤了
			return
#		self._conjureEidolon()	# 召唤出可跟随玩家的小精灵

	def conjureEidolonSuccess( self, eidolonBaseMB ):
		"""
		Define method.
		召唤小精灵成功的回调

		@param eidolonBaseMB: 小精灵的base mailbox
		"""
		self.removeTemp( "conjuringEidolon" )
		self.setTemp( "eidolonNPCMB", eidolonBaseMB )
		self.callEidolonCell().giveControlToOwner()

	def levelUp4Eidolon( self ):
		"""
		玩家级别提升对小精灵的影响
		"""
		if self.getLevel() >= csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:	# csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL后小精灵无跟随功能
			eidolonCall = self.callEidolonCell()
			if eidolonCall:
				eidolonCall.destroyEidolon()

	def callEidolonCell( self ):
		"""
		for real
		"""
		eidolonBaseMB = self.queryTemp( "eidolonNPCMB", None )
		if eidolonBaseMB:
			try:
				eidolon = BigWorld.entities[eidolonBaseMB.id]
			except KeyError:
				return eidolonBaseMB.cell
			else:
				return eidolon
		return None

	def onEidolonDestory( self ):
		"""
		Define method.
		小精灵被销毁
		"""
		self.removeTemp( "eidolonNPCMB" )

	def conjureEidolon( self, srcEntityID ):
		"""
		召唤小精灵
		Exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return
		if self.getLevel() > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL and\
			self.vip == csdefine.ROLE_VIP_LEVEL_NONE :
				DEBUG_MSG( "%s :im not vip" % self.getName() )
				self.statusMessage( csstatus.EIDOLON_WITHDRAW_NOT_VIP )#add by wuxo 2011-12-7
				return
		if not self.canConjureEidolon(): # 不允许召唤
			return
		if self.queryTemp( "conjuringEidolon", False ):	# 正在召唤中
			return
		if self.queryTemp( "eidolonNPCMB", None ):		# 已经召唤了
			return
		self._conjureEidolon()

	def _conjureEidolon( self ):
		"""
		"""
		# 精灵在离角色一定距离的地点出生，而不是与角色重叠
		rx, ry, rz = self.position
		keepDistance = 2.0
		x = rx - keepDistance * math.sin( self.yaw )
		z = rz - keepDistance * math.cos( self.yaw )
		position = Math.Vector3( x, ry, z )
		# 精灵entity与地表做碰撞，确保可以放在地面上
		pos = position
		for amend in ( 1, 4 ):
			try :
				pos = ( position[0], position[1] + amend, position[2] )
				r = BigWorld.collide( caster.spaceID, position, pos )
				if r is not None :
					pos = r[0]
					break
			except :
				pass

		ownerAttr = { "ownerID": self.id, "ownerName" : self.getName(), "baseOwner" : self.base, "ownerLevel":self.getLevel(), "spaceMBID": self.getCurrentSpaceBase().id }
		# 如果有小精灵模型数据
		eidolonModelInfo = self.queryTemp( "eidolonModelNum", None )
		if eidolonModelInfo:
			ownerAttr["modelNumber"] = eidolonModelInfo[0]
			ownerAttr["modelScale"] = eidolonModelInfo[1]
		if self.isShareVip:
			ownerAttr["isShare"] = self.isShareVip
			ownerAttr["shareVIPLevel"] = self.vip
		if self.isInTeam():
			ownerAttr["ownerCaptainID"] = self.captainID	# 小精灵共享vip功能时可以通过比较captainID以确定是否同在一个队伍中
		self.createNPCObjectFormBase( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), csconst.EIDOLON_NPC_CLASSNAME, pos, self.direction, ownerAttr )

	def withdrawEidolon( self, srcEntityID ):
		"""
		收回小精灵
		Exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return
		eidolonCall = self.callEidolonCell()
		if eidolonCall:
			self.statusMessage( csstatus.EIDOLON_WITHDRAW_DESTROY )
			self.client.onWithdrawEidolon()
			eidolonCall.destroyEidolon()

	def canConjureEidolon( self ):
		"""
		能否召唤小精灵
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canConjureEidolon: # 此地图不允许召唤
			self.statusMessage( csstatus.EIDOLON_WITHDRAW_IN_FORBIDSPACE ) #add by wuxo 2011-12-7
			return False
		
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.statusMessage( csstatus.EIDOLON_WITHDRAW_IN_FLYSTATE )#add by wuxo 2011-12-7
			return False

		return True
	
	def withdrawEidolonBeforeBuff( self, srcEntityID ):
		"""
		骑宠飞行、飞行传送、凌波微步或类似的buff生效时要收回小精灵并记录状态
		Exposed Method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return
		eidolonCall = self.callEidolonCell()
		if eidolonCall:
			self.client.onWithdrawEidolon()
			eidolonCall.destroyEidolon()
			self.setTemp( "autoWithdrawEidolon", True )
	
	def conjureEidolonAfterBuff( self, srcEntityID ):
		"""
		骑宠飞行、飞行传送、凌波微步或类似的buff结束时要召唤小精灵
		Exposed Method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return
		if self.queryTemp( "autoWithdrawEidolon", False ):
			self.removeTemp( "autoWithdrawEidolon" )
			if self.getLevel() > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
				return
			spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			spaceScript = g_objFactory.getObject( spaceKey )
			if not spaceScript.canConjureEidolon:
				return
			if self.queryTemp( "conjuringEidolon", False ):	# 正在召唤中
				return
			if self.queryTemp( "eidolonNPCMB", None ):		# 已经召唤了
				return
#			self._conjureEidolon()
	
	def eidolonTeleport( self ):
		"""
		小精灵传送跟着主人传送
		define method.
		"""
		eidolonCall = self.callEidolonCell()
		if eidolonCall:
			pos = Math.Vector3( self.position )
			rPos = ( pos.x +  random.randint( -2, 2 ), pos.y, pos.z + random.randint( -2, 2 ) )
			cResult = BigWorld.collide( self.spaceID, ( rPos[0], rPos[1] - 10, rPos[2] ), ( rPos[0], rPos[1] + 10, rPos[2] ) )
			if cResult:
				rPos = cResult[0]
			else:
				rPos = tuple( self.position )
			eidolonCall.teleportToOwner( self, self.spaceID, rPos, self.direction  )

	def hasEidolon( self ):
		"""
		是否召唤了小精灵
		"""
		return self.queryTemp( "eidolonNPCMB", None ) != None

	def vipShareSwitch( self, srcEntityID ):
		"""
		Exposed method.
		vip共享开关
		"""
		if srcEntityID != self.id:
			HACK_MSG( " srcEntityID( %i ) != self.id( %i ) " % ( srcEntityID, self.id ) )
			return

		self.isShareVip = not self.isShareVip
		eidolonNPCCall = self.callEidolonCell()
		if eidolonNPCCall:
			if self.isShareVip:
				eidolonNPCCall.vipShare( self.vip )
			else:
				eidolonNPCCall.stopShare()

	def setVIP( self, vipLevel ):
		"""
		设置玩家的vip等级
		"""
		self.vip = vipLevel
		if self.isShareVip:
			eidolonNPCCall = self.callEidolonCell()
			if eidolonNPCCall:
				eidolonNPCCall.onOwnerVIPLevelChange( vipLevel )

	def ei_onLevelTeam( self ):
		"""
		玩家离开队伍影响小精灵vip功能
		"""
		eidolonNPCCall = self.callEidolonCell()
		if eidolonNPCCall:
			eidolonNPCCall.onOwnerLeaveTeam()

	def ei_joinTeam( self ):
		"""
		玩家加入队伍对vip功能的影响
		"""
		eidolonNPCCall = self.callEidolonCell()
		if eidolonNPCCall:
			eidolonNPCCall.onOwnerJoinTeam( self.teamMailbox.id )

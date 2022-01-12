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
	��ɫС��������ӿ�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def manageEidolon4Login( self ):
		"""
		��ҵ�½������С�����������

		player Level <= 30���ٻ�С����
		"""
		if self.getLevel() > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
			return
		if not self.canConjureEidolon(): # �������ٻ�
			return
		if self.queryTemp( "conjuringEidolon", False ):	# �����ٻ���
			return
		if self.queryTemp( "eidolonNPCMB", None ):		# �Ѿ��ٻ���
			return
#		self._conjureEidolon()	# �ٻ����ɸ�����ҵ�С����

	def conjureEidolonSuccess( self, eidolonBaseMB ):
		"""
		Define method.
		�ٻ�С����ɹ��Ļص�

		@param eidolonBaseMB: С�����base mailbox
		"""
		self.removeTemp( "conjuringEidolon" )
		self.setTemp( "eidolonNPCMB", eidolonBaseMB )
		self.callEidolonCell().giveControlToOwner()

	def levelUp4Eidolon( self ):
		"""
		��Ҽ���������С�����Ӱ��
		"""
		if self.getLevel() >= csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:	# csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL��С�����޸��湦��
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
		С���鱻����
		"""
		self.removeTemp( "eidolonNPCMB" )

	def conjureEidolon( self, srcEntityID ):
		"""
		�ٻ�С����
		Exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return
		if self.getLevel() > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL and\
			self.vip == csdefine.ROLE_VIP_LEVEL_NONE :
				DEBUG_MSG( "%s :im not vip" % self.getName() )
				self.statusMessage( csstatus.EIDOLON_WITHDRAW_NOT_VIP )#add by wuxo 2011-12-7
				return
		if not self.canConjureEidolon(): # �������ٻ�
			return
		if self.queryTemp( "conjuringEidolon", False ):	# �����ٻ���
			return
		if self.queryTemp( "eidolonNPCMB", None ):		# �Ѿ��ٻ���
			return
		self._conjureEidolon()

	def _conjureEidolon( self ):
		"""
		"""
		# ���������ɫһ������ĵص���������������ɫ�ص�
		rx, ry, rz = self.position
		keepDistance = 2.0
		x = rx - keepDistance * math.sin( self.yaw )
		z = rz - keepDistance * math.cos( self.yaw )
		position = Math.Vector3( x, ry, z )
		# ����entity��ر�����ײ��ȷ�����Է��ڵ�����
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
		# �����С����ģ������
		eidolonModelInfo = self.queryTemp( "eidolonModelNum", None )
		if eidolonModelInfo:
			ownerAttr["modelNumber"] = eidolonModelInfo[0]
			ownerAttr["modelScale"] = eidolonModelInfo[1]
		if self.isShareVip:
			ownerAttr["isShare"] = self.isShareVip
			ownerAttr["shareVIPLevel"] = self.vip
		if self.isInTeam():
			ownerAttr["ownerCaptainID"] = self.captainID	# С���鹲��vip����ʱ����ͨ���Ƚ�captainID��ȷ���Ƿ�ͬ��һ��������
		self.createNPCObjectFormBase( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), csconst.EIDOLON_NPC_CLASSNAME, pos, self.direction, ownerAttr )

	def withdrawEidolon( self, srcEntityID ):
		"""
		�ջ�С����
		Exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return
		eidolonCall = self.callEidolonCell()
		if eidolonCall:
			self.statusMessage( csstatus.EIDOLON_WITHDRAW_DESTROY )
			self.client.onWithdrawEidolon()
			eidolonCall.destroyEidolon()

	def canConjureEidolon( self ):
		"""
		�ܷ��ٻ�С����
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canConjureEidolon: # �˵�ͼ�������ٻ�
			self.statusMessage( csstatus.EIDOLON_WITHDRAW_IN_FORBIDSPACE ) #add by wuxo 2011-12-7
			return False
		
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.statusMessage( csstatus.EIDOLON_WITHDRAW_IN_FLYSTATE )#add by wuxo 2011-12-7
			return False

		return True
	
	def withdrawEidolonBeforeBuff( self, srcEntityID ):
		"""
		�����С����д��͡��貨΢�������Ƶ�buff��ЧʱҪ�ջ�С���鲢��¼״̬
		Exposed Method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return
		eidolonCall = self.callEidolonCell()
		if eidolonCall:
			self.client.onWithdrawEidolon()
			eidolonCall.destroyEidolon()
			self.setTemp( "autoWithdrawEidolon", True )
	
	def conjureEidolonAfterBuff( self, srcEntityID ):
		"""
		�����С����д��͡��貨΢�������Ƶ�buff����ʱҪ�ٻ�С����
		Exposed Method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return
		if self.queryTemp( "autoWithdrawEidolon", False ):
			self.removeTemp( "autoWithdrawEidolon" )
			if self.getLevel() > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
				return
			spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			spaceScript = g_objFactory.getObject( spaceKey )
			if not spaceScript.canConjureEidolon:
				return
			if self.queryTemp( "conjuringEidolon", False ):	# �����ٻ���
				return
			if self.queryTemp( "eidolonNPCMB", None ):		# �Ѿ��ٻ���
				return
#			self._conjureEidolon()
	
	def eidolonTeleport( self ):
		"""
		С���鴫�͸������˴���
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
		�Ƿ��ٻ���С����
		"""
		return self.queryTemp( "eidolonNPCMB", None ) != None

	def vipShareSwitch( self, srcEntityID ):
		"""
		Exposed method.
		vip������
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
		������ҵ�vip�ȼ�
		"""
		self.vip = vipLevel
		if self.isShareVip:
			eidolonNPCCall = self.callEidolonCell()
			if eidolonNPCCall:
				eidolonNPCCall.onOwnerVIPLevelChange( vipLevel )

	def ei_onLevelTeam( self ):
		"""
		����뿪����Ӱ��С����vip����
		"""
		eidolonNPCCall = self.callEidolonCell()
		if eidolonNPCCall:
			eidolonNPCCall.onOwnerLeaveTeam()

	def ei_joinTeam( self ):
		"""
		��Ҽ�������vip���ܵ�Ӱ��
		"""
		eidolonNPCCall = self.callEidolonCell()
		if eidolonNPCCall:
			eidolonNPCCall.onOwnerJoinTeam( self.teamMailbox.id )

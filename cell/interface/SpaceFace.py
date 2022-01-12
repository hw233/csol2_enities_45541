# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.15 2008-08-30 09:21:16 yangkai Exp $

"""
Player Cell for SPACE Face
2007/07/19: tidied up by huangyongwei
"""

from bwdebug import *
import BigWorld
import Language
from ECBExtend import *
import csconst
import csstatus
import csdefine
import Const
import Math
import math
import utils
from ObjectScripts.GameObjectFactory import g_objFactory
from MsgLogger import g_logger

from ObjectScripts.SpaceCopy  import SpaceCopy

ILLEGALITY_POSITION_Y_AXIS = -99999

# player id, space name, time
TELEPORT_KEY = "SPACE WATCH DOG: %s.[player id %i, player name %s, space %s, at %f]"

# ����λ�洫�ͽ�����ǰ����1��ľ���
GUESS_TIME = 1

class SpaceFace:
	"""
	player in cell
	"""
	def __init__( self ):
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onEnterSpace_( self ):
		"""
		����ҽ���ĳ�ռ䣬�÷���������
		"""
		self.spaceType = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		print "++++++ entering space!"
		print TELEPORT_KEY % ("player entered space", self.id, self.getName(), self.spaceType, BigWorld.time())
		spaceBase = self.getCurrentSpaceBase()

		try:
			cellMailbox = BigWorld.entities[spaceBase.id]
		except KeyError:
			cellMailbox = spaceBase.cell
		space = g_objFactory.getObject( self.spaceType )
		cellMailbox.onEnter( self.base, space.packedSpaceDataOnEnter( self ) )

	def onLeaveSpace_( self ):
		"""
		������뿪ĳ�ռ䣬�÷���������
		"""
		# ȡ��entity��ǰ���ڵ�space��space entity base
		# ����ҵ����򷵻���Ӧ��base���Ҳ����򷵻�.
		# �Ҳ�����ԭ��ͨ������Ϊspace����destoryed�У����Լ���û���յ�ת��֪ͨ��destroy.
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % self.spaceID]
		except KeyError:
			return

		try:
			cellMailbox = BigWorld.entities[spaceBase.id]
		except KeyError:
			cellMailbox = spaceBase.cell

		# ����ڲ�ͬ��ͼ���ͽ�������д�
		if self.qieCuoState in [ csdefine.QIECUO_READY, csdefine.QIECUO_FIRE ]:
			self.loseQieCuo()
		elif self.qieCuoState in [ csdefine.QIECUO_INVITE, csdefine.QIECUO_BEINVITE ] :
			self.replyQieCuo( self.id, self.qieCuoTargetID, False )

		space = g_objFactory.getObject( self.spaceType )
		cellMailbox.onLeave( self.base, space.packedSpaceDataOnLeave( self ) )

	# -------------------------------------------------
	def onEnterArea( self ) :
		"""
		ͬ��ͼ��ת�󱻵���
		hyw--2008.10.08
		"""
		pass

	def onLeaveArea( self ):
		"""
		ͬ��ͼ��תǰ������
		hyw--2008.10.08
		"""
		pass

	def onGotoSpaceBefore( self, spaceName ):
		"""
		����ǰ����
		"""
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def gotoForetime( self ):
		"""
		define method.
		���͵���ȥ��λ��
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:	# ���κθ����У�ֻҪ��ϵͳ�Զ�������ҳ����������������δ��������������ͨ�ĸ��ʽ�������󶨵�
			self.reviveOnCity()
			self.setTemp( "role_die_teleport", True ) 	#������ʱ�������
		else:
			self.setTemp( "ignoreFullRule", True )		# ����һ����ǣ� �ڶ��ߵ�ͼ�к������ߵĹ��� �����ڸ������޷�������������
			self.gotoSpace( self.lastSpaceType, self.lastSpacePosition, self.direction )
			self.removeTemp( "ignoreFullRule" )

	def gotoEnterPos( self ):
		"""
		define method.
		���͵����븱����λ��
		"""
		self.setTemp( "ignoreFullRule", True )
		self.gotoSpace( self.lastSpaceType, self.lastSpacePosition, self.direction )
		self.removeTemp( "ignoreFullRule" )
		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.reviveActivity()

	# ----------------------------------------------------------------
	# callback methods
	# ----------------------------------------------------------------
	def enterSpaceNotify( self ):
		"""
		defined method.
		�ڲ��ӿڣ�����������
		����space���
		"""
		self.onEnterSpace_()
		# δ��BUFF
		self.spellTarget( csconst.PENDING_SKILL_ID, self.id )
		# ���ԴspaceID��Ŀ��spaceID��ȣ��϶��еط�������
		assert self.popTemp( "enter_spaceID" ) != self.spaceID

	def enterPlanesNotify(self):
		"""
		defined method.
		�ڲ��ӿڣ�����������
		����λ��֪ͨ
		"""
		self.onEnterSpace_()

	def requestTeleport( self, exposed ):
		"""
		define method.
		�ͻ���������
		"""
		if exposed != self.id:
			return
		rtInfos = self.queryTemp( "requestTeleport", None )
		if rtInfos:
			rtInfosL = rtInfos.split(";")
			map = rtInfosL[0]
			pos = Math.Vector3( eval(rtInfosL[1]) )
			dire = Math.Vector3( eval(rtInfosL[2]) )
			self.gotoSpace( map, pos, dire )
		self.removeTemp( "requestTeleport" )

	def requestFlash( self, exposed, pos ):
		"""
		exposed method.
		�ͻ�����������
		"""
		if exposed != self.id:
			return
		flashInfo = self.queryTemp( "SPELL_FLASH", 0.0 )
		if flashInfo > 0.0:
			if self.position.flatDistTo( pos ) <= flashInfo:
				self.openVolatileInfo()
				self.position = pos
		self.removeTemp( "SPELL_FLASH" )

	# ----------------------------------------------------------------
	# defination methods
	# ----------------------------------------------------------------
	def gotoSpace( self, spaceName, position, direction ):
		"""
		define method.
		����ռ�
		���ã�
			����spaceName�����ҵ�Ҫ����Ŀռ���Ϣ�����ݿռ���Ҫ����������cell���ռ�����(����������ͬһ����)��
			Ȼ�����base��enterSpace��ڣ�����������ȥ
		@type 			spaceName : string
		@param 			spaceName : �ռ������ռ�Ĺؼ���
		@type 			position  : vector3
		@param 			position  : Ŀ��λ��
		@type 			direction : vector3
		@param 			direction : ����
		"""
		INFO_MSG( spaceName, position, direction )

		#����spaceScript������domain��spaceNormal��һЩ�ӿ� ���Դ˴�ֱ�ӻ�ȡ�� �������ƵĽű�ֱ�ӽ���domain����ؼ��
		spaceObj = g_objFactory.getObject( spaceName )				# 2007.12.14: modified by hyw
		if spaceObj is None :
			ERROR_MSG( "objectScript can't found. %s" % spaceName )
			return

		# ����뿪space�����Ƿ�����
		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		result = currSpaceObj.checkDomainLeaveEnable( self )
		if result != csstatus.SPACE_OK:
			INFO_MSG( "leave domain condition different:", result )
			self.client.spaceMessage( result )
			return

		# ������space�����Ƿ�����
		result = spaceObj.checkDomainIntoEnable( self )
		if result == csstatus.SPACE_OK:
			self.onGotoSpaceBefore( spaceName )
			self.base.enterSpace( spaceName, position, direction, spaceObj.packedDomainData( self ) )
			spaceType = spaceObj.getSpaceType()
			try:
				g_logger.actJoinEnterSpaceLog( spaceType, csdefine.ACTIVITY_JOIN_ROLE, self.databaseID, self.level, self.getName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			INFO_MSG( "into domain condition different:", result )
			self.client.spaceMessage( result )

	def gotoPlane( self, spaceName, position, direction ):
		"""
		Define method.
		�������λ��ռ䡣���ֽ��뷽ʽû�д��ͽ��ȼ��أ�����Ŀ��λ�ñ�����player�ͻ�����Χ�Ѿ����ص�chunk��������playerΪ���ĵ�9����

		������ע�⣬���û��ָ��position����ôʹ����ҵ�ǰ��position����ΪĿ��position������ʹ�ÿͻ����ṩ��position��
		"""
		DEBUG_MSG( "player( %s ) request goto plane( %s )." % ( self.getName(), spaceName ) )
		print TELEPORT_KEY % ("player request goto plane", self.id, self.getName(), spaceName, BigWorld.time())
		# ���������ͬ��ͼλ�洫��
		assert spaceName != self.spaceType

		if position.y <= ILLEGALITY_POSITION_Y_AXIS:	# ��ʱʹ��yֵС�ڵ���ILLEGALITY_POSITION_Y_AXIS��ʾλ����Ч
			position = self.postion
		self.setTemp( "gotoPlane", True )
		self.gotoSpace( spaceName, position, direction )	# ����ͨ��ʽ����ռ䱣��һ�£��ڵײ�ʵ����plane��space��һ���ĸ���
		self.removeTemp( "gotoPlane" )

	def teleportToPlanes( self, position, direction, cellMailBox, planesID ):
		"""
		defined method.
		���ã����͵�ָ��λ��space�������������Ĺ��ܣ��������ָ���ռ䡣
		ע�����ڵײ��teleport()û����ɻص������������Ҫ�Լ�ģ�⡣

		@type     position: vector3
		@param    position: Ŀ��λ��
		@type    direction: vector3
		@param   direction: ����
		@type  cellMailBox: MAILBOX
		@param cellMailBox: ���ڶ�λ��Ҫ��ת��Ŀ��space����mailbox�������������Ч��cell mailbox
		"""
		DEBUG_MSG( "player( %s ) teleport to plane( %s ) at %f" % ( self.getName(), self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), BigWorld.time() ) )
		print TELEPORT_KEY % ("player teleporting to plane", self.id, self.getName(), "N/A", BigWorld.time())

		self.onLeaveSpace_()
		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		if not isinstance(currSpaceObj, SpaceCopy):# ���ߵ�ͼ�ű����������ͼ
			self.lastSpaceType = self.spaceType
			self.lastSpacePosition = self.position

		self.setTemp( "enter_spaceID", self.spaceID )

		self.client.planeSpacePrepare()		# warnning : you have to do this before teleport to plane, or client will fail in smooth into the plane.Any question,pls contact wangshufeng.11:03 2014-1-4
		# You can send a method call after they do a teleport,
		# that's kinda the standard thing,
		# it'll get forwarded and queued on the real entity's destination.
		# The teleport might fail though,
		# if it does, onTeleportFailure gets called before any such queued method does.
		# So you can set a flag in onTeleportFailure and check for that in the queued method.
		#self.volatileInfo = VOLATILE_INFO_CLOSED
		if self.popTemp("MOVE_INTO_PLANE", False):
			print "------->>> move into plane at pos", position
			#prev_pos = position
			#position = self.guessPlaneEnterPos(position, direction)
			#print "------->>> guess destination", position
			#print "------->>> origin yaw %f, guess yaw %f" % (direction[-1], (position - prev_pos).yaw)
		self.systemCastSpell( Const.TELEPORT_PLANE_SKILLID  )	# �ѷ������ٶȵ���֤����Ϊһ���㹻���ֵ����֤�ͻ��˵�λ����֤��λ�洫��ʱ���ڶ��ǺϷ��ģ�ͨ��buff������topSpeed�ı��ʱ��
		self.planesID = planesID
		self.teleport( cellMailBox, position, direction )
		self.enterPlanesNotify()	# �˷���������teleport���棬�ұ�����defs�ж��塣

	def guessPlaneEnterPos(self, position, direction):
		"""
		@param position:
		@param direction:
		@return:
		"""
		global GUESS_TIME
		yaw = direction[-1]

		guessMove = GUESS_TIME * self.move_speed
		xm = guessMove * math.sin(yaw)
		zm = guessMove * math.cos(yaw)

		guessDest = Math.Vector3(position)
		guessDest.x += xm
		guessDest.z += zm

		guessDest = utils.navpolyToGround(self.spaceID, guessDest, 3.0, 3.0)
		properDest = self.canNavigateTo(guessDest, guessMove * 2)

		if properDest is None:
			origin = Math.Vector3(position)
			properDest = Math.Vector3(guessDest)
			origin.y += 0.5
			properDest.y = origin.y
			collision = BigWorld.collide(self.spaceID, origin, properDest)

			if collision:
				properDest = collision[0]
				xm = 0.5 * math.sin(yaw)
				zm = 0.5 * math.cos(yaw)
				properDest.x -= xm
				properDest.z -= zm

		return utils.navpolyToGround(self.spaceID, properDest, 3.0, 3.5)

	def gotoSpaceLineNumber( self, space, lineNumber, position, direction = (0, 0 ,0) ):
		"""
		define method.
		���͵�x�߳����� һЩ֧�ֶ��ߵ�space�����ָ�����͵��ڼ��ߣ�����ʹ������ӿڽ��д���
		ʹ��gotoSpaceҲ���ԣ� �����ױ����͵��ĸ�����space����ƽ����������
			@param space		:	Ŀ�ĳ�����ʶ
			@type space			:	string
			@param lineNumber	:	�ߵĺ���
			@type space			:	uint
			@param position		:	Ŀ�ĳ���λ��
			@type position		:	vector3
			@param direction	:	����ʱ����
			@type direction		:	vector3
		"""
		self.setTemp( "lineNumber", lineNumber )
		self.gotoSpace( space, position, direction )
		self.removeTemp( "lineNumber" )

	def teleportToSpace( self, position, direction, cellMailBox, dstSpaceID ):
		"""
		defined method.
		���ã����͵�ָ��space�������������Ĺ��ܣ��������ָ���ռ䡣
		ע�����ڵײ��teleport()û����ɻص������������Ҫ�Լ�ģ�⡣
			���ڴ���Ŀ���С���ͬ��ͼ�����ͺ͡���ͬ��ͼ���������֣�
			��ˣ���ģ���ʱ��������������Ҫ�����
				- ����Ŀ������ͬ��ͼ
				- ����Ŀ�겻����ͬ��ͼ
			��ʵ˵������dstSpaceID�Ժ󣬸о��ܹ֣�����ǰû�и��õĽ�������ˡ�

		@type     position: vector3
		@param    position: Ŀ��λ��
		@type    direction: vector3
		@param   direction: ����
		@type  cellMailBox: MAILBOX
		@param cellMailBox: ���ڶ�λ��Ҫ��ת��Ŀ��space����mailbox�������������Ч��cell mailbox
		@type   dstSpaceID: int32
		@param  dstSpaceID: Ŀ���ͼ��spaceID�����ֵ��Ҫ����ȷ��Ŀ���ͼ�뵱ǰ��ͼ�Ƿ���ͬһ��ͼ�á�
		"""
		entity = BigWorld.entities.get( cellMailBox.id, None )

		# ���entity�Ҳ�������û���ṩĿ��spaceID��������Ϊ���Ǵ�����÷���
		assert entity is not None or dstSpaceID >= 0

		# ����ʱ��Ӧ���е����˺�,���Խ�����ʼ����ĸ߶ȡ�����ΪҪ���͵���λ�õĸ߶� by mushuang
		self.fallDownHeight = position[ 1 ]

		# ���ڵ�ǰ cellapp �ҵ�ָ���� entity ������ entity ��ͬһ�� space �����ͬ��ͼ����
		# Ŀ��spaceID�뵱ǰ��ͼ��spaceID��ͬ������ͬ��ͼ����
		isSameSpace = ( ( entity is not None and entity.spaceID == self.spaceID ) or ( dstSpaceID == self.spaceID ) )
		self.planesID = 0
		if isSameSpace:
			self.onLeaveArea()
			self.direction = direction # ���������teleportͬ��ͼ���Ͳ����޸ĳ�������⣬���������ֶ����޸Ĵ��͵ĳ���
			self.teleport( None, position, direction )
			self.onEnterArea()
		else:
			self.onLeaveSpace_()
			currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			if not isinstance(currSpaceObj, SpaceCopy):# ���ߵ�ͼ�ű����������ͼ
				self.lastSpaceType = self.spaceType
				self.lastSpacePosition = self.position

			self.setTemp( "enter_spaceID", self.spaceID )	# ûɶ�ã���Ҫ������֤

			# You can send a method call after they do a teleport,
			# that's kinda the standard thing,
			# it'll get forwarded and queued on the real entity's destination.
			# The teleport might fail though,
			# if it does, onTeleportFailure gets called before any such queued method does.
			# So you can set a flag in onTeleportFailure and check for that in the queued method.
			self.teleport( cellMailBox, position, direction )
			self.enterSpaceNotify()	# �˷���������teleport���棬�ұ�����defs�ж��塣

	def onTeleportFailure( self ):
		"""
		This method is called on a real entity when a teleport() call for that entity fails.
		This can occur if the nearby entity mailbox passed into teleport() is stale,
		meaning that the entity that it points to no longer exists on the destination CellApp pointed to by the mailbox.
		"""
		ERROR_MSG( "id %i(%s) teleport failure. current space id %i, space name %s, position" % ( self.id, self.getName(), self.spaceID, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ), self.position )

	def requestInitSpaceSkill( self, exposed ):
		# �����ʼ����������
		# Exposed mothods
		if exposed != self.id:
			return

		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		currSpaceObj.requestInitSpaceSkill( self )

	def isCurrSpaceCanFly( self ):
		"""
		�жϵ�ǰ�ռ��Ƿ���Է���
		"""
		spaceLabel =BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		return g_objFactory.getObject( spaceLabel ).canFly

	def isCurrSpaceCanVehicle( self ):
		"""
		�жϵ�ǰ�ռ��Ƿ�����ٻ����
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		return g_objFactory.getObject( spaceLabel ).canVehicle

	def onSpaceCopyTeleport( self, actType, spaceLabel, pos, direction, isFirstEnter ):
		"""
		define method
		�����ѿ�����
		"""
		if self.isActivityCanNotJoin( actType ) and isFirstEnter:
			self.statusMessage( csstatus.SPACE_COOY_YE_WAI_CHALLENGE_FULL )
		else:
			self.gotoSpace( spaceLabel, pos, direction )

	# ----------------------------------------------------------------
	# plane space
	# ----------------------------------------------------------------
	def enterPlane(self, planeType):
		self.gotoPlane(planeType, self.position, self.direction)

	def leavePlane(self):
		self.gotoPlane(self.lastSpaceType, self.position, self.direction)

	def telportToPlaneEntry(self, srcEntityID):
		"""
		Exposed method
		"""
		if srcEntityID != self.id:
			return

		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_WM:
			ERROR_MSG("%s isn't in wm space type but %s currentlly." %
				(self.getName(), self.getCurrentSpaceType()))
			return

		if self.state != csdefine.ENTITY_STATE_FREE:
			ERROR_MSG("%s is not in free state currentlly but %s" %
				(self.getName(), self.state))
			return

		DEBUG_MSG("%s request to teleport to plane entry of wm %s" %
			(self.getName(), self.spaceType))

		space_script = g_objFactory.getObject(self.spaceType)
		space_script.telportRoleToEntry(self)

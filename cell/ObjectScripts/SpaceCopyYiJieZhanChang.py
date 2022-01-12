# -*- coding: gb18030 -*-
#python
import random
#bigworld
import BigWorld
#common
import csdefine
import csstatus
from bwdebug import INFO_MSG,ERROR_MSG

from SpaceCopy import SpaceCopy


# ս������Ӫ���졢�ء���
FACTION_TIAN					= csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN
FACTION_DI						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI
FACTION_REN						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN

# entity className
YI_JIE_TOWER			= 20254095		# ����
YI_JIE_STONE			= 20254098		# �����ʯ
YI_JIE_FACTION_FLAG		= 10121771		# ��Ӫ��

class SpaceCopyYiJieZhanChang( SpaceCopy ):
	# ���ս��
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.enterInfos = []
		

# ----------------------------------------------------------------
# �·���
# ----------------------------------------------------------------

	def getRandomEnterPos( self ):
		"""
		���ȡ��һ�������λ��
		"""
		return random.choice( self.enterInfos )
	
	def getFactionEnterPos( self, faction ) :
		"""
		ȡ����Ӫ�����
		"""
		if faction == FACTION_TIAN :
			return self.enterInfos[0][0]
		elif faction == FACTION_DI :
			return self.enterInfos[1][0]
		else :
			return self.enterInfos[2][0]
	
	def __isInCircle( self, pos, center, radius ) :
		"""
		�� pos �Ƿ���Բ��Բ��Ϊcenter,�뾶Ϊradius����
		"""
		dx = pos[0] - center[0]
		dy = pos[1] - center[1]
		if dx * dx + dy * dy < radius * radius :
			return True
		else :
			return False
	
	def onYiJieStoneCreate( self, selfEntity ) :
		"""
		�����ʯ����ʱ����
		"""
		selfEntity.battlegroundMgr.onYiJieStoneCreate()
	
	def onYiJieStoneDie( self, selfEntity, killerDBID ):
		"""
		�����ʯ����ʱ����
		"""
		selfEntity.battlegroundMgr.finalBlowStone( killerDBID )
	

# ----------------------------------------------------------------
# ���ط���
# ----------------------------------------------------------------

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )
		
		for idx, item in enumerate( section[ "Space" ][ "enterInfos" ].values() ):
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self.enterInfos.append( ( pos, direction ) )
			
		self.canAllianceTime = section[ "Space" ][ "canAllianceTime" ].asInt
		self.enrageTime = section[ "Space" ][ "enrageTime" ].asInt
		self.closeTime = section[ "Space" ][ "closeTime" ].asInt
		self.reviveTime = section[ "Space" ][ "reviveTime" ].asInt
		self.reviveRadius = section[ "Space" ][ "reviveRadius" ].asInt
		self.maxRage = section[ "Space" ][ "maxRage" ].asInt
		self.minLevel = section[ "Space" ][ "minLevel" ].asInt
	
	def initEntity( self, selfEntity ):
		"""
		��ʼ���Լ���entity������
		"""
		SpaceCopy.initEntity( self, selfEntity )
		
	
	def _createDoor( self, selfEntity ):
		"""
		����Door
		"""
		print "Create createDoor..."
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "Doormap" ].iteritems():
			print "create Door ", name
			BigWorld.createEntity( "SpaceDoorYiJieZhanChang", selfEntity.spaceID, otherDict["position"], (0, 0, 0), otherDict )
	
	def checkDomainLeaveEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ��뿪������
		"""
		# ֻ��ʹ�ø����ڴ�����ʱ�Ż�����������,�����κ�;�����޷��뿪��
		if not entity.popTemp( "leaveYiJieZhanChang", False ) :
			return csstatus.SPACE_MISS_LEAVE_CANNOT_TELEPORT_SPACE
		return csstatus.SPACE_OK
	
	def packedDomainData( self, entity ):
		"""
		����SpaceDomainYiJieZhanChangʱ�����ݲ���
		"""
		d = {}
		d[ "dbID" ] = entity.databaseID
		d[ "level" ] = entity.level
		if entity.teamMailbox :
			d[ "teamID" ] = entity.teamMailbox.id
		return d
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		pickDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		enterPos = entity.position
		if self.__isInCircle( enterPos, self.enterInfos[0][0], self.reviveRadius ) :
			entity.yiJieFaction = FACTION_TIAN
			pickDict[ "faction" ] = FACTION_TIAN
		elif self.__isInCircle( enterPos, self.enterInfos[1][0], self.reviveRadius ) :
			entity.yiJieFaction = FACTION_DI
			pickDict[ "faction" ] = FACTION_DI
		elif self.__isInCircle( enterPos, self.enterInfos[2][0], self.reviveRadius ) :
			entity.yiJieFaction = FACTION_REN
			pickDict[ "faction" ] = FACTION_REN
		else :
			#ERROR_MSG( "Role[databaseID : %s] enter error position. " % entity.databaseID )
			pickDict[ "faction" ] = FACTION_REN
		
		return pickDict
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		����
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEMPORARY_FACTION )
		
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		�뿪
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onRoleDie( self, role, killer ):
		"""
		ĳrole�ڸø���������
		"""
		if not killer :
			return
		killerType = killer.getEntityType()
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
			killer = killer.getOwner().entity
		
		killerDBID = 0
		killerName = ""
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			killerDBID = killer.databaseID
			killerName = killer.playerName
		elif killer.isEntityType( csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER ) :
			killerName = killer.uname
		role.client.yiJieSetReviveInfo( self.reviveTime, killerName )
		role.getCurrentSpaceBase().cell.onRoleBeKill( tuple( role.position ), role.databaseID, killerDBID, killerType )

	def kickAllPlayer( self, selfEntity ):
		"""
		��������������߳�
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].yiJieLeaveSpace()
			else:
				e.cell.yiJieLeaveSpace()


# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *

import csdefine
import csconst
import csstatus

from SpaceDomain import SpaceDomain

class SpaceDomainCampTurnWar( SpaceDomain ):
	"""
	��ᳵ��սspace����
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		Define method.
		����һ��entity��ָ����space��
		
		@type position : VECTOR3
		@type direction : VECTOR3
		@param baseMailbox: entity��base mailbox
		@type baseMailbox : MAILBOX
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT
		"""
		BigWorld.globalData[ "CampMgr" ].turnWar_onEnterCampTurnWarSpace( self, position, direction, baseMailbox, params )
		
	def onEnterCampTurnWarSpace( self, playerBaseMailBox, direction, enterKeyDict ):
		"""
		Define method.
		��ҵ�¼�ռ�
		"""
		teamID = enterKeyDict[ "teamID" ]
		isRight = teamID == enterKeyDict[ "team_right" ][ "teamID" ]
		if enterKeyDict["isFirstOrder"]:
			if isRight:
				position = self.getScript().right_fightPoint
			else:
				position = self.getScript().left_fightPoint
		else:
			if isRight:
				position = self.getScript().right_watchPoint
			else:
				position = self.getScript().left_watchPoint
		spaceItem = self.findSpaceItem( enterKeyDict, True )
		pickData = self.pickToSpaceData( playerBaseMailBox, params )
		spaceItem.enter( playerBaseMailBox, position, direction, pickData )
		
	def onLoginTurnWarSpace( self, playerBase, enterKeyDict, shouldCreate ):
		"""
		Define method.
		��ҵ�¼�ռ�
		
		@param shouldCreate : �ռ䲻����ʱ�Ƿ���Ҫ����
		@type shouldCreate : BOOL
		@param playerBase : ����ռ�Ľ�ɫbase mailbox
		@type playerBase : MAILBOX
		@param enterKeyDict : ���ɿռ�Ĳ����ֵ�
		@type enterKeyDict : PY_DICT
		"""
		spaceItem = self.findSpaceItem( enterKeyDict, shouldCreate )
		if spaceItem:
			spaceItem.logon( playerBase )
			playerBase.cell.setTemp( "isLogin", True )
			return
			
		playerBase.logonSpaceInSpaceCopy()
	
	def getSpaceItemByTeamID( self, teamID ):
		number = self.keyTo.get( teamID )
		if number is not None:
			return self.getSpaceItem( number )
		else:
			return None

	def createSpaceItem( self, params ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		# ���ڵ�ǰ�Ĺ����Ǵ����߲��ᣨҲ�����ܣ����Ŷӳ��ĸı���ı䣬
		# �����ǰ�����Ĵ������뿪�˶��飬Ȼ���Լ����ⴴ������ʱ��
		# �µĸ����ͻḲ�Ǿɵĸ��������ھɵĸ�������Ĵ����߻������ڵ���ң�
		# ���ɵĸ����ȸ�����´����ĸ����ȹر�ʱ����Ȼ�ᵼ���µĸ���ӳ�䱻ɾ����
		# ��ˣ�Ϊ�˱�������bug���ڴ����µĸ���ʱ�����Ǳ����Ȳ��ҵ�ǰ����Ƿ��Ѵ����˸�����
		# ���������Ҫ�ȰѾɸ����Ĵ�������0����û�д����߻򴴽��߶�ʧ�����ſ��Դ����µĸ�����
		teamID1 = params["team_left"]["teamID"]
		teamID2 = params["team_right"]["teamID"]
		spaceItem = SpaceDomain.createSpaceItem( self, params )
		self.keyToSpaceNumber[ teamID1 ] = spaceItem.spaceNumber
		self.keyToSpaceNumber[ teamID2 ] = spaceItem.spaceNumber
		return spaceItem
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
		"""
		params["login"] = True
		if params[ "teamID" ]:
			BigWorld.globalData[ "CampMgr" ].turnWar_onEnterCampTurnWarSpace( self, ( 0, 0, 0 ), ( 0, 0, 0 ), baseMailbox, params )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
	
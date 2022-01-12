# -*- coding: gb18030 -*-

# �Ǽʵ�ͼ
# by daiqinghui

# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
import Const
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#���ȫ���뿪�����󣬸���ø�����ɾ��
LEAVE_SPACECOPY_STAR_MAP			 = 100001


class SpaceCopyStarMap( SpaceCopy ) :
	"""
	�Ǽʵ�ͼ������
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.initAccumPoint() 				# ��ҽ����Ǽʵ�ͼ������һ��������
			skills = {}
			if self.className in player.mapSkills:
				skills = player.mapSkills[self.className]
			player.client.showPGControlPanel( skills )
			INFO_MSG( "%s enter copy space star." % player.getName() )
		else :
			INFO_MSG( "Something enter copy space star." )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.resetAccumPoint()							# ����뿪�Ǽʵ�ͼ������ֵ��0
			player.removeTemp("callPGDict")							# ���ٻ��б����
			player.removeTemp("pg_formation")
			player.client.closePGControlPanel()
			INFO_MSG( "%s leave copy space star." % player.getName() )
		else :
			INFO_MSG( "Something leave copy space star." )
			
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def infoSpaceCopyStar( self, leaveTime ):
		"""
		"""
		self.addTimer( leaveTime, 0, LEAVE_SPACECOPY_STAR_MAP )
		self.addTimer( 60, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == LEAVE_SPACECOPY_STAR_MAP:
			if len( self._players ) == 0:
				INFO_MSG( "all players have leaved SpaceCopy." )
				return
			for e in self._players:
				BigWorld.entities[e.id].gotoForetime()
				
		if userArg == Const.SPACE_COPY_CLOSE_CBID:
			if len( self._players ) != 0:
				INFO_MSG( "someOne in SpaceCopy, cannot close spece." )
				return
			self.base.closeSpace( True )
			return

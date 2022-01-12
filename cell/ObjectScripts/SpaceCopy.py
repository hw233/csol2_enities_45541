# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2007-10-07 07:23:49 phw Exp $

"""
"""
import BigWorld
import csstatus
import Const
from bwdebug import *
from Space import Space

class SpaceCopy( Space ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Space.__init__( self )
		
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		Space.load( self, section )
		
		#spaceSec = section["Space"]

	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		"""
		#�������  packedDomainDataInTo ��д�ű�ʱ��Ӧ�ö�Ӧ���������
		�������10��
		params = self.packedDataInTo( player )
		if params[ "level" ] < 10:
			return csstatus.SPACE_MISS_LEVELLACK
		��ĳ����
		if not entity.getTeamMailbox():
			return csstatus.SPACE_MISS_NOTTEAM
		�����ж�
		if not entity.corpsID:
			return csstatus.SPACE_MISS_NOTCORPS
		��Ʒ�ж�
		for name, bag in entity.kitbags.items():
			if bag.find2All( self.__itemName ):
				if self.val == self.__itemName:
					return csstatus.SPACE_OK
		return csstatus.SPACE_MISS_NOTITEM
		"""
		return csstatus.SPACE_OK
		
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		params = Space.packedDomainData( self, entity )
		params[ 'dbID' ] = entity.databaseID
		params[ 'spaceKey' ] = entity.databaseID
		return params
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		pickDict = Space.packedSpaceDataOnEnter( self, entity )
		pickDict[ "isViewer" ] = entity.spaveViewerIsViewer()
		return pickDict
		
	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		pickDict = Space.packedSpaceDataOnLeave( self, entity )
		pickDict[ "isViewer" ] = entity.spaveViewerIsViewer()
		return pickDict
	
	def onEnterViewer( self, selfEntity, baseMailbox, params ):
		# �Թ۲��ߵ���ݽ��븱��
		pass
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		# �������ķ�ʽ���븱��
		Space.onEnter( self, selfEntity, baseMailbox, params )
		if params[ "databaseID" ] not in selfEntity._enterRecord:
			selfEntity._enterRecord.append( params[ "databaseID" ] )
		
	def onLeaveViewer( self, selfEntity, baseMailbox, params ):
		# �Թ۲��ߵ�����˳�����
		pass
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		# �������ķ�ʽ�˳�����
		playerEntity = BigWorld.entities.get( baseMailbox.id )
		if playerEntity:
			if playerEntity.queryTemp( 'leaveSpaceTime'):
				playerEntity.removeTemp( 'leaveSpaceTime')
			if playerEntity.leaveTeamTimer != 0:
				playerEntity.cancel( playerEntity.leaveTeamTimer )
				playerEntity.leaveTeamTimer = 0
		Space.onLeave( self, selfEntity, baseMailbox, params )

	def onConditionChange( self, params  ):
		"""
		define method
		���ڸ������¼��仯֪ͨ��
		�������¼��仯�����Ƕ���仯����һ�����ݵ���ɣ�Ҳ������һ����
		"""
		pass

	def eventHandle( self, selfEntity, eventID, params ):
		"""
		�������е��¼�
		"""
		pass
	
	def isViewer( self, params ):
		# �жϵ�ǰ��������Ƿ��ǹ۲���
		if params.get( "isViewer", False ):
			return True
			
		return False

	def onSpaceDestroy( self, selfEntity ):
		"""
		��space entity��onDestroy()����������ʱ�����˽ӿڣ�
		�ڴ����ǿ��Դ���һЩ���飬��Ѽ�¼���������ȫ�����͵�ָ��λ�õȣ�
		"""
		for e in selfEntity.spaceViewers:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
				
		Space.onSpaceDestroy( self, selfEntity )
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		�����ɢ
		"""
		pass
	
	def closeCopy( self, selfEntity, userArg = 0 ):
		"""
		�����ر�
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
		
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def kickAllPlayer( self, selfEntity ):
		"""
		��������������߳�
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_CLOSE:
			selfEntity.base.closeSpace( True )		# �رո���
		
		elif userArg == Const.SPACE_TIMER_ARG_KICK:
			self.kickAllPlayer( selfEntity )
		else:
			Space.onTimer( self, selfEntity, id, userArg )

	def onEntitySpaceGone( self, entity ):
		"""
		called when the space this entity is in wants to shut down. 
		"""
		Space.onEntitySpaceGone( self, entity )
		try:
			entity.spawnMB = None
		except:
			WARNING_MSG( " Entity %s ,id %i has now attribute 'SpawnMB' " % ( entity, entity.id  ) )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/10/03 07:42:22  phw
# ��������ת��һЩ���뵽entity SpaceCopy��
#
# Revision 1.1  2007/09/29 05:59:57  phw
# no message
#
# Revision 1.2  2007/09/24 08:30:17  kebiao
# add:onTimer
#
# Revision 1.1  2007/09/22 09:09:19  kebiao
# space�ű�������
#
# 
#

# -*- coding: gb18030 -*-

# 60 �����鸱��
# by hezhiming

# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
from SpaceCopy import SpaceCopy


class SpaceCopyPlotLv60( SpaceCopy ) :
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
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s enter copy plot lv60." % entity.getName() )
		else :
			INFO_MSG( "Something enter copy plot lv60." )

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
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s leave copy plot lv60." % entity.getName() )
		else :
			INFO_MSG( "Something leave copy plot lv60." )

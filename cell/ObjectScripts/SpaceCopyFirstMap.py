# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2007-10-07 07:23:49 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csconst
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyFirstMap( SpaceCopy ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		enterID = entity.queryTemp( "lineNumber", -1 )
		if enterID != -1:
			return { "spaceKey" : enterID }

		spaceLabel = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if spaceLabel == "xin_ban_xin_shou_cun":
			lineNumber = BigWorld.getSpaceDataFirstForKey( entity.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER )
			return { "spaceKey" : int(lineNumber) }
		return {}

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		lineNumber = selfEntity.params[ "lineNumber" ]
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER, lineNumber )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		selfEntity.base.onEnter( baseMailbox, params )
		func = getattr( baseMailbox.cell, "recordLastSpaceLineNumber" )
		if func:
			func( selfEntity.params[ "lineNumber" ] )
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		selfEntity.base.onLeave( baseMailbox, params )
		SpaceCopy.onLeave( self, selfEntity, baseMailbox, params )

#
# $Log: not supported by cvs2svn $
#

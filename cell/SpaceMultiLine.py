# -*- coding: gb18030 -*-
#
# $Id: SpaceNormal.py,v 1.49 2008-08-20 01:22:17 kebiao Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csconst
from bwdebug import *
from SpaceNormal import SpaceNormal

class SpaceMultiLine( SpaceNormal ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceNormal.__init__( self )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER, self.getLineNumber() )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MAX_LINE_NUMBER, self.getScript().maxLine )
		
	def getLineNumber( self ):
		"""
		���������������
		"""
		return self.params[ "lineNumber" ]
		
	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
	
		self.base.onEnter( baseMailbox, params )
		SpaceNormal.onEnter( self, baseMailbox, params )
		
		entity = BigWorld.entities.get( baseMailbox.id )
		if not entity:
			entity = baseMailbox.cell
			
		func = getattr( entity, "recordLastSpaceLineData" )
		if func:
			func( self.getLineNumber(), self.getScript().maxLine )

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		self.base.onLeave( baseMailbox, params )
		SpaceNormal.onLeave( self, baseMailbox, params )
				
#
# $Log: not supported by cvs2svn $
#
#
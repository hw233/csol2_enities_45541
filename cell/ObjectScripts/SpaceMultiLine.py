# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.10 2008-07-23 03:14:04 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csdefine
import csconst
from bwdebug import *
from Space import Space

class SpaceMultiLine( Space ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
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
		self.maxLine = section.readInt( "maxLine" )
		
	def packedDomainData( self, entity ):
		"""
		���಻����̳�����ӿڣ� ��̳�packedDomainData_
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		"""
		params = Space.packedDomainData( self, entity )
		lineNumber = entity.queryTemp( "lineNumber", -1 )
		ignoreFullRule = entity.queryTemp( "ignoreFullRule", False )
		currSpaceClassName = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		currSpaceLineNumber = entity.getCurrentSpaceLineNumber()
		
		# �����ָ���ߺ�����ӱ��
		if lineNumber != -1:
			params[ "lineNumber" ] = lineNumber
			
		# ������Ա����
		if ignoreFullRule:
			params[ "ignoreFullRule" ] = True
		
		params[ "currSpaceClassName" ] = currSpaceClassName
		params[ "currSpaceLineNumber" ] = currSpaceLineNumber
		params.update( self.packedMultiLineDomainData( entity ) )
		return params

	def packedMultiLineDomainData( self, entity ):
		"""
		virtual method.
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		return {}
		
		
#
# $Log: not supported by cvs2svn $
#

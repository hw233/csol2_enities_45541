# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.10 2007-09-24 07:38:39 phw Exp $

"""
Player Base for Space
"""
import time

import BigWorld
from bwdebug import *
import Language
# from SpaceConst import * ( �� import * ������������)
import csstatus
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objects = GameObjectFactory.instance()

class SpaceFace:
	"""
	Player Base
	"""
	def __init__( self ):
		pass

	def enterSpace( self, spaceType, position, direction, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@param spaceType:��ͼ��� "yanhuang",...
		@type spaceType : String,
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		result = g_objects.getObject( spaceType ).checkIntoDomainEnable( self ) #ֱ���ҵ�������Ӧ�ı��ؽű�����domain�����ж�
		if result == csstatus.SPACE_OK:
			self.spaceManager.teleportEntity( spaceType, position, direction, self, params )
		else:
			INFO_MSG( "enter domain condition different:", result )
			self.client.spaceMessage( result )

	def logonSpace( self ):
		"""
		define method.
		�������
		���ã�
		�������ʱ������֪ͨspaceManager
		"""
		spaceType = self.cellData["spaceType"]

		space = g_objects.getObject( spaceType )
		assert space != None, "space %s not found!" % spaceType
		result = space.checkIntoDomainEnable( self ) #ֱ���ҵ�������Ӧ�ı��ؽű�����domain�����ж�
		assert result != None, "space %s not found!" % spaceType
		if result == csstatus.SPACE_OK:
			self.spaceManager.teleportEntityOnLogin( spaceType, self, space.packedDomainData( self ) )
		else:
			INFO_MSG( "login domain condition different:", result )
			self.client.spaceMessage( result )

	def logonSpaceInSpaceCopy( self ):
		"""
		define method.
		�������ʱ��������ȥ��������߻��������ʱ�Ը�������½
		"""
		space = g_objects.getObject(self.cellData["spaceType"])
		assert space != None, "space %s not found!" % self.cellData["spaceType"]
		space.emplaceRoleOnLogon(self)

	def createCellFromSpace( self, spaceCell ):
		"""
		define method.
		��spaceCell�ϴ���roleCell
		@param spaceCell:	�ռ�cell
		@type spaceCell:	mailbox
		"""
		self.createCellEntity( spaceCell )

	def gotoSpace( self, space, position, direction = (0, 0 ,0) ):
		"""
		define method.
		���͵��µĳ�����λ��
			@param space	:	Ŀ�ĳ�����ʶ
			@type space		:	string
			@param position	:	Ŀ�ĳ���λ��
			@type position	:	vector3
			@param direction:	����ʱ����
			@type direction	:	vector3
		"""
		self.cell.gotoSpace( space, position, direction )

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
		self.cell.gotoSpaceLineNumber( space, lineNumber, position, direction )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2007/09/22 09:07:10  kebiao
# ���µ�����space���
#
# Revision 1.7  2007/06/14 09:24:19  huangyongwei
# SpaceConst �еĺ궨�屻�ƶ��� csstatus �У����Ҫ���� import
#
# Revision 1.6  2007/05/21 08:27:33  panguankong
# ����spaceDomainCondition�޸Ĵ���
#
# Revision 1.5  2007/05/14 07:04:07  phw
# ɾ�����õ�ģ������
#
# Revision 1.4  2007/05/11 07:51:11  phw
# method modified: createCellFromSpace(), param spaceBase removed
#
# Revision 1.3  2007/03/19 10:24:28  panguankong
# �޸�SPACE�ӿ�
#
# Revision 1.2  2007/03/19 09:18:44  panguankong
# �޸�space�ӿ�
#
# Revision 1.1  2006/11/01 08:51:37  panguankong
# ����˿ռ����ϵͳ
#
#
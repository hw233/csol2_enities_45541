# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyTeam.py,v 1.2 2008-01-28 06:06:39 kebiao Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopy import SpaceCopy

class SpaceCopyTeam( SpaceCopy ):
	"""
	����ƥ��SpaceDomainCopyTeam�Ļ�����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )

	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		d = { 'dbID' : entity.databaseID }
		d["teamID"] = entity.teamID		# ȡ������ʱ�Ķ���ID���������ֵ��Ϊ0��
		if entity.teamID:
			d["spaceKey"] = entity.teamID
		else:
			d["spaceKey"] = entity.databaseID
		# ע�������Ժ���ܻ���Ҫȡ���ѵ�dbid�������ڻ�û����Ҫ��ô���������ʱ����ע��
		return d

	def checkIntoDomainEnable( self, entity ):
		"""
		virtual method.
		���domain�Ľ�������
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		"""
		return csstatus.SPACE_OK

# SpaceNormal.py

# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.5 2008-04-16 05:50:45 kebiao Exp $

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

class SpaceCopyFirstMap( SpaceCopy ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, selfEntity, baseMailBox, params ):
		"""
		virtual method.
		��ҽ����˿ռ�
		@param baseMailbox: cell mailbox
		@type baseMailbox: mailbox
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "SpaceDomain_FirstMap" ].incPlayerAmount( selfEntity.spaceNumber )

	def onLeave( self, selfEntity, baseMailBox, params  ):
		"""
		virtual method.
		����뿪�ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "SpaceDomain_FirstMap" ].decPlayerAmount( selfEntity.spaceNumber )
		
# SpaceNormal.py

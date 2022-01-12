# -*- coding: gb18030 -*-
#
#$Id:$

"""
"""


import BigWorld
from bwdebug import *

import csdefine
import csconst
import csstatus

from SpaceDomain import SpaceDomain


class SpaceDomainWuDao( SpaceDomain ):
	"""
	������space����
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
		BigWorld.globalData[ "WuDaoMgr" ].onEnterWuDaoSpace( self, position, direction, baseMailbox, params )
		
		
	def onEnterWuDaoSpace( self, position, direction, shouldCreate, playerBase, enterKeyDict ):
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
		pickData = self.pickToSpaceData( playerBase, enterKeyDict )
		spaceItem.enter( baseMailbox, position, direction, pickData )
		
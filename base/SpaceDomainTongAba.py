# -*- coding: gb18030 -*-
#
#$Id:$

"""
2010.11
������̨��ֲΪ�����̨ by cxm
"""

import BigWorld
from bwdebug import *

import csdefine
import csconst
import csstatus

from SpaceDomain import SpaceDomain


class SpaceDomainTongAba( SpaceDomain ):
	"""
	�����̨��space����
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
			
	def createSpaceItem( self, enterKeyDict ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		# ���ڵ�ǰ�Ĺ����Ǵ����߲��ᣨҲ�����ܣ����Ŷӳ��ĸı���ı䣬
		# �����ǰ�����Ĵ������뿪�˶��飬Ȼ���Լ����ⴴ������ʱ��
		# �µĸ����ͻḲ�Ǿɵĸ��������ھɵĸ�������Ĵ����߻������ڵ���ң�
		# ���ɵĸ����ȸ�����´����ĸ����ȹر�ʱ����Ȼ�ᵼ���µĸ���ӳ�䱻ɾ����
		# ��ˣ�Ϊ�˱�������bug���ڴ����µĸ���ʱ�����Ǳ����Ȳ��ҵ�ǰ����Ƿ��Ѵ����˸�����
		# ���������Ҫ�ȰѾɸ����Ĵ�������0����û�д����߻򴴽��߶�ʧ�����ſ��Դ����µĸ�����
		tongDBID1 = enterKeyDict.get( "tongDBID1" )		# dbid����������֮��ص�ObjectScripts/SpaceCopy.py����ؽӿ�
		tongDBID2 = enterKeyDict.get( "tongDBID2" )
		spaceItem = SpaceDomain.createSpaceItem( self, enterKeyDict )
		self.keyToSpaceNumber[ tongDBID1 ] = spaceItem.spaceNumber
		self.keyToSpaceNumber[ tongDBID2 ] = spaceItem.spaceNumber
		return spaceItem
		
		
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
		BigWorld.globalData[ "TongManager" ].onEnterAbattoirSpace( self, position, direction, baseMailbox, params )
		
		
	def onEnterAbattoirSpace( self, shouldCreate, playerBase, enterKeyDict ):
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
		spaceItem = self.findSpaceItem( enterKeyDict, True )	# �����̨����spaceItem����ΪNone
		if enterKeyDict[ "isRight" ]:							# ȷ����������ڵ���̨λ��
			position = self.getScript().right_playerEnterPoint[ 0 ]
			direction = self.getScript().right_playerEnterPoint[ 1 ]
		else:
			position = self.getScript().left_playerEnterPoint[ 0 ]
			direction = self.getScript().right_playerEnterPoint[ 1 ]
			
		pickData = self.pickToSpaceData( playerBase, enterKeyDict )
		spaceItem.enter( playerBase, position, direction, pickData )
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""
		params[ "login" ] = True
		BigWorld.globalData[ "TongManager" ].onEnterAbattoirSpace( self, (0,0,0), (0,0,0), baseMailbox, params )	
			
			
	def onLoginAbattoirSpace( self, shouldCreate, playerBase, enterKeyDict ):
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
		if spaceItem:
			spaceItem.logon( playerBase )
			return
			
		playerBase.logonSpaceInSpaceCopy()
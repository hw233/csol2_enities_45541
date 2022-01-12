# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.8 2008-04-16 05:51:18 phw Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
import ECBExtend
import Language

class Space( GameObject ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		GameObject.__init__( self )
		self._spawnFile	=	""			 # ��ȡ�õ�ͼ�ĳ����������ļ�
		self.isDiffCampTeam = False							# �Ƿ�����ͬ��Ӫ��������
		self.bufferCount = 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initialized.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		GameObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "dirmapping", section["dirMapping"].asString )
		self.setEntityProperty( "timeon", section["TimeOn"].asInt )

		#self.bufferCount = section.readInt("spaceItemBuffers")


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		GameObject.load( self, section )
		self._spawnFile = section.readString("spawnFile") 								   # ��ָ����ͼ������
		self._spawnSection = Language.openConfigSection( self._spawnFile )
		if section.has_key( "DiffCampTeam" ):
			self.isDiffCampTeam = True

	def getSpaceSpawnFile( self, selfEntity ):
		"""
		��ȡ�������ļ�
		"""
		return self._spawnFile

	def getSpawnSection( self ):
		"""
		"""
		return self._spawnSection

	def onSpaceTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData ):
		"""
		domain�ҵ���Ӧ��spaceNormal��spaceNormal��ʼ����һ��entity������space��ʱ��֪ͨ
		"""
		baseMailbox.cell.teleportToSpace( position, direction, selfEntity.cell, selfEntity.spaceID )

	def onPlanesTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData, planesID ):
		"""
		domain�ҵ���Ӧ��spaceNormal��spaceNormal��ʼ����һ��entity������space��ʱ��֪ͨ
		λ�洫�ͣ���Ҫ��֪ͨ���Ͷ���Ŀͻ���
		"""
		baseMailbox.cell.teleportToPlanes( position, direction, selfEntity.cell, planesID )
	#------------------------------------------------------------------------------------------------------------------------------------

	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		return None		# {}


	def onEnter( self, selfEntity, cellMailBox, params ):
		"""
		virtual method.
		��ҽ����˿ռ�
		@param cellMailBox: cell mailbox
		@type cellMailBox: mailbox
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		pass

	def onLeave( self, selfEntity, cellMailBox, params  ):
		"""
		virtual method.
		����뿪�ռ�
		@param cellMailBox: ���mailbox
		@type cellMailBox: mailbox
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		pass

	def onCloseSpace( self, selfEntity ):
		"""
		virtual method.
		space�������ڽ���������ɾ��space,���������һЩ׼��ɾ��ʱҪ�������飻
		�˷�����Space entity���ã���SpaceNormal ʵ���ȣ���
		"""
		pass

	def checkIntoDomainEnable( self, entity ):
		"""
		virtual method.
		���domain�Ľ�������
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		"""
		return csstatus.SPACE_OK

	def emplaceRoleOnLogon(self, role):
		"""
		virtual method.
		��ҵ�½ʱ������ȷ�İ���λ��
		@param role: ���entityʵ��
		@type role : Role
		"""
		if role.cellData[ "spaceType" ] != role.cellData[ "lastSpaceType" ]:
			role.cellData[ "spaceType" ] = role.cellData[ "lastSpaceType" ]
			role.cellData[ "position" ] = role.cellData[ "lastSpacePosition" ]
			role.logonSpace()
		else:
			# ��ĳ������»�������ִ��� ���ͻ��˵�½��ͻ��˱�������δ��ת����һ�δ��ڵĳ���
			# ��ô��ʱ2��������¼����һ���� ���˳����ֲ�������½ �������ѭ��.
			DEBUG_MSG( "has a error! spaceType == lastSpaceType, login failed, again select revive to login !" )
			role.cellData[ "spaceType" ] = role.cellData[ "reviveSpace" ]
			role.cellData[ "position" ] = role.cellData[ "revivePosition" ]
			role.cellData[ "direction" ] = role.cellData[ "reviveDirection" ]
			role.logonSpace()

# SpaceNormal.py

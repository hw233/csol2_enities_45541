# -*- coding: gb18030 -*-

import re
from SpaceCopySingle import SpaceCopySingle


class SpaceCopyWM(SpaceCopySingle):

	def __init__(self):
		SpaceCopySingle.__init__(self)

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopySingle.load( self, section )
		self._spaceConfigInfo["revive_space"] = section.readString("revive_space")
		self._spaceConfigInfo["revive_position"] =\
			eval("(%s)" % re.sub(" +", ",", section.readString("revive_position")))
		self._spaceConfigInfo["revive_direction"] =\
			eval("(%s)" % re.sub(" +", ",", section.readString("revive_direction")))

	def onRoleRevive(self, role):
		"""
		�����λ�渴��ʱ���ô˽ӿ�
		@type	role:	Role Entity
		@param	role:	cell��Roleʵ��
		"""
		space_label = self._spaceConfigInfo["revive_space"]
		position = self._spaceConfigInfo["revive_position"]
		direction = self._spaceConfigInfo["revive_direction"]

		role.reviveOnSpace(space_label, position, direction)

	def telportRoleToEntry(self, role):
		"""
		�����λ�渴��ʱ���ô˽ӿ�
		@type	role:	Role Entity
		@param	role:	cell��Roleʵ��
		"""
		space_label = self._spaceConfigInfo["revive_space"]
		position = self._spaceConfigInfo["revive_position"]
		direction = self._spaceConfigInfo["revive_direction"]

		role.gotoSpace(space_label, position, direction)
	
	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		pickDict = {}
		pickDict[ "planesID" ] = entity.planesID
		pickDict[ "databaseID" ] = entity.databaseID
		pickDict[ "playerName" ] = entity.playerName
		return pickDict
	
	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopySingle.onLeave( self, selfEntity, baseMailbox, params )
		selfEntity.base.onLeave( baseMailbox, { "planesID":params["planesID"] } )

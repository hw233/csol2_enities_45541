# -*- coding: gb18030 -*-
#

from Function import Function
from ObjectScripts.GameObjectFactory import g_objFactory
import csdefine
import Math
import math
import random


class FuncQuestMonster( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.questID = section.readInt( 'param1' )
		self.content = section.readString( 'param2' )
		self.monsterClassName01 = section.readString( 'param3' )
		self.monsterClassName02 = section.readString( 'param4' )
		self.monsterClassName03 = section.readString( 'param5' )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		entity = BigWorld.entities.get( player.targetID )
		# ���ȡ��ɢ��
		rad = math.pi * 2.0 * random.random()

		entities = talkEntity.entitiesInRangeExt( 20.0, 'Monster' )
		entityClassNames = []
		for i in entities:
			entityClassNames.append( i.className )

		for iClassName in [ self.monsterClassName01, self.monsterClassName02, self.monsterClassName03 ]:
			if iClassName in entityClassNames:
				player.setGossipText( self.content )
				player.sendGossipComplete( talkEntity.id )
				return
			rad = math.pi * 2.0 * random.random()
			pos = Math.Vector3( entity.position )
			distance = 2 + 2 * random.random()
			pos.x += distance * math.sin( rad )
			pos.z += distance * math.cos( rad )
			g_objFactory.createEntity( iClassName, player.spaceID, pos, entity.direction, { "spawnPos" : tuple( pos ) } )

		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		quest = player.getQuest( self.questID )
		return quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH



#
# $Log: not supported by cvs2svn $
# Revision 1.11  2007/12/22 09:53:05  fangpengjun
# �����ͻ��˴򿪲ֿ�ӿ�
#
# Revision 1.10  2007/12/05 03:36:24  phw
# �������޷���ȷ�رտͻ��˶Ի������bug
#
# Revision 1.9  2007/11/07 09:36:03  huangyongwei
# < 		player.enterInventoryTrade( talkEntity.id )
#
# ---
# > 		player.enterTradeIV( talkEntity.id )
#
# Revision 1.8  2007/08/18 08:06:02  yangkai
# NPC���״������
#     - �Ż���NPC����״̬���ж�
#     - ��ؽӿ����˸ı�
#
# Revision 1.7  2007/06/14 09:58:54  huangyongwei
# ���������˺궨��
#
# Revision 1.6  2007/05/18 08:42:02  kebiao
# �޸�����param ΪtargetEntity
#
# Revision 1.5  2006/12/21 10:14:18  phw
# ȡ���˲������ֿ�򿪲�����Ҫ��������
#
# Revision 1.4  2006/02/28 08:13:07  phw
# no message
#
# Revision 1.3  2005/12/22 09:55:27  xuning
# no message
#
# Revision 1.2  2005/12/14 02:50:57  phw
# no message
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#

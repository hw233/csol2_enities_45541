# -*- coding: gb18030 -*-
#
# $Id: MonsterDropManager.py

"""
����������������
"""
import sys
import random
import BigWorld
import csdefine
import csconst
from bwdebug import *
from Love3 import g_rewards
from items.ItemDropLoader import SpecialDropLoader
g_SpecialDrop = SpecialDropLoader.instance()


class MonsterDropManager:
	"""
	�������Ĺ���
	"""
	_instance = None

	def __init__( self ):
		pass

	def getDropItems( self, scriptMonster, monster ):
		"""
		��ȡ�������Ʒ�б�
		@param scriptMonster : ����Ľű���ʵ��
		@param monster       : ����entityʵ��
		ע���б��д�ŵ�ֱ������Ʒʵ��
		"""
		dropInfos = scriptMonster.getEntityProperty( "drops" )
		luckyDrop = scriptMonster.getEntityProperty( "luckyDropOdds" )

		itemDrops = []
		# ����콵���е���
		luckyItemList = self.getLuckyBoxDropItems( monster )
		if luckyItemList:
			itemDrops.extend( luckyItemList )

		if dropInfos:
			for info in dropInfos:
				itemDrops.extend( self.dropItems( monster,info['dropType'],info['dropAmount'],info['dropOdds'] ) )
			if luckyDrop and random.random()*100 < luckyDrop:	# ��������� ��ô����һ�ε���
				for info in dropInfos:
					itemDrops.extend( self.dropItems( monster,info['dropType'],info['dropAmount'],info['dropOdds'] ) )

		return itemDrops

	def getLuckyBoxDropItems( self, monster ):
		"""
		�������
		"""
		itemList = []
		if not BigWorld.globalData.has_key("LuckyActivity"):
			return itemList
		dropKeys = BigWorld.globalData["LuckyActivity"]
		for dk, rewardID in dropKeys.iteritems():
			awarder = g_rewards.fetch( rewardID, monster )
			if not awarder is None:
				for item in awarder.items:
					item.set( "level", monster.level )
					itemList.append( item )
					DEBUG_MSG( "Lucky Drop(%s), item(%d)"%( dk, item.id ) )
		return itemList

	def getDropItemOwners( self, monster ):
		"""
		virtual method
		��ȡ������Ʒӵ����
		@param monster: ��ȫ�����ݶ�Ӧ�ļ̳���Monster��real Monster entityʵ��
		@type  monster: Monster
		@return :array of entityID, tuple like as [ entityID1,...]
		"""
		bootyOwner = monster.getBootyOwner()
		owners = []
		# ����ǳ������Ȩ�������ת����role ������ҳ�������������� �羭��
		# ��δ���Ӧ���Ǽ���ghost�������
		# bootyOwner( entityID, TeamID )
		if bootyOwner[0] != 0:
			e = BigWorld.entities[ bootyOwner[0] ]
			if e.isEntityType( csdefine.ENTITY_TYPE_PET ) :
				owner = e.getOwner()
				e = owner.entity
				if owner.etype == "MAILBOX" :
					bootyOwner = ( e.id, 0 )
				elif e.isInTeam():
					bootyOwner = ( 0, e.getTeamMailbox().id )
				else:
					bootyOwner = ( e.id, 0 )

		if bootyOwner[0] != 0:
			owners = [ bootyOwner[0], ]
		if bootyOwner[1] != 0:
			members = monster.searchTeamMember( bootyOwner[1], 100 )
			if len( members ) == 0:
				owners = []
			elif len( members ) >= 1:
				entity = members[0]
				if entity.pickUpState == csdefine.TEAM_PICKUP_STATE_FREE:
					owners = entity.getFreePickerIDs()
				elif entity.pickUpState == csdefine.TEAM_PICKUP_STATE_ORDER:
					owners = [ entity.getOrderPickerID( members ) ]
					entity.onChangeLastPickerNotify( members, owners[0] )

		return owners

	def dropItems( self,monster,index,amount,odds ):
		"""
		��ȡ����ĵ���
		"""
		dropList = []
		datas = g_SpecialDrop.getDropDatas()		#��ȡ������������
		instance = datas.get(index, None)
		if not instance:
			ERROR_MSG( "has no special drop type : %s, please check out in SpecialDropAmend.xml" % index )
			return []
		for time in xrange( amount ):
			if random.random() < odds:
				item = instance.getDropItem( monster)
				if item is None:		#itemIDΪ0��ʾû���ҵ��õȼ�Ӧ�õ������Ʒ
					continue
				#owner = self.getDropItemOwners( monster )
				dropList.append( item )
		return dropList

	@classmethod
	def instance( self ):
		if self._instance == None:
			self._instance = MonsterDropManager()
		return self._instance
# -*- coding: gb18030 -*-
#
# $Id: FuncWarehouse.py,v 1.12 2008-01-15 06:06:34 phw Exp $

"""
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
import csdefine
import items
import Const
import ItemTypeEnum
import sys

class FuncOnlineBenefit( Function ):
	"""
	�����ۼ�ʱ�佱��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.benefitItemList = []		# ������Ʒ��Ϣ�б�( itemID, amount )
		sParam = section.readString( "param1" )
		if sParam != "":
			for sItem in sParam.split( "," ):
				itemInfo = sItem.split( ";" )
				self.benefitItemList.append( ( int( itemInfo[0] ), int( itemInfo[1] ) ) )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.canBenefit():
			itemList = []
			for itemID, amount in self.benefitItemList:
				itemList.append( items.instance().createDynamicItem( itemID, amount ) )
			checkResult = player.checkItemsPlaceIntoNK_( itemList )
			if checkResult != csdefine.KITBAG_CAN_HOLD:
				player.setGossipText( cschannel_msgs.ON_LINE_GIFT_VOICE_0 % len( self.benefitItemList ) )
				player.sendGossipComplete( talkEntity.id )
			else:
				player.spellTarget( Const.BENEFIT_SKILL_ID, player.id )
				for item in itemList:
					player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCGIVE, reason = csdefine.ADD_ITEM_ONLINEBENEFI )
				player.resetBenefitTime()
				player.setGossipText( cschannel_msgs.ON_LINE_GIFT_VOICE_1 )
				player.sendGossipComplete( talkEntity.id )
		else:
			player.setGossipText( cschannel_msgs.ON_LINE_GIFT_VOICE_2 )
			player.sendGossipComplete( talkEntity.id )

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
		return True


class FuncOnlineBenefitCheck( Function ):
	"""
	���߽���ʱЧ��ѯ
	"""
	def __init__( self, function ):
		"""
		"""
		Function.__init__( self, function )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			ERROR_MSG( "player( %s ) request benefit,but talkEntity is None." % player.getName() )
			return
		restBenefitTime = player.getRestBenefitTime()
		if restBenefitTime > 0:		# �Ѿ����Ա�����
			player.setGossipText( cschannel_msgs.ON_LINE_GIFT_VOICE_3 )
			player.sendGossipComplete( talkEntity.id )
		else:
			restBenefitTime = abs( restBenefitTime )
			hour = int( restBenefitTime / 3600 )
			minut = int( ( restBenefitTime - hour * 3600 ) / 60 )
			second = int( restBenefitTime - hour * 3600 - minut * 60 )
			player.setGossipText( cschannel_msgs.ON_LINE_GIFT_VOICE_4 % ( hour, minut, second ) )
			player.sendGossipComplete( talkEntity.id )

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
		return True

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

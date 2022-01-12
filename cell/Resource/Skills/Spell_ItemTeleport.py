# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemTeleport.py,v 1.9 2008-08-09 01:53:04 wangshufeng Exp $

"""
���ͼ��ܻ���
"""

from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import csconst
import ItemTypeEnum
import sys
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
from PetFormulas import formulas

class Spell_ItemTeleport( Spell_Item, Spell_TeleportBase ):
	"""
	���;��ᣬ ������� ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		Spell_TeleportBase.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_TeleportBase.init( self, dict )

	def getIntonateTime( self , caster ):
		"""
		virtual method.
		��ȡ�������������ʱ�䣬������ʱ������б�Ҫ�����Ը��������߾��������ʱ����

		@param caster:	ʹ�ü��ܵ�ʵ�塣�����Ժ���չ����ĳЩ�츳��Ӱ��ĳЩ���ܵ�Ĭ������ʱ�䡣
		@type  caster:	Entity
		@return:		�ͷ�ʱ��
		@rtype:			float
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		if item.query( "ch_teleportRecord", 0 ) == 0:
			return 0

		return Spell_Item.getIntonateTime( self , caster )

	def useableCheck( self, caster, target ) :
		"""
		"""
		#�ü��ܶ��Լ�������
		state = Spell_TeleportBase.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		if caster.getState() == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_USE_TELEPORT_ON_FIGHTING
		if caster.getState() == csdefine.ENTITY_STATE_VEND:
			return csstatus.SKILL_USE_TELEPORT_ON_VEND
		if caster.id != target.getObject().id:
			return csstatus.SKILL_NOT_SELF_ENTITY
		
		# ���Ӷ԰�����ʱ��������� by mushuang
		
		# if ��������
		if caster.getNormalKitbagFreeOrderCount() == 0 :
			uid = caster.queryTemp( "item_using" )
			item = caster.getByUid( uid )
			amount = item.getAmount()
			# if amount > 1 ����ʹ��
			if amount > 1 :
				caster.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
				return

		return Spell_Item.useableCheck( self, caster, target )

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form order[%s]." %  uid )
			return

		info = item.query( "ch_teleportRecord", 0 )
		spaceType = caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		
		Spell_Item.updateItem( self , caster ) 

		if caster.getCurrentSpaceType() in [ csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_TOWER_DEFENSE, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
			caster.statusMessage( csstatus.SPACE_COPY_CANNOT_USE_ITEM_TELEPORT )
			return
		if info != 0:
			if info[0] == spaceType:
				caster.teleportToSpace( info[1], caster.direction, caster, -1 )
			else:
				caster.gotoSpace( info[0], info[1], caster.direction )
		else:
			if caster.getNormalKitbagFreeOrderCount() <= 0 and item.amount != 1:
				caster.statusMessage( csstatus.USE_ITEM_KITBAG_IS_FULL )
				return
			newItem = caster.createDynamicItem( 110109008 )
			#newItem = caster.createDynamicItem( "040201007" )
			if newItem is None: return
			if item.isBinded(): newItem.setBindType( ItemTypeEnum.CBT_PICKUP )
			newItem.set( "ch_teleportRecord", ( spaceType, tuple( caster.position ), ( 0, 0, 0 ) ) )
			caster.addItemAndNotify_( newItem, csdefine.ADD_ITEM_ITEMTELEPORT )
	


# $Log: not supported by cvs2svn $
# Revision 1.8  2008/07/16 03:49:12  yangkai
# �޸��˼����������Ʒ�Ĵ���
#
# Revision 1.7  2008/05/31 03:01:19  yangkai
# ��Ʒ��ȡ�ӿڸı�
#
# Revision 1.6  2008/04/19 08:19:49  yangkai
# �޸� �����༼�ܱ������ ��� ����
#
# Revision 1.5  2007/12/18 09:23:50  kebiao
# �Ż��˴���
#
# Revision 1.4  2007/12/18 08:34:23  kebiao
# ��������жϣ�  �ڴ��;��¼�������һ��ʹ�ò���������
#
# Revision 1.3  2007/12/18 07:55:21  kebiao
# no message
#
# Revision 1.2  2007/12/18 07:52:45  kebiao
# no message
#
# Revision 1.1  2007/12/18 07:50:00  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemCure.py,v 1.9 2008-06-13 02:09:46 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from bwdebug import *
from SpellBase import *
from Spell_Item import Spell_Item
import ItemTypeEnum
import csstatus
import csdefine

class Spell_ItemCure( Spell_Item ):
	"""
	ʹ�ã����ָ̻�����HP,MP1960�㡣
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def cureHP( self, caster, receiver, value ):
		"""
		����HP
		"""
		amendValue = int( value * ( 1 + receiver.queryTemp( "Item_cure_hp_amend_percent", 0 ) ) )
		m_addHp = receiver.addHP( amendValue )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.statusMessage( csstatus.SKILL_HP_BUFF_CURE, receiver.queryTemp( "bag_useItemName", "" ), m_addHp )
		elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
			#SKILL_HP_CURE_BUFF_PET:%sΪ��ĳ���ָ���%i������ֵ��
			receiver.statusMessage( csstatus.SKILL_HP_CURE_BUFF_PET, receiver.queryTemp( "bag_useItemName", "" ), m_addHp )

	def cureMP( self, caster, receiver, value ):
		"""
		����MP
		"""
		amendValue = int( value * ( 1 + receiver.queryTemp( "Item_cure_mp_amend_percent", 0 ) ) )
		m_addMp = receiver.addMP( amendValue )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			#%s�ָ�����%i�㷨��ֵ��
			receiver.statusMessage( csstatus.SKILL_MP_BUFF_CURE, receiver.queryTemp( "bag_useItemName", "" ), m_addMp )
		elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
			#%sΪ��ĳ���ָ���%i�㷨��ֵ��
			receiver.statusMessage( csstatus.SKILL_MP_CURE_BUFF_PET, receiver.queryTemp( "bag_useItemName", "" ), m_addMp )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not caster:
			return
			
		# ֻ����casterΪreal��ʱ���ִ�У� ��Ϊ���ģ��ᱻ����һЩģ��ʹ��
		# ����������ģ������receiver.receiveOnReal( caster.id, self )����receive����ʱcasterΪghost
		if not caster.isReal():
			return

		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		# �����ﲻ�����Լ����Ǳ���ʩ�� caster����real��˿�����ô��
		receiver.setTemp( "bag_useItemName", item.name() )
		

# $Log: not supported by cvs2svn $
# Revision 1.8  2008/05/31 03:01:19  yangkai
# ��Ʒ��ȡ�ӿڸı�
#
# Revision 1.7  2008/02/01 03:30:53  kebiao
# no message
#
# Revision 1.6  2008/02/01 02:03:15  kebiao
# no message
#
# Revision 1.5  2008/01/31 09:32:10  kebiao
# no message
#
# Revision 1.4  2008/01/31 09:11:18  kebiao
# �޸��˿��ܳ��ֵ�BUG
#
# Revision 1.3  2008/01/31 08:15:41  kebiao
# ֧�ְ�����Ʒ������ʾ ������Ϣ
#
# Revision 1.1  2008/01/31 07:07:05  kebiao
# �������ƻ���
#
# Revision 1.2  2007/12/04 08:31:21  kebiao
# ʹ�ü���Ч��ֵ
#
# Revision 1.1  2007/12/03 07:45:20  kebiao
# no message
#
#
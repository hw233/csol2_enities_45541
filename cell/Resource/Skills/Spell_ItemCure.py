# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemCure.py,v 1.9 2008-06-13 02:09:46 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from bwdebug import *
from SpellBase import *
from Spell_Item import Spell_Item
import ItemTypeEnum
import csstatus
import csdefine

class Spell_ItemCure( Spell_Item ):
	"""
	使用：立刻恢复自身HP,MP1960点。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def cureHP( self, caster, receiver, value ):
		"""
		治疗HP
		"""
		amendValue = int( value * ( 1 + receiver.queryTemp( "Item_cure_hp_amend_percent", 0 ) ) )
		m_addHp = receiver.addHP( amendValue )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.statusMessage( csstatus.SKILL_HP_BUFF_CURE, receiver.queryTemp( "bag_useItemName", "" ), m_addHp )
		elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
			#SKILL_HP_CURE_BUFF_PET:%s为你的宠物恢复了%i点生命值。
			receiver.statusMessage( csstatus.SKILL_HP_CURE_BUFF_PET, receiver.queryTemp( "bag_useItemName", "" ), m_addHp )

	def cureMP( self, caster, receiver, value ):
		"""
		治疗MP
		"""
		amendValue = int( value * ( 1 + receiver.queryTemp( "Item_cure_mp_amend_percent", 0 ) ) )
		m_addMp = receiver.addMP( amendValue )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			#%s恢复了你%i点法力值。
			receiver.statusMessage( csstatus.SKILL_MP_BUFF_CURE, receiver.queryTemp( "bag_useItemName", "" ), m_addMp )
		elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
			#%s为你的宠物恢复了%i点法力值。
			receiver.statusMessage( csstatus.SKILL_MP_CURE_BUFF_PET, receiver.queryTemp( "bag_useItemName", "" ), m_addMp )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not caster:
			return
			
		# 只有在caster为real的时候才执行， 因为这个模块会被其他一些模块使用
		# 而往往其他模块会存在receiver.receiveOnReal( caster.id, self )导致receive调用时caster为ghost
		if not caster.isReal():
			return

		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		# 在这里不管是自己还是别人施法 caster都是real因此可以这么做
		receiver.setTemp( "bag_useItemName", item.name() )
		

# $Log: not supported by cvs2svn $
# Revision 1.8  2008/05/31 03:01:19  yangkai
# 物品获取接口改变
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
# 修改了可能出现的BUG
#
# Revision 1.3  2008/01/31 08:15:41  kebiao
# 支持按照物品名称显示 治疗信息
#
# Revision 1.1  2008/01/31 07:07:05  kebiao
# 加入治疗基础
#
# Revision 1.2  2007/12/04 08:31:21  kebiao
# 使用技能效果值
#
# Revision 1.1  2007/12/03 07:45:20  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Change_Body.py,v 1.2 2008-08-14 02:32:06 zhangyuxing Exp $

"""
�ڹ涨λ��ʹ����Ʒ
"""

from SpellBase import *
import cschannel_msgs
import ShareTexts as ST
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csconst
from Spell_Item import Spell_Item

# ���ݽ�ɫ���Ա�ְҵ������Ʒ��param�����еõ��ʵ���ģ�����ID
param_map = {
	0:{
	16:"param1",		# սʿ
	32:"param2",		# ����
	48:"param3",		# ����
	64:"param4",		# ��ʦ
	},
	1:{
	16:"param5",
	32:"param6",
	48:"param7",
	64:"param8",
	},
}

class Spell_ItemChangeHeadAbout( Spell_Item ):
	"""
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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		# self.drawChangeBody( caster, receiver )
		uid = caster.queryTemp( "item_using" )
		item = caster.getItemByUid_( uid )
		if item:
			param = param_map[receiver.getGender()][receiver.getClass()]
			modnum = int(item.query( param ))
			receiver.setTemp( "headAboutModNum", modnum )
		Spell_Item.receive( self, caster, caster )
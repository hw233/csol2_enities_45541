# -*- coding: gb18030 -*-
#
# ���������䷽ʹ��

from bwdebug import *
from Spell_Item import Spell_Item
import random
import csstatus

MIN = 2
MAX = 5


class Spell_ItemScroll( Spell_Item ):
	"""
	ʹ��
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
	
	def useableCheck( self, caster, target ):
		"""
		"""
		targetObject = target.getObject()
		if hasattr( targetObject, "sc_canLearnSkill" ):
			if not targetObject.sc_canLearnSkill():
				caster.statusMessage( csstatus.SKILL_SPELL_SCROLL_SKILL_FULL )
				return csstatus.SKILL_NO_MSG
		return Spell_Item.useableCheck( self, caster, target )

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
		raFixedAttr = []
		for k, v in item.getExtraEffect().items():
			raFixedAttr.append( (k,v) )
		
		# �����ﲻ�����Լ����Ǳ���ʩ�� caster����real��˿�����ô��
		caster.sc_learnSkill( {"itemID":item.id, "raFixedAttr":raFixedAttr, "maxCount":random.randint(MIN,MAX),"quality":item.getQuality()} )


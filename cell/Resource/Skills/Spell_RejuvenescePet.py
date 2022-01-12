# -*- coding: gb18030 -*-
#
# $Id: Spell_322370.py,v 1.7 2008-04-10 03:25:50 kebiao Exp $

"""
implement pet item spell( ��ͯ�� ʹ�ã������������1����һ����� )
2007/11/30: writen by huangyongwei
"""

import csstatus
from PetFormulas import formulas
from Spell_Item import Spell_Item
import csdefine

class Spell_RejuvenescePet( Spell_Item ) :
	"""
	��ͯ������
	"""
	def __init__( self ) :
		Spell_Item.__init__( self )
		self.__catholiconType = csdefine.PET_GET_CATHOLICON		# ��������ʱ������д����Ӧ��������Ʒ���� setTemp ���õ�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		#��������ֻ��һ�ֻ�ͯ�� ��˵�ǰ��д���
		#self.__catholiconType = eval( "csdefine." + section.readString( "param0" ) )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		pet = caster.pcg_getActPet()
		if pet is None:
			caster.removeTemp( "item_using" )
			return
		Spell_Item.updateItem( self, caster )
		
	def useableCheck( self, caster, target ) :
		baseStatus = Spell_Item.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON :
			return baseStatus
		if not caster.pcg_hasActPet() :
			return csstatus.PET_EVOLVE_FAIL_NOT_CONJURED
		return csstatus.SKILL_GO_ON

	def getCatholiconType( self ):
		"""
		��û�ͯ���ͣ�Ĭ��Ϊ��ͨ��ͯ��
		"""
		return csdefine.PET_GET_CATHOLICON

	def receive( self, caster, receiver ):
		pet = caster.pcg_getActPet()
		if pet is None:
			return
		receiver.rejuvenesce( self.getCatholiconType() )
		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )
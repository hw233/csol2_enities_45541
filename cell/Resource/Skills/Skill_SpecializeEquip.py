# -*- coding: gb18030 -*-
#
# $Id: Skill_SpecializeEquip.py,v 1.4 2007-08-15 03:28:35 kebiao Exp $

"""
"""

from SpellBase import *
from Skill_Normal import Skill_Normal
import ItemTypeEnum

class Skill_SpecializeEquip( Skill_Normal ):
	"""
	��ͨװ����ì���ܵȣ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_Normal.__init__( self )
		self._itemType = 0		# װ������
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._itemType = eval( ( dict["NeedEquip"] if len( dict["NeedEquip"] ) > 0 else "" ) .strip(), None, ItemTypeEnum.__dict__ )	
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		item = ownerEntity.findEquipsByType( self._itemType )
		for it in item:
			it.unWield( ownerEntity )
		
		key = "specialize" + str( self._itemType )
		ownerEntity.setTemp( key, self._id )
		
		for it in item:
			it.wield( ownerEntity )

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		item = ownerEntity.findEquipsByType( self._itemType )
		for it in item:
			it.unWield( ownerEntity, update = False )
		
		key = "specialize" + str( self._itemType )
		ownerEntity.setTemp( key, 0 )
		
		for it in item:
			it.wield( ownerEntity, update = False )

		ownerEntity.calcDynamicProperties()
		
	def do( self, owner ):
		"""
		��ͨϵ�е�ͳһ�ӿ�
		
		@return: BOOL
		"""
		return True
		
	def undo( self, owner ):
		"""
		��ͨϵ�е�ͳһ�ӿ�
		"""
		pass
			
#
# $Log: not supported by cvs2svn $
# 
#
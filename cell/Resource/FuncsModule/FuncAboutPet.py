# -*- coding: gb18030 -*-
#
# $Id: FuncAboutPet.py,v 1.4 2008-06-19 07:49:25 fangpengjun Exp $

"""
ʵ���������صĶԻ�����
"""

import csdefine

# --------------------------------------------------------------------
# ����ϳ�
# --------------------------------------------------------------------
class FuncCombinePet :
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.pcg_dlgCombinePet( talkEntity )
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
		if player.pcg_dlgCanCombinePet() :
			return True
		return False


# --------------------------------------------------------------------
# ������ʯ
# --------------------------------------------------------------------
class FuncBuyGem :
	def __init__( self, param ):
		"""
		param format: ��

		@param param: ��ʵ�����Լ����͸�ʽ
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.ptn_dlgBuyTrainGem( talkEntity )
		player.gem_activateGem( talkEntity.id )

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
		if player.ptn_dlgAllownActivateTrainGem() :
			return True
		return False



# --------------------------------------------------------------------
# ���ﷱֳ
# --------------------------------------------------------------------
class FuncProcreatePet :
	def __init__( self, param ):
		"""
		param format: ��

		@param param: ��ʵ�����Լ����͸�ʽ
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.pft_dlgShowProcreateDialog( talkEntity )

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

# --------------------------------------------------------------------
# ��ȡ��ֳ��ɵĳ���
# --------------------------------------------------------------------
class FuncGetProcreatedPet :
	def __init__( self, param ):
		"""
		param format: ��

		@param param: ��ʵ�����Լ����͸�ʽ
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.pft_dlgTakeProcreatePet( talkEntity )

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

# --------------------------------------------------------------------
# ��������
# --------------------------------------------------------------------
class FuncHireStorage :
	def __init__( self, param ):
		"""
		param format: ��

		@param param: ��ʵ�����Լ����͸�ʽ
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.client.pst_openHire( talkEntity.id )

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
		if player.pst_dlgCanBeHired() :
			return True
		return False



# --------------------------------------------------------------------
# ����С�ֿ�
# --------------------------------------------------------------------
class FuncOpenStorage :
	def __init__( self, param ):
		"""
		param format: ��

		@param param: ��ʵ�����Լ����͸�ʽ
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.pst_dlgOpen( talkEntity )

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
		if player.pst_dlgCanBeOpen() :
			return True
		return False

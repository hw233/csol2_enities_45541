# -*- coding: gb18030 -*-
#
# $Id: PetTrainer.py,v 1.7 2008-08-01 11:19:59 wangshufeng Exp $

"""
This module implements the pet entity.

2007/07/17 : writen by huangyongwei
2007/10/24 : according to new version document, it is rewriten by huangyongwei
"""

from bwdebug import *
import csstatus
import csconst
import csdefine
import event.EventCenter as ECenter

class PetTrainer :
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		pass

	def ptn_activeCommonGem( self, index, remainTime ) :
		"""
		���þ��鱦ʯ

		@param remainTime : �ͻ���������ɵ�����ʱ��,������24Сʱ��С��3Сʱ
		"""
		for gem in self.__commonGems:	# �ж���Ӧindex�ı�ʯ�Ƿ��ѱ�����
			if gem.index == index:
				self.statusMessage( csstatus.PET_GEM_ACTIVATE_FAIL_ACTIVED )
				return
		if self.ptn_getComGemCount() + self.gem_getComGemCount() >= csconst.GEM_COUNT_UPPER:
			#self.statusMessage(),�Ѵﵽ�������õ�����
			return
		self.cell.ptn_hireCommonGem( index, remainTime )


	def ptn_inactiveCommonGem( self, index ):
		"""
		��ֹ���þ��鱦ʯ
		"""
		if not self.isPetTrainGemActive():
			return
		self.cell.ptn_inactivateCommonGem( index )


	# -------------------------------------------------
	def ptn_getTrainGem( self ) :
		return self.__trainGem

	def ptn_getCommonGems( self ) :
		gems = []
		for gem in self.__commonGems :
			gems.append( gem )
		return gems


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def ptn_onUpdateGemAttr( self, index, attrName, value ) :
		"""
		Define method.
		��ʯ���Ը��µ�ͳһ�ӿ�
		"""
		if index < 0 :
			self.__trainGem.onUpdateAttr( attrName, value )
		else :
			gem = self.ptn_getcomGemByIndex( index )
			if gem is not None:
				gem.onUpdateAttr( attrName, value )


	def ptn_loadComGem( self, index ):
		"""
		Define method.
		���þ��鱦ʯ�ɹ�֪ͨ

		index : ���õľ��鱦ʯ����
		"""
		self.statusMessage( csstatus.GEM_LOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_LOAD_PET_GEM", index )


	def ptn_offloadComGem( self, index ):
		"""
		Define method.
		ж�¾��鱦ʯ��֪ͨ
		"""
		ECenter.fireEvent( "EVT_ON_OFFLOAD_PET_GEM", index )


	def ptn_getComGemCount( self ):
		"""
		public
		��õ�ǰ��ҵļӳɾ��鱦ʯ����
		"""
		return len( self.__commonGems )


	def isPetTrainGemActive( self ):
		"""
		�жϳ��ﾭ�鱦ʯ�Ƿ񼤻�
		"""
		return self.gemActive & csdefine.GEM_PET_ACTIVE_FLAG


	def ptn_getcomGemByIndex( self, index ):
		"""
		��indexȡ����Ӧ��comGem
		"""
		comGem = None
		for gem in self.__commonGems:
			if gem.index == index:
				comGem = gem
				break
		return comGem

	def getPetGemExp( self ):
		"""
		��ȡ��ʯ�ϵľ���ֵ
		"""
		return self.__trainGem.EXP



#
# $Log: not supported by cvs2svn $
#
#
#
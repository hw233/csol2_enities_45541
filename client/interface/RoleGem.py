# -*- coding: gb18030 -*-
#
# $Id: RoleGem.py,v 1.1 2008-08-01 11:17:09 wangshufeng Exp $

"""
��ɫ���鱦ʯϵͳ��15:31 2008-7-21��wsf
"""

import time
import csdefine
import csstatus
import csconst
from bwdebug import *
import BigWorld

import event.EventCenter as ECenter

class RoleGem:
	"""
	��Ҿ��鱦ʯϵͳ
	"""
	def __init__( self ):
		"""
		��Ҵ�����ʯ��
		��ҿ�ʼ������������5���Ӹ���һ�α�ʯ����ֵ���ݡ���ʯ��ֵ��ʣ��ʱ��.
		�������ֹͣ��������ʣ��ʱ�䵽��ʱ��֪ͨ����������������ֵ��ֹͣ�������Ҹ��µ��ͻ��ˣ�
		�����������ʱ��������ڴ����ڼ���������˼���������ֵ������ش���ͬʱ֪ͨ���ͻ��ˡ�

		�����ȡ�ı�ʯ��
		�����ȡ��ʯ�󣬿ͻ�������������ܹ�ʹ�ñ�ʯ��ʱ�䣬��֪ͨ�����������ʵ���ܹ�ʹ�õ�ʱ�䡣
		��������timer����timer���ں�����ʯ���ڵĴ����ͻ��˱�����������޹ء�
		"""
		pass
		# self.gemActive,��Ҿ��鱦ʯϵͳ�Ƿ񱻼���ı�־���ұߵ�1λ��ʾ��Ҿ��鱦ʯ����2λ��ʾ��ҳ��ﾭ�鱦ʯ


	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if self.roleTrainGem.inTraining():
			self.roleTrainGem.startUpdateTimer()


	def onUpdateRoleGem( self, index, attrName, value ):
		"""
		Define method.
		��Ҵ������鱦ʯ����
		"""
		if index < 0:	# ������ʯ
			self.roleTrainGem.onUpdateAttr( attrName, value )
		else:			# ��ȡ���鱦ʯ��index��csdefine�ж���
			gem = self.gem_getcomGemByIndex( index )
			if gem is not None:
				gem.onUpdateAttr( attrName, value )


	def isRoleTrainGemActive( self ):
		"""
		�ж���Ҵ������鱦ʯ�Ƿ񼤻�
		"""
		return self.gemActive & csdefine.GEM_ROLE_ACTIVE_FLAG


	def gem_derive( self ):
		"""
		�ӱ�ʯ��ȡ����
		"""
		if not self.isRoleTrainGemActive():
			ERROR_MSG( "���( %s )���鱦ʯ��û������ɼ�ȡ���顣" % ( self.getName() ) )
		else :
			self.cell.gem_derive()

	def gem_hire( self, index, remainTime ):
		"""
		���þ��鱦ʯ
		"""
		self.cell.gem_hire( index, remainTime )


	def gem_stopTrain( self ):
		"""
		ֹͣ������
		"""
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û�������ֹͣ������" % ( self.getName() ) )
			return
		if not self.roleTrainGem.inTraining():
			self.statusMessage( csstatus.PET_TRAIN_STOP_FAIL_NOT_IN_TRAIN )
			return
		self.cell.gem_stopTrain()


	def gem_startTrain( self, trainType ):
		"""
		��ʼ������
		"""
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û���" % ( self.getName() ) )
			return
		self.cell.gem_startTrain( trainType )


	def gem_offload( self, index ):
		"""
		Define method.
		ж�±�ʯ
		"""
		self.statusMessage( csstatus.GEM_OFFLOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_OFFLOAD_ROLE_GEM", index )

	def gem_loadComGem( self, index ):
		"""
		Define method.
		���þ��鱦ʯ�ɹ�֪ͨ
		index : ���õľ��鱦ʯ����
		"""
		self.statusMessage( csstatus.GEM_LOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_LOAD_ROLE_GEM", index )

	def gem_getComGemCount( self ):
		"""
		�����ҵ�ǰ��ȡ�ľ��鱦ʯ����
		"""
		return len( self.roleCommonGem )


	def gem_getcomGemByIndex( self, index ):
		"""
		��indexȡ����Ӧ��comGem
		"""
		comGem = None
		for gem in self.roleCommonGem:
			if gem.index == index:
				comGem = gem
				break
		return comGem


	def set_gemActive( self, oldValue ):
		"""
		"""
	#	self.statusMessage( csstatus.GEM_LOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_EXP_GEM_ACRIVATED" )
		BigWorld.callback( 1, self.showGemPanel )


	def showGemPanel( self ):
		ECenter.fireEvent("EVT_ON_EXP_GEM_SHOW")
#
# $log:v$
#
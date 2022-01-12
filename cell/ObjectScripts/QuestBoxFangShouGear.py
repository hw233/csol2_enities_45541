# -*- coding: gb18030 -*-
#

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
import csdefine
from bwdebug import *
# ------------------------------------------------
# from cell
from QuestBox import QuestBox
import Const
# ------------------------------------------------

class QuestBoxFangShouGear( QuestBox ) :
	"""
	���ظ�������
	"""
	
	def __init__( self ) :
		QuestBox.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		QuestBox.initEntity( self, selfEntity )
		selfEntity.setTemp( "isStarted", False )
	
	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		��������Ļص�����ĳЩ���⼼�ܵ���
		
		@param spell: ����ʵ��
		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		# ����˴���ⲻͨ�������ʾ��Ҷ�ĳ������Ķ��������ˣ���ʱ��û�кõ���ʾ������
		if selfEntity.queryTemp( "isStarted", False ) :
			return
		
		selfEntity.setTemp( "isStarted", True )
		currentArea = self.getCurrentFangShouArea( selfEntity.position )
		selfEntity.getCurrentSpaceBase().cell.remoteScriptCall( "onFangShouGearStarting", ( currentArea, ) )
		
		QuestBox.onReceiveSpell( self, selfEntity, caster, spell )
	
	def getCurrentFangShouArea( self, pos ) :
		"""
		��ȡ��ǰ���ڷ��ظ�������
		"""
		z = pos.z
		currentArea = ""
		if z > Const.COPY_FANG_SHOU_AERA_POS_Z_FIRST :
			currentArea = Const.COPY_FANG_SHOU_AREA_FIRST
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_SECOND :
			currentArea = Const.COPY_FANG_SHOU_AREA_SECOND
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_THRID :
			currentArea = Const.COPY_FANG_SHOU_AREA_THRID
		else :
			currentArea = Const.COPY_FANG_SHOU_AREA_FORTH
		return currentArea
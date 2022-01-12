# -*- coding: gb18030 -*-
#
# $Id: TabSwitcher.py,v 1.7 2008-06-21 01:53:33 huangyongwei Exp $

"""
implement tab switcher class
2006/07/21: writen by huangyongwei
2009/04/09: rewriten byw huangyongwei
		    ȡ�� RootGUI �̳��� TabSwitcher
		    �޸�Ϊ��Ҫ�ڶ���ؼ�֮��ת������ʱ�ٴ���
		    ÿ���ؼ�������� onKeyDown �¼�ʱ������ת��������Ч
"""

from guis import *

class TabSwitcher( object ) :
	"""
	����ת����
	"""
	def __init__( self, pyCons = None ) :
		self.__pyCons = WeakList()						# Ҫ��ȡ������ӿؼ�
		if pyCons :
			self.addTabInControls( pyCons )

	def dispose( self ) :
		self.clearTabInControls()

	def __del__( self ) :
		if Debug.output_del_TabSwitcher :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addTabInControls( self, pyCons ) :
		"""
		���һ��Ҫ��ȡ����Ŀؼ�
		"""
		for pyCon in pyCons :
			self.addTabInControl( pyCon )

	def addTabInControl( self, pyCon ) :
		"""
		���һ��Ҫ��ȡ����Ŀؼ�
		"""
		if pyCon not in self.__pyCons :
			self.__pyCons.append( pyCon )
			pyCon.onKeyDown.bind( self.onKeyDown_ )

	def removeTabInControl( self, pyCon ) :
		"""
		ɾ��һ��Ҫ��ȡ����Ŀؼ�
		"""
		if pyCon not in self.__pyCons :
			ERROR_MSG( "pyCon is not in %s" % str( self ) )
		else :
			self.__pyCons.remove( pyCon )
			pyCon.onKeyDown.unbind( self.onKeyDown_ )

	def clearTabInControls( self ) :
		"""
		�������Ҫ��ȡ����Ŀؼ�
		"""
		for pyCon in self.__pyCons :
			pyCon.onKeyDown.unbind( self.onKeyDown_ )
		self.__pyCons.clear()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cancelCurrTabStop( self ) :
		"""
		ȡ����ǰ�ؼ������뽹��
		"""
		pyCon = self.pyTabInControl
		if not pyCon : return False
		pyCon.tabStop = False
		return True

	def __getCanBeTabInControls( self ) :
		"""
		��ȡ���п��Ի�ý���Ŀؼ�
		"""
		pyCons = []
		for pyCon in self.__pyCons :
			if not pyCon.rvisible : continue
			if not pyCon.enable : continue
			if not pyCon.canTabIn : continue
			pyCons.append( pyCon )
		return pyCons


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		��������ʱ�����ã����뱣֤��������Ƚػ񰴼���Ϣ��
		"""
		if mods == 0 and key == KEY_TAB :					# ������� TAB ��
			self.tabForward()								# ��ǰ�ƽ���
			return True
		elif mods == MODIFIER_SHIFT and key == KEY_TAB :	# ������� SHIFT �� TAB ��
			self.tabBackward()								# ����ƽ���
			return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def tabForward( self ) :
		"""
		ǰ�ƽ���
		"""
		pyCons = self.__getCanBeTabInControls()				# ��ȡ���п��Ի�ý���Ŀؼ�
		if not len( pyCons ) : return False					# �������Ϊ 0���򷵻� False
		pyCon = self.pyTabInControl
		if pyCon is None :									# �����ǰû�л�ý���Ŀؼ�
			pyCons[0].tabStop = True						# ���õ�һ���ؼ���ý���
			return True										# �������óɹ�
		if len( pyCons ) == 1 :								# ���ֻ��һ���ɻ�ȡ����ؼ�
			return True										# ��������
		index = pyCons.index( pyCon )						# ��õ�ǰ����ؼ�������
		nextIndex = ( index + 1 ) % len( pyCons )			# �����һ���ؼ�������
		pyCons[nextIndex].tabStop = True					# ������һ���ؼ���ý���
		return True

	def tabBackward( self ) :
		"""
		���ƽ���
		"""
		pyCons = self.__getCanBeTabInControls()				# ��ȡ���п��Ի�ý���Ŀؼ�
		if not len( pyCons ) : return False					# �������Ϊ 0���򷵻� False
		pyCon = self.pyTabInControl
		if pyCon is None :									# �����ǰû�л�ý���Ŀؼ�
			pyCons[0].tabStop = True						# ���õ�һ���ؼ���ý���
			return True										# �������óɹ�
		if len( pyCons ) == 1 :								# ���ֻ��һ���ɻ�ȡ����ؼ�
			return True										# ��������
		index = pyCons.index( pyCon )						# ��õ�ǰ����ؼ�������
		foreIndex = ( index - 1 ) % len( pyCons )			# �����һ���ؼ�������
		pyCons[foreIndex].tabStop = True					# ������һ���ؼ���ý���
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTabInControls( self ) :
		return self.__pyCons.list()

	def _getTabInControlCount( self ) :
		return self.__pyCons.count()

	# -------------------------------------------------
	def _getTabInControl( self ) :
		for pyCon in self.__pyCons :
			if pyCon.tabStop : return pyCon
		return None


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyTabInControls = property( _getTabInControls )								# ��ȡ���п��Ի�ý���Ŀؼ�
	tabInControlCount = property( _getTabInControlCount )						# ��ȡ���Ի�ý���ؼ�������
	pyTabInControl = property( _getTabInControl )								# ��ȡ��ǰ��ý���Ŀؼ���û���򷵻� None

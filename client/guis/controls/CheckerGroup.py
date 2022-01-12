# -*- coding: gb18030 -*-
#
# $Id: CheckerGroup.py,v 1.2 2008-06-21 01:39:48 huangyongwei Exp $

"""
implement radio button array
-- 2007/06/26: writen by huangyongwei( the model's old name: RadioButtonArray )
-- 2008/03/29: renamed to 'CheckGroup' by huangyongwei
-- 2008/06/18: rename to 'CheckerGroup' by huangyongwei
"""

from guis import *

class CheckerGroup( object ) :
	def __init__( self, *pyCheckers ) :
		self.__pyCheckers = []				# ��ѡ�пؼ��б�
		self.__events = []
		self.generateEvents_()

		self.addCheckers( *pyCheckers )

	def __del__( self ) :
		self.clearCheckers()
		self.__events = []
		if Debug.output_del_CheckerGroup :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		"""
		�����¼�
		"""
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		self.__onCheckChanged = self.createEvent_( "onCheckChanged" )		# ��ѡ�еĿؼ��ı�ʱ������

	@property
	def onCheckChanged( self ) :
		"""
		��ѡ�еĿؼ��ı�ʱ����������һ����������ʾ��ǰѡ�еĿؼ��������ǰû��ѡ�еĿؼ�����ò���Ϊ None
		"""
		return self.__onCheckChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onChackerChackChanged( self, pyChecker, checked ) :
		if checked :															# �����һ���ؼ���ѡ��
			for pyTmp in self.__pyCheckers :									# �ҳ�֮ǰ��ѡ�еĿؼ�
				if not pyTmp.checked : continue
				if pyTmp == pyChecker : continue								# ����ǵ�ǰ��Ҫѡ�еĿؼ��������
				pyTmp.onCheckChanged.unbind( self.__onChackerChackChanged )		# ���֮ǰѡ�пؼ��İ��¼����Է���ѭ��
				pyTmp.checked = False											# ��֮ǰѡ�еĿؼ�����Ϊδѡ��
				pyTmp.onCheckChanged.bind( self.__onChackerChackChanged )		# ���°�
				break
			self.onCheckChanged( pyChecker )									# �޸�ѡ�еĿؼ������¼�
		else :																	# ���ĳ���ؼ���ѡ�б�ȡ��
			self.onCheckChanged( None )											# ���� None �����¼�


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addChecker( self, pyChecker ) :
		"""
		���һ����ѡ�ؼ�
		@type				pyChecker : checkable Control
		@param				pyChecker : ��ѡ�еĿؼ����� checked ���ԣ�
		@rtype						  : bool
		@return					  	  : ��ӳɹ��򷵻� True
		"""
		if pyChecker in self.__pyCheckers :
			DEBUG_MSG( "the button has been set!" )
			return False
		self.__pyCheckers.append( pyChecker )
		pyChecker.onCheckChanged.bind( self.__onChackerChackChanged )
		return True

	def addCheckers( self, *pyCheckers ) :
		"""
		���һ���ѡ�пؼ�
		@type				pyCheckers : list
		@param				pyCheckers : һ��ɱ�ѡ�еĿؼ�
		@return						   : None
		"""
		for pyChecker in pyCheckers :
			self.addChecker( pyChecker )

	def removeChecker( self, pyChecker ) :
		"""
		ɾ��һ����ѡ�пؼ�
		@type				pyChecker : checkable Control
		@param				pyChecker : ��ѡ�еĿؼ����� checked ���ԣ�
		@rtype						  : bool
		@return					  	  : ɾ���ɹ��򷵻� True
		"""
		if pyChecker not in self.__pyCheckers :
			DEBUG_MSG( "the button has not in the button array!" )
			return False
		isRemoveChecked = pyChecker == self.pyCurrChecker
		pyChecker.onCheckChanged.unbind( self.__onChackerChackChanged )
		self.__pyCheckers.remove( pyChecker )
		if isRemoveChecked :
			self.onCheckChanged( None )
		return True

	def clearCheckers( self ) :
		"""
		������п�ѡ�пؼ�
		@return					  : None
		"""
		hasChecked = False
		for pyChecker in self.__pyCheckers :
			if pyChecker.checked : hasChecked = True
			pyChecker.onCheckChanged.unbind( self.__onChackerChackChanged )
		self.__pyCheckers = []
		if hasChecked :
			self.onCheckChanged( None )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCheckers( self ) :
		return self.__pyCheckers[:]

	def _getCount( self ) :
		return len( self.__pyCheckers )

	# -------------------------------------------------
	def _getCurrChecker( self ) :
		for pyChecker in self.__pyCheckers :
			if pyChecker.checked :
				return pyChecker
		return None

	def _setCurrChecker( self, pyChecker ) :
		if isDebuged :
			assert pyChecker in self.__pyCheckers, "%s is not my member!" % str( pyChecker )
		pyChecker.checked = True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyCheckers = property( _getCheckers )								# ��ȡ���п�ѡ�еĿؼ�
	count = property( _getCount )										# ��ȡ��ѡ�пؼ�������
	pyCurrChecker = property( _getCurrChecker, _setCurrChecker )		# ��ȡ��ǰѡ�еĿؼ�

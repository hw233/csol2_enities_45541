# -*- coding: gb18030 -*-
#
# $Id: SelectorGroup.py,v 1.3 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement control arry, controls in the array must can be selected

2007/3/17 : writen by huangyongwei
"""

from guis import *

class SelectorGroup( object ) :
	def __init__( self, *pySelectors ) :
		self.__pySelectors = []						# ��ѡ�пؼ��б�
		self.__events = []
		self.generateEvents_()

		self.addSelectors( *pySelectors )

	def __del__( self ) :
		self.clearSelectors()
		self.__events = []
		if Debug.output_del_SelectorGroup :
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
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )		# ��ѡ�еĿؼ��ı�ʱ������

	@property
	def onSelectChanged( self ) :
		"""
		��ѡ�еĿؼ��ı�ʱ����������һ����������ʾ��ǰѡ�еĿؼ��������ǰû��ѡ�еĿؼ�����ò���Ϊ None
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelectChanged_( self, pySelector, selected ) :
		"""
		��ĳ�� selector ѡ��״̬�ı�ʱ������
		"""
		if selected :
			for pyTmp in self.__pySelectors :								# �ҳ�֮ǰ��ѡ�еĿؼ�
				if not pyTmp.selected : continue
				if pyTmp == pySelector : continue							# ����ǵ�ǰ��Ҫѡ�еĿؼ��������
				pyTmp.onSelectChanged.unbind( self.onSelectChanged_ )		# ���֮ǰѡ�пؼ��İ��¼����Է���ѭ��
				pyTmp.selected = False										# ��֮ǰѡ�еĿؼ�����Ϊδѡ��
				pyTmp.onSelectChanged.bind( self.onSelectChanged_ )			# ���°�
				break
			self.onSelectChanged( pySelector )								# �޸�ѡ�еĿؼ������¼�
		else :
			self.onSelectChanged( None )									# �޸�ѡ�еĿؼ������¼�


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addSelector( self, pySelector ) :
		"""
		���һ����ѡ�ؼ�
		@type				pySelector : checkable Control
		@param				pySelector : ��ѡ�еĿؼ����� selected ���ԣ�
		@rtype						   : bool
		@return					  	   : ��ӳɹ��򷵻� True
		"""
		if pySelector in self.__pySelectors :
			DEBUG_MSG( "the button has been set!" )
			return False
		if hasattr( pySelector, "selectable" ) :
			pySelector.selectable = True
		self.__pySelectors.append( pySelector )
		pySelector.onSelectChanged.bind( self.onSelectChanged_ )
		return True

	def addSelectors( self, *pySelectors ) :
		"""
		���һ���ѡ�пؼ�
		@type				pySelectors : list
		@param				pySelectors : һ��ɱ�ѡ�еĿؼ�
		@return							: None
		"""
		for pySelector in pySelectors :
			self.addSelector( pySelector )

	def removeSelector( self, pySelector ) :
		"""
		ɾ��һ����ѡ�пؼ�
		@type				pySelector : checkable Control
		@param				pySelector : ��ѡ�еĿؼ����� selected ���ԣ�
		@rtype						   : bool
		@return					  	   : ɾ���ɹ��򷵻� True
		"""
		if pySelector not in self.__pySelectors :							# Ҫɾ���Ŀؼ������б���
			DEBUG_MSG( "the selector has not in the selector array!" )
			return False													# ����ɾ��ʧ��
		isRemoveChecked = pySelector == self.pyCurrSelector					# ɾ���Ŀؼ��Ƿ��ǵ�ǰ��ѡ�еĿؼ�
		pySelector.onSelectChanged.unbind( self.onSelectChanged_ )			# ��ѡ���¼�
		self.__pySelectors.remove( pySelector )								# ���б���ɾ��
		if isRemoveChecked : self.onSelectChanged( None )					# ���ɾ���Ŀؼ���ǡ���Ǳ�ѡ�еĿؼ������� None ����ѡ�иı�
		return True															# ����ɾ���ɹ�

	def clearSelectors( self ) :
		"""
		������п�ѡ�пؼ�
		@return					  : None
		"""
		hasSelected = False													# ��¼�Ƿ���ѡ�еĿؼ�
		for pySelector in self.__pySelectors :								# ѭ�����ؼ�
			if pySelector.selected : hasSelected = True						# ���������ѡ�еĿؼ������� hasSelected Ϊ True
			pySelector.onSelectChanged.unbind( self.onSelectChanged_ )		# ȡ���ؼ���ѡ�а��¼�
		self.__pySelectors = []												# ��տؼ��б�
		if hasSelected :													# ���֮ǰ��ѡ�еĿؼ�
			self.onSelectChanged( None )									# ���� None ����ѡ�иı��¼�


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelectors( self ) :
		return self.__pySelectors[:]

	def _getCount( self ) :
		return len( self.__pySelectors )

	# -------------------------------------------------
	def _getCurrSelector( self ) :
		for pySelector in self.__pySelectors :
			if pySelector.selected :
				return pySelector
		return None

	def _setCurrSelector( self, pySelector ) :
		if isDebuged :
			assert pySelector in self.__pySelectors, "%s is not my member!" % str( pySelector )
		pySelector.selected = True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pySelectors = property( _getSelectors )								# ��ȡ���п�ѡ�еĿؼ�
	count = property( _getCount )										# ��ȡ��ѡ�пؼ�������
	pyCurrSelector = property( _getCurrSelector, _setCurrSelector )		# ��ȡ��ǰѡ�еĿؼ�

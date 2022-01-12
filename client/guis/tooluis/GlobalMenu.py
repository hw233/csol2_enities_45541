# -*- coding: gb18030 -*-

# �ò˵����κεط���Ҫʱ����������괦������
# �˵��ṹ�ɵ����߰���Լ���Ĺ������ж��ơ�
# by ganjinxing 2010-11-03

import weakref
from bwdebug import *
from cscollections import Queue
from AbstractTemplates import Singleton
import event.EventCenter as ECenter

from guis.uidefine import MIStyle
from guis.controls.ContextMenu import ContextMenu, DefMenuItem


class GlobalMenu( Singleton ) :

	def __init__( self ) :
		self.__pyMenu = None
		self.__releaseWhenHide = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onBeforePopup( self ) :
		"""
		Ϊ�˲˵��ܵ��������������Ҫ����True
		"""
		return True

	def __onMenuItemClicked( self, pyMuItem ) :
		"""
		�˵���������
		"""
		try :
			pyMuItem.handler()
		except :
			EXCEHOOK_MSG()

	def __onHide( self ) :
		"""
		�رղ˵�
		"""
		if self.__releaseWhenHide :
			self.__pyMenu = None
			self.__class__.releaseInst()

	def __popup( self, struct, pyOwner = None ) :
		"""
		�����˵�
		"""
		if self.__construct( struct ) :
			self.__pyMenu.popup( pyOwner )
		else :
			self.__onHide()
			ERROR_MSG( "Build menu fail, please contact the relative person!" )

	def __construct( self, struct ) :
		"""
		���ݸ��������ݣ������˵�
		@param		struct : �˵���ṹ
							(
							  ( muItemText1, handler1 ),					# �˵���1��
							  ( muItemText2, (								# �˵���2
							  		( subMuItemtext21, handler21 ),			# �˵���2���Ӳ˵���
							  		), ),
							  ( "SPLITTER", 1 )								# ����1���ָ���
							  ( muItemText3, (								# �˵���3
							  		( subMuItemtext31, handler31 ),			# �˵���3���Ӳ˵�1��
							  		( subMuItemtext32, (					# �˵���3���Ӳ˵�2��
							  			( subMuItemtext321, handler321 ),	# �˵���3���Ӳ˵�2���Ӳ˵�1��
							  			), ),
							  		), ),
							  ( muItemText4, handler4 ),					# �˵���4
							)
							ע�⣺ÿһ���˵����һ����Ԫ��
		@type		struct : tuple
		"""
		if self.__pyMenu :
			self.__releaseWhenHide = False
			self.__pyMenu.clear()
		else :
			self.__pyMenu = ContextMenu()
			self.__pyMenu.onItemClick.bind( self.__onMenuItemClicked )
			self.__pyMenu.onAfterClose.bind( self.__onHide )
			self.__pyMenu.onBeforePopup.bind( self.__onBeforePopup )
		self.__releaseWhenHide = True
		return self.__buildMuItems( struct )

	def __buildMuItems( self, struct ) :
		"""
		���ɲ˵���
		"""
		if self.__pyMenu is None : return False
		if len( struct ) == 0 : return False

		def buildMI( parent, label, style = MIStyle.COMMON ) :
			muItem = DefMenuItem( label, style )
			parent.add( muItem )
			return muItem

		muQueue = Queue()
		muQueue.enter( ( self.__pyMenu, struct ) )
		while muQueue.length() :
			muParent, muItems = muQueue.leave()
			for muLabel, muKernel in muItems :
				if type( muLabel ) is not str :
					ERROR_MSG( "Error struct of menu items:", \
						str( muLabel ), str( muKernel ) )
					return False
				elif muLabel == "SPLITTER" :									# �����ָ���
					if type( muKernel ) is int :
						for i in xrange( muKernel ) :
							buildMI( muParent, "", MIStyle.SPLITTER )
					else :
						ERROR_MSG( "Error struct of menu items:", \
							str( muLabel ), str( muKernel ) )
						return False
				elif callable( muKernel ) :										# �����˵���
					subMuItem = buildMI( muParent, muLabel )
					subMuItem.handler = muKernel
				elif type( muKernel ) is tuple :								# �Ӳ˵������
					subMuItem = buildMI( muParent, muLabel )
					muQueue.enter( ( subMuItem.pySubItems, muKernel ) )
				else :
					ERROR_MSG( "Error struct of menu items:", \
						str( muLabel ), str( muKernel ) )
					return False
		return True


	# ----------------------------------------------------------------
	# class methods
	# ----------------------------------------------------------------
	@classmethod
	def registerEvents( SELF ) :
		ECenter.registerEvent( "EVT_ON_POPUP_GLOBAL_MENU", SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.inst.__popup( *args )


GlobalMenu.registerEvents()

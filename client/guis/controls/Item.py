# -*- coding: gb18030 -*-
#
# $Id: Item.py,v 1.27 2008-08-25 09:03:53 huangyongwei Exp $

"""
implement object/skill/quick base item class

2006.05.09: writen by huangyongwei
"""
"""
composing :
	GUI.Window
"""

from guis import *
from guis.controls.Control import Control

class Item( Control ) :
	"""
	��Ʒ�����ܡ�buff �ȸ��ӵĻ���
	"""
	def __init__( self, item = None, pyBinder = None ) :
		Control.__init__( self, item, pyBinder )
		self.__index = 0							# Item �ڸ��б��е�����
		self.__selectable = False					# Item �Ƿ���Ա�ѡ��
		self.__selected = False						# Item �Ƿ���ѡ��״̬
		self.__description = ""						# Item ��������Ϣ
		self.__initialize( item )					# ��ʼ�� Item

		self.__locked = False						# Item �Ƿ�������״̬
		self.__itemInfo = None						# Item ��Ӧ�ĵײ���Ϣ
		self.__mouseHighlight = True				# ������ʱ���Ƿ������ʾ item
		self.__isLocked = False						# Item �Ƿ񱻸ı���ɫ

	def subclass( self, item, pyBinder = None ) :
		Control.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def dispose( self ) :
		self.__itemInfo = None
		Control.dispose( self )

	def __del__( self ) :
		if Debug.output_del_Item :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )			# Item ��ѡ��ʱ����

	@property
	def onSelectChanged( self ) :
		"""
		Item ��ѡ��ʱ����
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.focus = False
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		Item.clear( self )

	# -------------------------------------------------
	def __select( self ) :
		"""
		ѡ�� Item
		"""
		if self.selected : return
		self.__selected = True
		self.setState( UIState.SELECTED )
		self.onSelectChanged( True )

	def __deselect( self ) :
		"""
		ȡ��ѡ��
		"""
		if not self.selected : return
		self.__selected = False
		self.setState( UIState.COMMON )
		self.onSelectChanged( False )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		"""
		��������ʱ�����ã���������ʾ����
		"""
		#self.update( self.itemInfo ) # ÿ����ʾ������ʱ�򶼸���һ�£���֤���������µġ����������Ǵ�ģ���Ϊ�п��ܸ��ǵ��ⲿ���޸ġ�
		dsp = self.description
		if dsp is None : return
		if dsp == [] : return
		if dsp == "" : return
		toolbox.infoTip.showItemTips( self, dsp )

	def onDescriptionHide_( self ) :
		"""
		������뿪ʱ�����ã��������������
		"""
		toolbox.infoTip.hide( self )

	# -------------------------------------------------
	def onStateChanged_( self, state ) :
		pass

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		self.onDescriptionHide_()
		return True

	def onRMouseDown_( self, mods ) :
		Control.onRMouseDown_( self, mods )
		self.onDescriptionHide_()
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		self.setState( UIState.HIGHLIGHT )
		if self.__mouseHighlight :
			toolbox.itemCover.highlightItem( self )
		if not BigWorld.isKeyDown( KEY_MOUSE0 ) :
			self.onDescriptionShow_()
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		self.setState( UIState.COMMON )
		toolbox.itemCover.normalizeItem()
		self.onDescriptionHide_()
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if self.itemInfo is None :
			return True
		return Control.onDragStart_( self, pyDragged )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		"""
		ͨ���ײ�� itemInfo ���� Item ��Ϣ
		"""
		self.__itemInfo = itemInfo
		if itemInfo is None :
			self.onDescriptionHide_()
			self.clear()
		else :
			self.icon = itemInfo.icon
			self.description = itemInfo.description

	# ---------------------------------------
	def lock( self ) :
		"""
		������Ʒ/���ܸ���
		"""
		self.__isLocked = True
		#self.focus = False
		#self.crossFocus = False
		self.dragFocus = False
		self.dropFocus = False

	def unlock( self ) :
		"""
		��������
		"""
		self.__isLocked = False
		#self.focus = True
		#self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True

	def _getLock( self ) :
		"""
		��ȡ������ɫ�Ƿ񱻸ı�
		"""
		return self.__isLocked

	def clear( self ) :
		"""
		��� Item ��Ϣ
		"""
		self.__itemInfo = None
		self.icon = ( "", None )
		self.description = ""
		if self.__selectable :
			self.selected = False

	# -------------------------------------------------
	def setState( self, state ) :
		"""
		���� Item ��״̬
		"""
		if state == UIState.COMMON and self.selected :
			self.onStateChanged_( UIState.SELECTED )
		else :
			self.onStateChanged_( UIState.COMMON )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getLocked( self ) :
		return self.__locked

	def _setLocked( self, locked ) :
		if locked :
			self.setState( UIState.LOCKED )
		elif self.selected :
			self.setState( UIState.SELECTED )
		else :
			self.setState( UIState.COMMON )
		self.__locked = locked

	# ---------------------------------------
	def _getItemInfo( self ) :
		return self.__itemInfo

	# ---------------------------------------
	def _getMouseHighlight( self ) :
		return self.__mouseHighlight

	def _setMouseHighlight( self, highlight ) :
		self.__mouseHighlight = highlight

	# -------------------------------------------------
	def _setTexture( self, texture ) :
		Control._setTexture( self, texture )
		if texture.strip() != "" and self.texture == "" :
			self.getGui().textureName = "icons/tb_yw_sj_005.dds"
			self.mapping = ( ( 0, 0 ), ( 0, 1 ), ( 1, 1 ), ( 1, 0 ) )

	# -------------------------------------------------
	def _getIndex( self ) :
		return self.__index

	def _setIndex( self, index ) :
		self.__index = index

	# -------------------------------------------------
	def _getGBIndex( self ) :
		return self.__index

	# -------------------------------------------------
	def _getIcon( self ) :
		return ( self.texture, self.mapping )

	def _setIcon( self, icon ) :
		if isDebuged :
			assert isinstance( icon, ( tuple, str ) )
		isTuple = type( icon ) is tuple
		self.texture = ( isTuple and [icon[0]] or [icon] )[0]
		if not isTuple or icon[1] is None :
			self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )
		else :
			self.mapping = icon[1]

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, value ) :
		self.__selectable = value

	# -------------------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, selected ) :
		if not self.__selectable : return
		if selected == self.__selected : return
		if selected : self.__select()
		else : self.__deselect()

	# -------------------------------------------------
	def _getDescription( self ) :
		return self.__description

	def _setDescription( self, dsp ) :
		self.__description = dsp


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	isLocked = property( _getLock )										# �����ڻ�ȡ��Ʒ�Ƿ񱻸ı���ɫ����Ϣ
	locked = property( _getLocked, _setLocked )							# ���� Item ������״̬
	itemInfo = property( _getItemInfo )									# ��ȡ��Ӧ�ĵײ� Item ��Ϣ
	mouseHighlight = property( _getMouseHighlight, _setMouseHighlight )	# ��ȡ/���������� Item ʱ���Ƿ������ʾ
	texture = property( Control._getTexture, _setTexture )				# ��ȡ Item ����ͼ
	index = property( _getIndex, _setIndex )							# ��ȡ/���� Item �ڸ��б��е�����ֵ
	gbIndex = property( _getGBIndex )									# ��ȡ Item �����и��б��е�����ֵ
	icon = property( _getIcon, _setIcon )								# ��ȡ/���� Item ��ͼ�꣺( texture, mapping )
	selectable = property( _getSelectable, _setSelectable )				# ���� Item �Ƿ���Ա�ѡ��
	selected = property( _getSelected, _setSelected )					# ���� Item �Ƿ���ѡ��״̬
	description = property( _getDescription, _setDescription )			# ��ȡ/���� Item ��������Ϣ

# -*- coding: gb18030 -*-
#
# $Id: GUIBaseObject.py,v 1.45 2008-08-27 09:03:34 huangyongwei Exp $

"""
implement base python class of gui��
2005/03/20 : writen by huangyongwei
"""
"""
composing :
	XXGUIComponent
"""

import os
import weakref
import Math
import guis.Debug as Debug
import BigWorld
from guis import *


class GUIBaseObject( object ) :
	def __init__( self, guiObject = None ) :
		object.__init__( self )
		self.__guiObject = None					# ��Ӧ������ UI
		self.__initialize( guiObject )			# ��ʼ��
		self.__disposed = False					# �Ƿ��Ѿ�����

		self.__hDockStyle = "LEFT"				# ��ˮƽ�����ϣ�����丸�׵�ͣ����ʽ��"HFILL", "LEFT", "CENTER", "RIGHT", "S_LEFT", "S_CENTER", "S_RIGHT"
		self.__vDockStyle = "TOP"				# �ڴ�ֱ�����ϣ�����丸�׵�ͣ����ʽ��"VFILL", "TOP", "MIDDLE", "BOTTOM", "S_TOP", "S_MIDDLE", "S_BOTTOM"
		self.__hDockChildren = WeakList()		# ����ˮƽ�����ϣ�����������Ҷ�ͣ���������� UI������ʹ����������������ʹ���� UI �����ͷţ�
		self.__vDockChildren = WeakList()		# ����ˮƽ�����ϣ�����������Ҷ�ͣ���������� UI������ʹ����������������ʹ���� UI �����ͷţ�

	def subclass( self, guiObject ) :
		self.__initialize( guiObject )
		return self

	def dispose( self ) :
		"""
		�ֹ� dispose ��������ʵ�ú������岻����Ϊ������б�Ľű����ұ���������
		��������˸ú�����Ҳ�޷��ͷš�����ֻ����һЩ�򵥵�����������
		"""
		if self.pyParent is not None :						# ��� parent �� python ����
			self.pyParent.__delDockChild( self )			# ���ҴӸ��׵� dock style �б������
		gui = self.__guiObject
		if gui.parent is None : GUI.delRoot( gui )			# ��� parent �� None������ζ�����Ƕ��� UI��Ҫ�� root �����
		else : gui.parent.delChild( gui )					# �븸�����븸�ӹ�ϵ
		for n, ch in gui.children :							# �����еĺ���
			gui.delChild( ch )								# ���븸�ӹ�ϵ
		gui.script = None									# ȡ�������� UI ������
		self.__disposed = True								# ����Ѿ�������

	def __del__( self ) :
		if Debug.output_del_GUIBaseObject :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, guiObject ) :
		if guiObject is None : return
		if self.__guiObject is None :
			self.__guiObject = guiObject					# �������� UI������ʹ��ǿ���õ�Ŀ���ǣ���ֻ֤Ҫ python UI ���ڣ������Ӧ������ UI Ҳ���ڣ�
			UIScriptWrapper.wrap( guiObject, self )			# ʹ���� UI Ҳ�� python UI ���а�
															#������ʹ�ð�װ����Ŀ���ǣ�ʹ���� UI �� python UI ������Ϊ �����ã���Щ�����õĲ��������
															# ��װ������ɵģ������ͷ�ֹ������ UI �� python UI ֮��Ľ������ã�
		else :
			self.resetBindingUI_( guiObject )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addDockChild( self, pyChild ) :
		"""
		���һ������������ҵ�ͣ����ʽ
		"""
		if pyChild.h_dockStyle != "LEFT" :					# �ų�����ͣ������ΪĬ������ͣ��
			if pyChild not in self.__hDockChildren :
				self.__hDockChildren.append( pyChild )
		elif pyChild in self.__hDockChildren :				# ����Ǵӱ��ͣ����ʽ��Ϊ��ͣ����ʽ��
			self.__hDockChildren.remove( pyChild )			# �򣬴�ͣ���б������������Ҫ��¼��ͣ����
		if pyChild.v_dockStyle != "TOP" :					# �ų�����ͣ������ΪĬ������ͣ��
			if pyChild not in self.__vDockChildren :
				self.__vDockChildren.append( pyChild )
		elif pyChild in self.__vDockChildren :				# ����Ǵӱ��ͣ����ʽ��Ϊ��ͣ����ʽ��
			self.__vDockChildren.remove( pyChild )			# �򣬴�ͣ���б������������Ҫ��¼��ͣ����

	def __delDockChild( self, pyChild ) :
		"""
		ɾ��һ������������ҵ�ͣ����ʽ
		"""
		if pyChild in self.__hDockChildren :
			self.__hDockChildren.remove( pyChild )
		if pyChild in self.__vDockChildren :
			self.__vDockChildren.remove( pyChild )


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onParentWidthChanged_( self, oldWidth, newWidth ) :
		"""
		�����׵Ŀ�ȸı�ʱ������
		"""
		if self.h_dockStyle == "CENTER" :						# �����ˮƽ�м�ͣ��
			self.left += ( newWidth - oldWidth ) / 2.0			# �����м��븸���е�ľ���ֵ�Ǻ�ֵ
		elif self.h_dockStyle == "RIGHT" :						# �������ͣ��
			self.left += ( newWidth - oldWidth )				# �����ұ��븸���ұߵľ���ֵ�Ǻ��ֵ
		elif  self.h_dockStyle == "HFILL" :						# �����ˮƽ��չ��ʽ
			self.width += ( newWidth - oldWidth )				# �򣬸��׵Ŀ��������٣��ҵĿ��Ҳ�����������
		elif self.h_dockStyle == "S_LEFT" :						# �����������ͣ����ʽ
			self.left *= ( newWidth / oldWidth )				# ���ҵ�����游�׵Ŀ�ȱ仯���������仯������ֵ�ǣ����׿�ȱ仯ǰ��ı�ֵ��
		elif self.h_dockStyle == "S_CENTER" :					# ������м�����ͣ����ʽ
			oldCenter = oldWidth / 2 - self.center				# �����м���븸���м��ľ����游�׿�ȵı仯���������仯������ֵ�ǣ����׿�ȱ仯ǰ��ı�ֵ��
			newCenter = oldCenter * ( newWidth / oldWidth )
			self.center = newWidth / 2 - newCenter
		elif self.h_dockStyle == "S_RIGHT" :					# ������ұ�����ͣ��
			oldRight = oldWidth - self.right					# �����ұ��븸���ұߵľ����游�׿�ȵı仯���������仯������ֵ�ǣ����׿�ȱ仯ǰ��ı�ֵ��
			newRight = oldRight * ( newWidth / oldWidth )
			self.right = newWidth - newRight

	def onParentHeightChanged_( self, oldHeight, newHeight ) :
		"""
		�����׵ĸ߶ȱ仯ʱ������
		"""
		if self.v_dockStyle == "MIDDLE" :						# ����Ǵ�ֱ�м�ͣ��
			self.top += ( newHeight - oldHeight ) / 2.0         # �����м��븸���е�ľ���ֵ�Ǻ�ֵ
		elif self.v_dockStyle == "BOTTOM" :                     # ����ǵײ�ͣ��
			self.bottom += ( newHeight - oldHeight )            # ���ҵױ��븸�׵ױߵľ���ֵ�Ǻ��ֵ
		elif self.v_dockStyle == "VFILL" :                      # ����Ǵ�ֱ��չ��ʽ
			self.height += ( newHeight - oldHeight )            # �򣬸��׵ĸ߶�������٣��ҵĸ߶�Ҳ�����������
		elif self.v_dockStyle == "S_TOP" :                      # �����������ͣ����ʽ
			self.top *= ( newHeight / oldHeight )               # ���ҵ��Ͼ��游�׵Ŀ�ȱ仯���������仯������ֵ�ǣ����׸߶ȱ仯ǰ��ı�ֵ��
		elif self.v_dockStyle == "S_MIDDLE" :                   # ������м�����ͣ����ʽ
			oldMiddle = oldHeight / 2 - self.middle             # �����м���븸���м��ľ����游�׿�ȵı仯���������仯������ֵ�ǣ����׸߶ȱ仯ǰ��ı�ֵ
			newMiddle = oldMiddle * ( newHeight / oldHeight )
			self.middle = newHeight / 2 - newMiddle
		elif self.v_dockStyle == "S_BOTTOM" :                   # ����ǵױ�����ͣ��
			oldBottom = oldHeight - self.bottom                 # ���ҵױ��븸���ұߵľ����游�׸߶ȵı仯���������仯������ֵ�ǣ����׸߶ȱ仯ǰ��ı�ֵ��
			newBottom = oldBottom * ( newHeight / oldHeight )
			self.bottom = newHeight - newBottom


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def resetBindingUI_( self, gui ) :
		"""
		�������������󶨵����� UI
		"""
		if gui == self.__guiObject : return
		oldGui = self.__guiObject								# ���ȱ���ɵ����� UI
		self.__guiObject = gui									# ���ð󶨵����� UI Ϊ�����õ� UI
		UIScriptWrapper.wrap( gui, self )						# ��װ������ UI ���ҵ����ù�ϵ
		UIScriptWrapper.wrap( oldGui, None )					# ���������� UI �����ù�ϵ����������� UI û�б�����ã���ǰ�������ý������������ͷţ�
		parent = oldGui.parent									# ԭ���ĸ����� UI
		if parent is None :										# ���ԭ��û���и� UI����˵���ɵ����� UI �Ƕ��� UI
			if oldGui in GUI.roots() :							# ����ɵ����� UI �� rool ��
				GUI.delRoot( oldGui )							# �������
				GUI.addRoot( gui )								# ���µ����� UI ��ӵ� root ��
		else :													# ���ԭ���и� UI
			for n, ch in parent.children :						# �򣬱����� UI
				if ch != oldGui : continue						# �ҵ������� UI �ڸ� UI �е�λ��
				parent.addChild( gui, n )						# ���µ� UI ����ɵ� UI
				break

		for ch in util.preFindGui( oldGui ) :					# ǰ������ҳ��� UI ���������� UI
			if ch.parent : ch.parent.delChild( ch )				# �������ǵ����еĸ��ӹ�ϵ��������ֻ�й�ϵ�������ʵ���Զ��ͷţ�

	# -------------------------------------------------
	def onWidthChanged_( self, oldWidth ) :
		"""
		���ҵĿ�ȸı�ʱ������
		"""
		pass

	def onHeightChanged_( self, oldHeight ) :
		"""
		���ҵĸ߶ȸı�ʱ������
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getGui( self ) :
		"""
		��ȡ��Ӧ������ UI
		"""
		return self.__guiObject

	def resort( self ) :
		"""
		�� UI ��λ�õ� Z ֵ������������
		"""
		self.__guiObject.reSort()

	def hitTest( self, x, y ) :
		"""
		�ж���Ļ��ĳ��ά���Ƿ�����������
		"""
		return self.__guiObject.hitTest( x, y )

	def isMouseHit( self ) :
		"""
		�ж�����Ƿ�ָ��������
		"""
		return s_util.isMouseHit( self.__guiObject )

	# -------------------------------------------------
	def setToDefault( self, tiled = False ) :
		"""
		���ҵĸ�����������Ϊ���� UI ��Ĭ������ֵ
		"""
		gui = self.__guiObject
		gui.verticalAnchor = "TOP"					# ���������еĴ�ֱͣ����ʽΪĬ��
		gui.horizontalAnchor = "LEFT"				# ���������е�ˮƽͣ����ʽΪĬ��
		gui.materialFX = "BLEND"					# ����Ĭ����ͼ����Ⱦ��ʽ
		gui.widthRelative = False					# Ĭ��ʹ����������
		gui.heightRelative = False					# Ĭ��ʹ����������
		gui.tiled = tiled							# �Ƿ����ƽ��ģʽ

	# -------------------------------------------------
	def addPyChild( self, pyChild, name = "" ) :
		"""
		���һ���� UI
		"""
		if name == "" :											# û���ֵ���ӷ�ʽ
			self.__guiObject.addChild( pyChild.getGui() )
		else :
			self.__guiObject.addChild( pyChild.getGui(), name )	# �����ֵ���ӷ�ʽ

		# ����������ܹ��죬��������һ�� bug��ֻ��ͨ�����·��������ܽ���� bug
		focus = getattr( pyChild, "focus", False )				# ��ȡ�� UI �� focus ����
		if focus :												# ����� UI ԭ���� focus Ϊ True
			child = pyChild.getGui()
			child.focus = False									# ������Ҫ���� UI �� focus ������Ϊ false��Ϊ���������ٴ�����Ϊ True ʱ��Ч��
			child.focus = True									# ��������Ϊ True����ʵ�����ڲ��ǽ��� UI��ӵ� focus �б�
																# ���֮ǰû�н����� focus ����Ϊ False������ֱ������Ϊ True
																# �����������жϣ�����ǰ���ֵ�Ƿ�һ�������һ���Ļ��������Ὣ UI ��ӵ�
																# fosus �б����������һ�� bug���������� focus���磺crossFocus �ȣ� û�и����⣩
		self.__addDockChild( pyChild )							# ��ӵ�ͣ���б�

	def delPyChild( self, pyChild ) :
		"""
		ɾ��һ���� UI
		"""
		self.__delDockChild( pyChild )
		self.__guiObject.delChild( pyChild.getGui() )

	def clearChildren( self ) :
		"""
		��������� UI
		"""
		for n, ch in self.__guiObject.children :
			self.__guiObject.delChild( ch )
		self.__hDockChildren.clear()
		self.__vDockChildren.clear()

	# -------------------------------------------------
	def getPosToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ����������λ�ã�һ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ��λ�ã�
		"""
		pos = pyUI.posToScreen()
		selfPos = self.posToScreen()
		pos = selfPos[0] - pos[0], selfPos[1] - pos[1]
		return pos

	def getRPosToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ���������λ�ã�һ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ��λ�ã�
		"""
		pos = pyUI.r_posToScreen()
		selfPos = self.r_posToScreen()
		pos = selfPos[0] - pos[0], selfPos[1] - pos[1]
		return pos

	# ---------------------------------------
	def getLeftToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ������������ࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ����ࣩ
		"""
		return self.leftToScreen - pyUI.leftToScreen

	def getRLeftToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI �����������ࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ����ࣩ
		"""
		return self.r_leftToScreen - pyUI.r_leftToScreen

	def getCenterToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI �����������оࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ���оࣩ
		"""
		return self.centerToScreen - pyUI.leftToScreen

	def getRCenterToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ����������оࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ���оࣩ
		"""
		return self.r_centerToScreen - pyUI.r_leftToScreen

	def getRightToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI �����������Ҿࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ���Ҿࣩ
		"""
		return self.rightToScreen - pyUI.leftToScreen

	def getRRightToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ����������Ҿࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� ���Ҿࣩ
		"""
		return self.r_rightToScreen - pyUI.r_leftToScreen

	# ---------------------------------------
	def getTopToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ���������궥�ࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� �Ķ��ࣩ
		"""
		return self.topToScreen - pyUI.topToScreen

	def getRTopToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ��������궥�ࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� �Ķ��ࣩ
		"""
		return self.r_topToScreen - pyUI.r_topToScreen

	def getMiddleToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ���������괹ֱ�оࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� �Ĵ�ֱ�оࣩ
		"""
		return self.middleToScreen - pyUI.topToScreen

	def getRMiddleToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ��������괹ֱ�оࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� �Ĵ�ֱ�оࣩ
		"""
		return self.r_middleToScreen - pyUI.r_topToScreen

	def getBottomToUI( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ����������׾ࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� �ĵ׾ࣩ
		"""
		return self.bottomToScreen - pyUI.topToScreen

	def getRBottomToParent( self, pyUI ) :
		"""
		��ȡ�������ĳ�� UI ���������׾ࣨһ�������������Ҫ��� ����� ���� �� ���׵ĸ��� �ĵ׾ࣩ
		"""
		return self.r_bottomToScreen - pyUI.r_topToScreen


	# ----------------------------------------------------------------
	# common properties
	# ----------------------------------------------------------------
	def _getDisposed( self ) :
		return self.__disposed

	# -------------------------------------------------
	def _getName( self ) :
		return self.__guiObject.name

	def _setName( self, name ) :
		self.__guiObject.name = name

	# -------------------------------------------------
	def _getParent( self ) :
		parent = self.__guiObject.parent
		if parent is None :
			return None
		return UIScriptWrapper.unwrap( parent )

	def _getNearParent( self ) :
		parent = self.__guiObject.parent
		while parent :
			pyParent = UIScriptWrapper.unwrap( parent )
			if pyParent : return pyParent
			parent = parent.parent
		return None

	def _getTopParent( self ) :
		parent = self.__guiObject.topParent
		return UIScriptWrapper.unwrap( parent )

	# -------------------------------------------------
	def _getVisible( self ) :
		return self.getGui().visible

	def _setVisible( self, value ) :
		self.__guiObject.visible = value

	def _getRVisible( self ) :
		return self.getGui().rvisible

	# -------------------------------------------------
	def _getColor( self ) :
		return self.__guiObject.colour.tuple()

	def _setColor( self, color ) :
		if len( color ) == 3 :
			a = self.__guiObject.colour.alpha
			color = tuple( color ) + ( a, )
		self.__guiObject.colour = color

	# ---------------------------------------
	def _getAlpha( self ) :
		return self.__guiObject.colour.alpha

	def _setAlpha( self, value ) :
		self.__guiObject.colour.alpha = value

	# -------------------------------------------------
	def _getTexture( self ) :
		return self.__guiObject.textureName

	def _setTexture( self, texture ) :
		if isinstance( texture, BigWorld.PyTextureProvider ):
			self.__guiObject.texture = texture
		else:
			self.__guiObject.textureName = texture

	# ---------------------------------------
	def _getTextureFolder( self ) :
		return "/".join( self.texture.split( "/" )[:-1] )

	# -------------------------------------------------
	def _getMapping( self ) :
		return self.__guiObject.mapping

	def _setMapping( self, mapping ) :
		self.__guiObject.mapping = mapping

	# ---------------------------------------
	def _getMaterialFX( self ) :
		return self.__guiObject.materialFX

	def _setMaterialFX( self, style ) :
		self.__guiObject.materialFX = style

	# ----------------------------------------------------------------
	# pos properties
	# ----------------------------------------------------------------
	def _getHorizontalDockStyle( self ) :
		return self.__hDockStyle

	def _setHorizontalDockStyle( self, dockStyle ) :
		if isDebuged :
			assert dockStyle in ["HFILL", "LEFT", "CENTER", "RIGHT", "S_LEFT", "S_CENTER", "S_RIGHT"]
		self.__hDockStyle = dockStyle
		pyParent = self.pyParent
		if pyParent is not None :
			pyParent.__addDockChild( self )

	# ---------------------------------------
	def _getVerticalDockStyle( self ) :
		return self.__vDockStyle

	def _setVerticalDockStyle( self, dockStyle ) :
		if isDebuged :
			assert dockStyle in ["VFILL", "TOP", "MIDDLE", "BOTTOM", "S_TOP", "S_MIDDLE", "S_BOTTOM"]
		self.__vDockStyle = dockStyle
		pyParent = self.pyParent
		if pyParent is not None :
			pyParent.__addDockChild( self )

	# -------------------------------------------------
	def _getHAnchor( self ) :
		return self.__guiObject.horizontalAnchor

	def _setHAnchor( self, anchor ) :
		self.__guiObject.horizontalAnchor = anchor

	# ---------------------------------------
	def _getVAnchor( self ) :
		return self.__guiObject.verticalAnchor

	def _setVAnchor( self, anchor ) :
		self.__guiObject.verticalAnchor = anchor

	# -------------------------------------------------
	def _getLeft( self ) :
		return s_util.getGuiLeft( self.__guiObject )

	def _setLeft( self, left ) :
		s_util.setGuiLeft( self.__guiObject, left )

	# -------------------------------------------------
	def _getTop( self ) :
		return s_util.getGuiTop( self.__guiObject )

	def _setTop( self, top ) :
		s_util.setGuiTop( self.__guiObject, top )

	# -------------------------------------------------
	def _getRight( self ) :
		return s_util.getGuiRight( self.__guiObject )

	def _setRight( self, right ) :
		s_util.setGuiRight( self.__guiObject, right )

	# -------------------------------------------------
	def _getBottom( self ) :
		return s_util.getGuiBottom( self.__guiObject )

	def _setBottom( self, bottom ) :
		s_util.setGuiBottom( self.__guiObject, bottom )

	# -------------------------------------------------
	def _getCenter( self ) :
		return s_util.getGuiCenter( self.__guiObject )

	def _setCenter( self, center ) :
		s_util.setGuiCenter( self.__guiObject, center )

	# -------------------------------------------------
	def _getMiddle( self ) :
		return s_util.getGuiMiddle( self.__guiObject )

	def _setMiddle( self, middle ) :
		s_util.setGuiMiddle( self.__guiObject, middle )

	# -------------------------------------------------
	def _getPos( self ) :
		return s_util.getGuiPos( self.__guiObject )

	def _setPos( self, ( left, top ) ) :
		s_util.setGuiPos( self.__guiObject, ( left, top ) )

	# ----------------------------------------------------------------
	def _getRLeft( self ) :
		return s_util.getGuiRLeft( self.__guiObject )

	def _setRLeft( self, left ) :
		s_util.setGuiRLeft( self.__guiObject, left )

	# -------------------------------------------------
	def _getRTop( self ) :
		return s_util.getGuiRTop( self.__guiObject )

	def _setRTop( self, top ) :
		s_util.setGuiRTop( self.__guiObject, top )

	# -------------------------------------------------
	def _getRRight( self ) :
		return s_util.getGuiRRight( self.__guiObject )

	def _setRRight( self, right ) :
		s_util.setGuiRRight( self.__guiObject, right )

	# -------------------------------------------------
	def _getRBottom( self ) :
		return s_util.getGuiRBottom( self.__guiObject )

	def _setRBottom( self, bottom ) :
		s_util.setGuiRBottom( self.__guiObject, bottom )

	# -------------------------------------------------
	def _getRCenter( self ) :
		return s_util.getGuiRCenter( self.__guiObject )

	def _setRCenter( self, center ) :
		s_util.setGuiRCenter( self.__guiObject, center )

	# -------------------------------------------------
	def _getRMiddle( self ) :
		return s_util.getGuiRMiddle( self.__guiObject )

	def _setRMiddle( self, middle ) :
		s_util.setGuiRMiddle( self.__guiObject, middle )

	# -------------------------------------------------
	def _getRPos( self ) :
		return s_util.getGuiRPos( self.__guiObject )

	def _setRPos( self, ( left, top ) ) :
		s_util.setGuiRPos( self.__guiObject, ( left, top ) )

	# -------------------------------------------------
	def _getPosZ( self ) :
		return self.__guiObject.position.z

	def _setPosZ( self, z ) :
		self.__guiObject.position.z = z


	# ----------------------------------------------------------------
	# size properties
	# ----------------------------------------------------------------
	def _getWidth( self ) :
		return s_util.getGuiWidth( self.__guiObject )

	def _setWidth( self, width ) :
		oldWidth = s_util.getGuiWidth( self.__guiObject )
		s_util.setGuiWidth( self.__guiObject, width )
		for pyChild in self.__hDockChildren :
			pyChild.onParentWidthChanged_( oldWidth, width )
		if self.h_dockStyle == "CENTER" :
			self.left -= ( width - oldWidth ) / 2
		elif self.h_dockStyle == "RIGHT" :
			self.left -= width - oldWidth
		self.onWidthChanged_( oldWidth )

	# -------------------------------------------------
	def _getHeight( self ) :
		return s_util.getGuiHeight( self.__guiObject )

	def _setHeight( self, height ) :
		oldHeight = s_util.getGuiHeight( self.__guiObject )
		s_util.setGuiHeight( self.__guiObject, height )
		for pyChild in self.__vDockChildren :
			pyChild.onParentHeightChanged_( oldHeight, height )
		if self.v_dockStyle == "MIDDLE" :
			self.top -= ( height - oldHeight ) / 2
		elif self.v_dockStyle == "BOTTOM" :
			self.top -= height - oldHeight
		self.onHeightChanged_( oldHeight )

	# -------------------------------------------------
	def _getSize( self ) :
		width = self._getWidth()
		height = self._getHeight()
		return Math.Vector2( width, height )

	def _setSize( self, ( width, height ) ) :
		self._setWidth( width )
		self._setHeight( height )

	# ----------------------------------------------------------------
	def _getRWidth( self ) :
		return s_util.getGuiRWidth( self.__guiObject )

	def _setRWidth( self, width ) :
		pWidth = s_util.toPXMeasure( width )
		self._setWidth( width )

	# -------------------------------------------------
	def _getRHeight( self ) :
		return s_util.getGuiRHeight( self.__guiObject )

	def _setRHeight( self, height ) :
		pHeight = s_util.toPYMeasure( height )
		self._setHeight( height )

	# -------------------------------------------------
	def _getRSize( self ) :
		width = self._getRWidth()
		height = self._getRHeight()
		return ( width, height )

	def _setRSize( self, ( width, height ) ) :
		self._setRWidth( width )
		self._setRHeight( height )

	# -------------------------------------------------
	def _getTiled( self ) :
		return self.__guiObject.tiled

	def _setTiled( self, tiled ) :
		self.__guiObject.tiled = tiled

	def _getTileWidth( self ) :
		return self.__guiObject.tileWidth

	def _setTileWidth( self, width ) :
		self.__guiObject.tileWidth = width

	def _getTileHeight( self ) :
		return self.__guiObject.tileHeight

	def _setTileHeight( self, height ) :
		self.__guiObject.tileHeight = height


	# ----------------------------------------------------------------
	# pos to screen
	# ----------------------------------------------------------------
	def _getLeftToScreen( self ) :
		return s_util.getGuiLeftToScreen( self.__guiObject )

	def _getTopToScreen( self ) :
		return s_util.getGuiTopToScreen( self.__guiObject )

	def _getCenterToScreen( self ) :
		return s_util.getGuiCenterToScreen( self.__guiObject )

	def _getMiddleToScreen( self ) :
		return s_util.getGuiMiddleToScreen( self.__guiObject )

	def _getRightToScreen( self ) :
		return s_util.getGuiRightToScreen( self.__guiObject )

	def _getBottomToScreen( self ) :
		return s_util.getGuiBottomToScreen( self.__guiObject )

	def _getPosToScreen( self ) :
		return s_util.getGuiPosToScreen( self.__guiObject )

	# ----------------------------------------------------------------
	def _getRLeftToScreen( self ) :
		return s_util.getGuiRLeftToScreen( self.__guiObject )

	def _getRTopToScreen( self ) :
		return s_util.getGuiRTopToScreen( self.__guiObject )

	def _getRCenterToScreen( self ) :
		return s_util.getGuiRCenterToScreen( self.__guiObject )

	def _getRMiddleToScreen( self ) :
		return s_util.getGuiRMiddleToScreen( self.__guiObject )

	def _getRRightToScreen( self ) :
		return s_util.getGuiRRightToScreen( self.__guiObject )

	def _getRBottomToScreen( self ) :
		return s_util.getGuiRBottomToScreen( self.__guiObject )

	def _getRPosToScreen( self ) :
		return s_util.getGuiRPosToScreen( self.__guiObject )


	# ----------------------------------------------------------------
	# mouse pos relative from me
	# ----------------------------------------------------------------
	def _getMousePos( self ) :
		return s_util.getMouseInGuiPos( self.__guiObject )

	def _getRMousePos( self ) :
		return s_util.getMouseInGuiRPos( self.__guiObject )


	# ----------------------------------------------------------------
	# properies
	# ----------------------------------------------------------------
	disposed = property( _getDisposed )										# ָ���Ƿ��Ѿ�������

	# -------------------------------------------------
	# writable properties
	# -------------------------------------------------
	gui = property( lambda self : self.__guiObject )						# ��ȡ���� UI
	txelems = property( lambda self : \
		getattr( self.__guiObject, "elements", {} ) )						# dict: ��ȡ�������ע��ֻ�� GUI.TextureFrame ���У�
	visible = property( _getVisible, _setVisible )							# bool: ��ȡ/���ÿɼ���
	rvisible = property( _getRVisible )										# bool: ��ȡ�ɼ��ԣ�ֻҪ�и� UI ���ɼ�����Ϊ False��
	name = property( _getName, _setName )									# str: ��ȡ/��������
	color = property( _getColor, _setColor )								# tuple / Vector4: ��ȡ/������ɫ
	alpha = property( _getAlpha, _setAlpha )								# int: ��ȡ/������ɫ�� alpha ֵ
	texture = property( _getTexture, _setTexture )							# str: ��ȡ/������ͼ
	mapping = property( _getMapping, _setMapping )							# tuple: ��ȡ/���� mapping ֵ
	materialFX = property( _getMaterialFX, _setMaterialFX ) 				# str: ��ͼ��Ⱦ��ʽ��
																			# ADD, BLEND��Ĭ�ϣ�, BLEND_COLOUR, BLEND_INVERSE_COLOUR, SOLID,
																			# MODULATE2X, ALPHA_TEST, BLEND_INVERSE_ALPHA, BLEND2X, or ADD_SIGNED
																			# COLOUR_EFF���Ҷȣ�
	acceptEvent = property( lambda self : False )							# ָ�� python �Ƿ����ϵͳ��Ϣ

	# ---------------------------------------
	h_dockStyle = property( _getHorizontalDockStyle, _setHorizontalDockStyle )	# str: ��ȡ/������Ը� UI ��ˮƽͣ����ʽ��"LEFT", "CENTER", "RIGHT", "HFILL"
	v_dockStyle = property( _getVerticalDockStyle, _setVerticalDockStyle )		# str: ��ȡ/������Ը� UI �Ĵ�ֱͣ����ʽ��"TOP", "MIDDLE", "BOTTOM", "VFILL"

	h_anchor = property( _getHAnchor, _setHAnchor )							# MACRO: ��ȡ/����ˮƽ�����������ͣ����ʽ��UIAnchor.LEFT/UIAnchor.CENTER/UIAnchor.RIGHT
	v_anchor = property( _getVAnchor, _setVAnchor )							# MACRO: ��ȡ/���ô�ֱ�����������ͣ����ʽ��UIAnchor.TOP/UIAnchor.MIDDLE/UIAnchor.BOTTOM

	left = property( _getLeft, _setLeft )									# float: ��ȡ/�������( �������� )
	top = property( _getTop, _setTop )										# float: ��ȡ/���ö���( �������� )
	center = property( _getCenter, _setCenter )								# float: ��ȡ/����ˮƽ�о�( �������� )
	middle = property( _getMiddle, _setMiddle )								# float: ��ȡ/���ô�ֱ�о�( �������� )
	right = property( _getRight, _setRight )								# float: ��ȡ/�����Ҿ�( �������� )
	bottom = property( _getBottom, _setBottom )								# float: ��ȡ/�������( �������� )
	pos = property( _getPos, _setPos )										# float: ��ȡ/�������( �������� )

	r_left = property( _getRLeft, _setRLeft )								# float: ��ȡ/�������( ������� )
	r_top = property( _getRTop, _setRTop )									# float: ��ȡ/���ö���( ������� )
	r_center = property( _getRCenter, _setRCenter )							# float: ��ȡ/����ˮƽ�о�( ������� )
	r_middle = property( _getRMiddle, _setRMiddle )							# float: ��ȡ/���ô�ֱ�о�( ������� )
	r_right = property( _getRRight, _setRRight )							# float: ��ȡ/�����Ҿ�( ������� )
	r_bottom = property( _getRBottom, _setRBottom )							# float: ��ȡ/�������( ������� )
	r_pos = property( _getRPos, _setRPos )									# float: ��ȡ/�������( ������� )

	posZ = property( _getPosZ, _setPosZ )									# float: ��ȡ/���� Z ֵ( ����Ϊ�����ϵ )

	# ---------------------------------------
	width = property( _getWidth, _setWidth )								# float: ��ȡ/���ÿ�ȶȣ��������꣩
	height = property( _getHeight, _setHeight )								# float: ��ȡ/���ø߶ȣ��������꣩
	size = property( _getSize, _setSize )									# tuple: ��ȡ/���ô�С���������꣩

	r_width = property( _getRWidth, _setRWidth )							# float: ��ȡ/���ÿ�ȣ�������꣩
	r_height = property( _getRHeight, _setRHeight )							# float: ��ȡ/���ø߶ȣ�������꣩
	r_size = property( _getRSize, _setRSize )								# tuple: ��ȡ/���ô�С��������꣩

	tiled = property( _getTiled, _setTiled )								# bool: ��ȡ/�����Ƿ����ƽ�����У���������ͼ��
	tileWidth = property( _getTileWidth, _setTileWidth )					# float: ��ȡ/����ƽ�̴�С( tiled Ϊ True ����Ч)������ʲô������� widthRelative ����
	tileHeight = property( _getTileWidth, _setTileWidth )					# float: ��ȡ/����ƽ�̴�С( tiled Ϊ True ����Ч)������ʲô������� heightRelative ����


	# -------------------------------------------------
	# readonly properties
	# -------------------------------------------------
	pyParent = property( _getParent )										# python ui: ��ȡ�� pyton ui��û���򷵻� None��
	pyNearParent = property( _getNearParent )								# python ui: ��ȡ�����һ���� python UI
	pyTopParent = property( _getTopParent )									# python ui: ��ȡ���� pytyon ui��û���򷵻� None��
	textureFolder = property( _getTextureFolder )							# str: ��ȡ��ͼ���ڵ�·�����������ļ�����

	# ---------------------------------------
	leftToScreen = property( _getLeftToScreen )								# flaot: ��ȡ�������Ļ����ࣨ�������꣩
	topToScreen = property( _getTopToScreen )								# flaot: ��ȡ�������Ļ�Ķ��ࣨ�������꣩
	centerToScreen = property( _getCenterToScreen )							# flaot: ��ȡ�������Ļ��ˮƽ�оࣨ�������꣩
	middleToScreen = property( _getMiddleToScreen )							# flaot: ��ȡ�������Ļ�Ĵ�ֱ�Ҿࣨ�������꣩
	rightToScreen = property( _getRightToScreen )							# flaot: ��ȡ�������Ļ���Ҿࣨ�������꣩
	bottomToScreen = property( _getBottomToScreen )							# flaot: ��ȡ�������Ļ�ĵ׾ࣨ�������꣩
	posToScreen = property( _getPosToScreen )								# tuple: ��ȡ�������Ļ��λ�ã��������꣩

	r_leftToScreen = property( _getRLeftToScreen )							# flaot: ��ȡ�������Ļ����ࣨ������꣩
	r_topToScreen = property( _getRTopToScreen )							# flaot: ��ȡ�������Ļ�Ķ��ࣨ������꣩
	r_centerToScreen = property( _getRCenterToScreen )						# flaot: ��ȡ�������Ļ��ˮƽ�оࣨ������꣩
	r_middleToScreen = property( _getRMiddleToScreen )						# flaot: ��ȡ�������Ļ�Ĵ�ֱ�Ҿࣨ������꣩
	r_rightToScreen = property( _getRRightToScreen )						# flaot: ��ȡ�������Ļ���Ҿࣨ������꣩
	r_bottomToScreen = property( _getRBottomToScreen )						# flaot: ��ȡ�������Ļ�ĵ׾ࣨ������꣩
	r_posToScreen = property( _getRPosToScreen )							# tuple : ��ȡ�������Ļ��λ�ã�������꣩

	# ---------------------------------------
	mousePos = property( _getMousePos )										# tupel: ��ȡ����������ϵ����꣨�������꣩
	r_mousePos = property( _getRMousePos )									# tupel: ��ȡ����������ϵ����꣨������꣩

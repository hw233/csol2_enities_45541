# -*- coding: gb18030 -*-
#
# $Id: UIFixer.py,v 1.8 2008-08-02 09:15:05 huangyongwei Exp $


"""
implement resolution adapter
	when resolution changed, it wll be used to fix all uis

2007/03/18: writen by huangyongwei, then it named "ResolutionAdapter"
2008/01/04: rewriten by huangyongwei, rename it "UIFixer"
"""

import sys
import BigWorld
import Math
import GUI
import util
import scale_util as s_util
import UIScriptWrapper
from bwdebug import *
from AbstractTemplates import Singleton
from Weaker import WeakSet
from Function import Functor

class UIFixer( Singleton ) :
	__cc_def_resolution = 1024.0, 768.0							# ƴ�ӽ���ʱ��ʹ�õ�Ĭ�Ϸֱ���

	def __init__( self ) :
		self.__rates = ( 1, 1 )
		self.__pyUIs = WeakSet()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __fixChildrenPosition( rates, ui ) :
		"""
		���ֱ��ʸı�ʱ������ ui ���������� UI ��λ��
		@type			rates : tuple
		@param			rates : �¾ɷֱ��ʱ�:( ��ˮƽ�ֱ��� / ��ˮƽ�ֱ��ʣ��ʹ�ֱ�ֱ��� / �´�ֱ�ֱ��� )
		@type			ui	  : engine ui
		@param			ui	  : ��������ÿһ�� ui
		@return				  : None
		"""
		def verifier( ch ) :
			if ch == ui : return False, 1
			return True, 1

		children = util.preFindGui( ui, verifier )
		for child in children :
			x, y, z = child.position
			newX = x * rates[0]
			newY = y * rates[1]
			child.position = newX, newY, z

	@staticmethod
	def __adaptDock( preReso, ui ) :
		"""
		���� dock style �������� ui ��ͣ��λ��
		@type				preReso : tuple
		@param				preReso : �ɷֱ���
		@type				ui		: engine ui
		@param				ui		: ÿ�� ui
		@return						: None
		"""
		if ui.parent is not None : return
		pyUI = UIScriptWrapper.unwrap( ui )
		if pyUI is None : return
		oldWidth = preReso[0]
		newWidth = BigWorld.screenWidth()
		oldHeight = preReso[1]
		newHeight = BigWorld.screenHeight()
		deltaW = newWidth - oldWidth
		deltaH = newHeight - oldHeight
		wscale = oldWidth / newWidth
		hscale = oldHeight / newHeight
		if pyUI.h_dockStyle == "LEFT" :
			pyUI.left *= wscale
		elif pyUI.h_dockStyle == "CENTER" :
			pyUI.left = pyUI.left * wscale + deltaW / 2
		elif pyUI.h_dockStyle == "RIGHT" :
			pyUI.left = pyUI.left * wscale + deltaW
		elif pyUI.h_dockStyle == "HFILL" :
			pyUI.left *= wscale
			pyUI.width += deltaW
		elif pyUI.h_dockStyle == "S_LEFT" :
			pass
		elif pyUI.h_dockStyle == "S_CENTER" :
			fixcleft = pyUI.top * wscale + deltaW / 2
			fixcenter = fixcleft + pyUI.width / 2
			pyUI.center = ( newWidth / 2 ) - ( ( newWidth / 2 - fixcenter ) / wscale )
		elif pyUI.h_dockStyle == "S_RIGHT" :
			fixrleft = pyUI.left * wscale + deltaW
			fixright = fixrleft + pyUI.width
			pyUI.right = newWidth - ( ( newWidth - fixright ) / wscale )

		if pyUI.v_dockStyle == "TOP" :
			pyUI.top *= hscale
		elif pyUI.v_dockStyle == "MIDDLE" :
			pyUI.top = pyUI.top * hscale + deltaH / 2
		elif pyUI.v_dockStyle == "BOTTOM" :
			pyUI.top = pyUI.top * hscale + deltaH
		elif pyUI.v_dockStyle == "VFILL" :
			pyUI.top *= hscale
			pyUI.height += deltaH
		elif pyUI.v_dockStyle == "S_TOP" :
			pass
		elif pyUI.v_dockStyle == "S_MIDDLE" :
			fixmtop = pyUI.top * hscale + deltaH / 2
			fixmiddle = fixmtop + pyUI.height / 2
			pyUI.middle = ( newHeight / 2 ) - ( ( newHeight / 2 - fixmiddle ) / hscale )
		elif pyUI.v_dockStyle == "S_BOTTOM" :
			fixbtop = pyUI.top * hscale + deltaH
			fixbottom = fixbtop + pyUI.height
			pyUI.bottom = newHeight - ( ( newHeight - fixbottom ) / hscale )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onResolutionChanged( self, preReso ) :
		"""
		���ֱ��ʸı�ʱ������
		"""
		hfUILoader.onResolutionChanged( preReso )

		for pyUI in self.__pyUIs :
			try :
				self.fix( preReso, pyUI.getGui() )
			except ReferenceError :
				self.__pyUIs.remove( pyUI )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def attach( self, pyUI ) :
		"""
		���� ui �������б���
		@type				pyUI : python ui
		@param				pyUI : python ui
		@return					 : None
		"""
		if pyUI not in self.__pyUIs :
			self.__pyUIs.add( pyUI )

	def detach( self, pyUI ) :
		"""
		�������б���ж�� ui
		@type				pyUI : python ui
		@param				pyUI : python ui
		@return					 : None
		"""
		if pyUI in self.__pyUIs :
			self.__pyUIs.remove( pyUI )

	# -------------------------------------------------
	def fix( self, preReso, ui ) :
		"""
		���ֱ��ʸı�ʱ�������������� ui ��λ��
		@type			preReso : tuple / Vector2
		@type			preReso : ����ǰ�ķֱ���
		@type			ui		: engine ui
		@param			ui		: ���� ui
		@return					: None
		"""
		rateX = preReso[0] / BigWorld.screenWidth()
		rateY = preReso[1] / BigWorld.screenHeight()
		rates = ( rateX, rateY )
		self.__fixChildrenPosition( rates, ui )
		self.__adaptDock( preReso, ui )

	def firstLoadFix( self, ui ) :
		"""
		������ GUI.load ���� ui ʱ�������������� ui ��λ��
		@type				ui : engine ui
		@param				ui : ���� ui
		@return				   : None
		"""
		defReso = self.__cc_def_resolution
		if defReso == BigWorld.screenSize() : return
		rateX = defReso[0] / BigWorld.screenWidth()
		rateY = defReso[1] / BigWorld.screenHeight()
		rates = ( rateX, rateY )
		self.__fixChildrenPosition( rates, ui )

	# -------------------------------------------------
	def firstDockRoot( self, pyRoot ) :
		"""
		������Ϊ RootGUI ʱ��������������ͣ����ʽ��DockStyle������ ui ����丸�׵�ͣ��λ��
		@type				pyRoot : python ui
		@param				pyRoot : python ui( common.RootGUI )
		@return					   : None
		"""
		self.__adaptDock( self.__cc_def_resolution, pyRoot.getGui() )

	# -------------------------------------------------
	def toFixedX( self, defX ) :
		"""
		��Ĭ�ϵ� X ���������ת��Ϊ�ʺϵ�ǰ�ֱ����µ� X ���������
		@type				defX : float
		@param				defX : Ĭ�Ϸֱ����µ� X ���������
		@rtype					 : float
		@return					 : ��ǰ�ֱ����µ� X ���������
		"""
		return defX * self.__cc_def_resolution[0] / BigWorld.screenWidth()

	def toFixedY( self, defY ) :
		"""
		��Ĭ�ϵ� Y ���������ת��Ϊ�ʺϵ�ǰ�ֱ����µ� Y ���������
		@type				defY : float
		@param				defY : Ĭ�Ϸֱ����µ� Y ���������
		@rtype					 : float
		@return					 : ��ǰ�ֱ����µ� Y ���������
		"""
		return defY * self.__cc_def_resolution[1] / BigWorld.screenHeight()

	def toFixedPos( self, defPos ) :
		"""
		��Ĭ�ϵ��������ת��Ϊ�ʺϵ�ǰ�ֱ����µ��������
		@type				defPos : Vector3
		@param				defPos : Ĭ�Ϸֱ����µ��������
		@rtype					   : Vector3/Vector2
		@return					   : ��ǰ�ֱ����µ��������
		"""
		scx, scy = BigWorld.screenSize()
		x = defPos[0] * self.__cc_def_resolution[0] / scx
		y = defPos[1] * self.__cc_def_resolution[1] / scy
		if len( defPos ) == 2 :
			return Math.Vector2( x, y )
		return Math.Vector3( x, y, defPos[2] )


# --------------------------------------------------------------------
# ʵ����ҪƵ�����ص� UI �ļ�����
# ͨ���ü��������м��أ������ firstLoadFix �ĵ���
# ע�⣺
#	�� ǧ������е� UI �����������أ��������ʵ��䷴
#	�� ֻ��������Ϸ�����ж���Ҫ�������ص� UI ����������
# --------------------------------------------------------------------
class HFUILoader( Singleton ) :
	"""
	ui loader for load ui high frequency
	"""
	def __init__( self ) :
		self.__uis = {}

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onResolutionChanged( self, preReso ) :
		"""
		�ֱ��ʸı�ʱ������
		"""
		for path in self.__uis.keys() :
			self.__uis[path] = uiFixer.firstLoadFix( GUI.load( path ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def load( self, path ) :
		"""
		���� UI ����
		"""
		ui = self.__uis.get( path, None )
		if ui : return util.copyGuiTree( ui )
		ui = GUI.load( path )
		uiFixer.firstLoadFix( ui )
		self.__uis[path] = ui
		return util.copyGuiTree( ui )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiFixer = UIFixer()
hfUILoader = HFUILoader()

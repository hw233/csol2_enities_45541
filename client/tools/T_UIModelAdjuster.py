# -*- coding: gb18030 -*-
#
# $Id: T_UIModelAdjuster.py,v 1.23 2008-08-28 03:55:08 huangyongwei Exp $
#
"""
implement cameras, it moved from love3.py
2008/05/29: created by huangyongwei
"""

import os
import copy
import string
import Math
import gbref
import love3
from MessageBox import *
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.AdjModelRender import AdjModelRender
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.TextBox import TextBox
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import SingleColListItem
from guis.tooluis.CSTextPanel import CSTextPanel
from tools import toolMgr
from ITool import ITool
from config.client.msgboxtexts import Datas as mbmsgs

_helpText = "@F{fc=(205,97,44)}ʹ�÷�����@B@D"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "�鿴Ŀ¼��$cfgPath���Ƿ���ڡ���������ڣ��򴴽�һ����@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "����������󣬰��ļ���$cfgFile����������@B@B"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}ģ���б�@D@B"
_helpText += "@S{4}���������һ���������г�������ģ�ͣ�ѡ��һ��ģ�� 0.5 �����ѡ���ģ�ͽ���"
_helpText += "��ģ�Ͱ�������ʾ��ѡ��ģ�ͺ󣬱����������Ĳ��������ϵ���ģ�͵�λ�ã����"
_helpText += "ĳ��ģ�͵�λ�ñ������ˣ�����û���棬��ģ��ѡ����潫�����һ�������������"
_helpText += "ĳ��ģ�͵�λ�ñ������ˣ����ұ����ˣ���ģ��ѡ����潫�����һ�����㡱��@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}ģ��λ�ò���ָ����@D@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "�����ƶ�ģ�ͣ������ť@I{p=guis/clienttools/uimodeladjuster/leftbtn.gui}@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "�����ƶ�ģ�ͣ������ť@I{p=guis/clienttools/uimodeladjuster/rightbtn.gui}@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "�����ƶ�ģ�ͣ������ť@I{p=guis/clienttools/uimodeladjuster/upbtn.gui}@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "�����ƶ�ģ�ͣ������ť@I{p=guis/clienttools/uimodeladjuster/downbtn.gui}@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "����/���ƶ�ģ�ͣ������ŵ����ڵĿ��ư����ϣ����������֡�@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "��ģ����б�������ŵ����ڵĿ��ư����ϣ�����ס ALT ����Ȼ����������֡�@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "�ָ�Ϊ��һ�α�����״̬(����ȡ���޸ı��)��˫�����ư���@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "��ģ���Զ���Ӧ��Ⱦ������ס CTRL ����Ȼ��˫�����ư���@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}���棺@D@B"
_helpText += "@S{4}�����ǰѡ�е�ģ�ͱ��ı䣬����û����Ļ����򡰱��桱��ť���ã����򡰱��桱"
_helpText += "��ť��ʾΪ��ɫ״̬��@B"
_helpText += "@S{4}�������ˡ��رա���ť��������ģ��û�б��棬��ᵯ��һ����ʾ����ʾ���Ƿ�"
_helpText += "Ҫ���滹û�����ģ��λ�����á�@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}�����İ�����@D@B"
_helpText += "@S{4}��������������Ͻǵİ�ť��@I{p=guis/clienttools/uimodeladjuster/closebtn.gui}��"
_helpText += "����Թرհ������ڡ�@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}���������ǣ�@D@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/riding.gui;m='show_tips'}@B"
_helpText += "A�����������벻��ѧ�Ұ���@BB���ţ�@BA���룿�ǸϿ�ȥ��ֵ������Ѵ�ѳ�Ʊ�䡣@B"
_helpText += "B�����磬��ûǮ����ô���ţ�@BA�������£��ҷ��ӳ��Ӷ���Ѻ�ˡ�@B"
_helpText += "B������û��û���� T_T��@BA��������Ů���Ѳ���@B"
_helpText += "B���ǵ���һ������ͦ PL �ġ�@BA��ѹ�˰ɣ��� PL Ҳ�����ϴ��������պ��ҵĴ���е�ʣ�ģ��ҿ��԰��㡣@B"
_helpText += "B��ร�Ӣ�ۣ������...@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(138,236,94)}"
_helpText += "�汾��2.0@B"
_helpText += "��Ȩ�������ʫ��@B"
_helpText += "���ߣ�����ΰ@B"
_helpText += "��ַ��@L{t=http://www.cogame.cn;m='goto_website';cfc=(0,0,255);hfc=(255,255,255)}@B"

_helpTemplate = string.Template( _helpText )


class UIModelAdjuster( Window, ITool ) :
	def __init__( self ) :
		toolMgr.addTool( self )
		wnd = GUI.load( "guis/clienttools/uimodeladjuster/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		ITool.__init__( self )
		self.__initialize( wnd )
		self.posZSegment_ = ZSegs.L2
		self.addToMgr()
		rds.ruisMgr.toolUIModelAdjuster = self

		self.__pyRender = None											# Ҫ������ģ�͹۲���
		self.__tempPath = ""											# ���õı���·��
		self.width = 260												# Ĭ�ϲ���ʾ����

	def __initialize( self, wnd ) :
		self.__pyLPModels = ListPanel( wnd.lpModels.clipPanel, wnd.lpModels.scrollBar )	# ģ���б����
		self.__pyLPModels.onItemSelectChanged.bind( self.__onModelItemSelected )
		self.__pyLPModels.itemPerScroll = False
		self.__pyLPModels.perScroll = 76.0

		self.__pyAdjustPanel = Control( wnd.adjustPanel )				# ģ�Ϳ��ư���
		self.__pyAdjustPanel.focus = True
		self.__pyAdjustPanel.mouseScrollFocus = True
		self.__pyAdjustPanel.onLDBClick.bind( self.__onAPLDBClick )
		self.__pyAdjustPanel.onMouseScroll.bind( self.__onAPMouseScroll )

		self.__pyCloseHelpBtn = Button( wnd.tpHelp.closeBtn )			# �رհ�����ť
		self.__pyCloseHelpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseHelpBtn.onLClick.bind( self.onCloseHelp_ )
		self.__pyTPHelp = CSTextPanel( wnd.tpHelp.clipPanel, wnd.tpHelp.scrollBar )	# ������ʾ����
		self.__pyTPHelp.perScroll = 60
		self.__pyTPHelp.onComponentLClick.bind( self.__onHelpLinkClick )
		self.__pyTPHelp.onComponentMouseEnter.bind( self.__onHelpShowTip )
		self.__pyTPHelp.onComponentMouseLeave.bind( self.__onHelpHideTip )

		self.__pyLBtn = Button( wnd.adjustPanel.leftBtn )				# ���ư�ť
		self.__pyLBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyLBtn.onLMouseDown.bind( self.__leftMove )
		self.__pyRBtn = Button( wnd.adjustPanel.rightBtn )				# ���ư�ť
		self.__pyRBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRBtn.onLMouseDown.bind( self.__rightMove )
		self.__pyUBtn = Button( wnd.adjustPanel.upBtn )					# ���ư�ť
		self.__pyUBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyUBtn.onLMouseDown.bind( self.__upMove )
		self.__pyDBtn = Button( wnd.adjustPanel.downBtn )				# ���ư�ť
		self.__pyDBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDBtn.onLMouseDown.bind( self.__downMove )

		self.__pyTBNuance = TextBox( wnd.tbNuance )						# ΢��ֵ����
		self.__pyTBNuance.inputMode = InputMode.FLOAT
		self.__pyTBNuance.text = "10"

		self.__pySaveBtn = Button( wnd.saveBtn )						# ���水ť
		self.__pySaveBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pySaveBtn.onLClick.bind( self.__onSaveBtnClick )

		self.__pyCloseBtn = Button( wnd.closeBtn1 )						# ȡ����ť
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCloseBtn.onLClick.bind( self.__onCloseBtnClick )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getNuance( self ) :
		text = self.__pyTBNuance.text.strip()
		if text == "" :
			text = 1.0
		return float( text ) / 100.0

	# -------------------------------------------------
	def __onModelItemSelected( self, pyItem ) :
		"""
		ѡ��ĳ��ģ��
		"""
		if pyItem is None : return
		if self.__pyRender.getConfigKey() == pyItem.modelInfo.mark :
			return
		pyItem.assignToRender()
		self.__pySaveBtn.enable = pyItem.modified

	# -------------------------------------------------
	def __leftMove( self ) :
		"""
		����ģ��
		"""
		self.__pyLPModels.pySelItem.moveX( self.__getNuance() )

	def __rightMove( self ) :
		"""
		����ģ��
		"""
		self.__pyLPModels.pySelItem.moveX( -self.__getNuance() )

	def __upMove( self ) :
		"""
		����ģ��
		"""
		self.__pyLPModels.pySelItem.moveY( self.__getNuance() )

	def __downMove( self ) :
		"""
		����ģ��
		"""
		self.__pyLPModels.pySelItem.moveY( -self.__getNuance() )

	def __onAPLDBClick( self, mods ) :
		"""
		˫��ģ�Ϳ��ư���
		"""
		if BigWorld.isKeyDown( KEY_LCONTROL ) :					# ��ס CTRL ��˫��
			self.__pyLPModels.pySelItem.autoAdjust()			# �Զ�����ģ��
		else :													# ֱ��˫��
			self.__pyLPModels.pySelItem.resume()				# �ָ�ԭ��״̬

	def __onAPMouseScroll( self, dz ) :
		"""
		��������ģ�Ϳ��ư����Ϲ���
		"""
		if BigWorld.isKeyDown( KEY_LALT ) :										# ��ס ALT ��
			if dz > 0 :
				self.__pyLPModels.pySelItem.movePitch( -self.__getNuance() )	# ��������
			else :
				self.__pyLPModels.pySelItem.movePitch( self.__getNuance() )
		else :																	# ֱ�ӹ���
			if dz > 0 :
				self.__pyLPModels.pySelItem.moveZ( -self.__getNuance() )		# ����Զ��
			else :
				self.__pyLPModels.pySelItem.moveZ( self.__getNuance() )

	def __onSaveBtnClick( self ) :
		"""
		������水ť
		"""
		self.__pyLPModels.pySelItem.save()
		datas = self.__pyRender.configDatas_
		if gbref.PyConfiger().write( datas, self.__tempPath ) :
			# "����ɹ�"
			showAutoHideMessage( 3.0, 0x0c02, "" )
		else :
			# "����ʧ�ܣ�·����%s��������"
			showAutoHideMessage( 5.0, mbmsgs[0x0c03] % self.__tempPath, "" )

	def __onCloseBtnClick( self ) :
		"""
		����رհ�ť
		"""
		self.hide()

	# -------------------------------------------------
	def __onHelpLinkClick( self, pyCom ) :
		if pyCom.linkMark == "goto_website" :
			# "@A{C}���Ǵ����ˣ���վ��û����ã�@B����@I{p=maps/emote/emote_13.gui}"
			showAutoHideMessage( 5.0, 0x0c04, "" )

	def __onHelpShowTip( self, pyCom ) :
		if pyCom.linkMark == "show_tips" :
			toolbox.infoTip.showToolTips( self, "������һ��ȥ�洴��ඣ�@A{C}@I{p=maps/emote/emote_13.gui}" )
			pyCom.getGui().materialFX = "BLEND2X"

	def __onHelpHideTip( self, pyCom ) :
		if pyCom.linkMark == "show_tips" :
			toolbox.infoTip.hide()
			pyCom.getGui().materialFX = "BLEND"


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onShowHelp_( self ) :
		"""
		��ʾ����
		"""
		self.width = 512.0

	def onCloseHelp_( self ) :
		"""
		�رհ���
		"""
		self.width = 260


	# ----------------------------------------------------------------
	# friend methods of model item
	# ----------------------------------------------------------------
	def onModifiedChanged__( self, pyItem ) :
		"""
		ѡ�е�ģ���޸�״̬�ı�ʱ������
		"""
		self.__pySaveBtn.enable = pyItem.modified


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCHName( self ) :
		return "UI ģ�ͱ༭��"

	def getHitUIs( self, pyRoot, mousePos ) :
		def doFunc( pyUI ) :
			if not pyUI.rvisible : return False, 0
			if not pyUI.hitTest( *mousePos ) : return False, 0
			if not isinstance( pyUI, AdjModelRender ) : return False, 1
			return True, 1
		pyUIs = util.postFindPyGui( pyRoot.getGui(), doFunc, True )
		return [( pyUI.__class__.__name__, pyUI ) for pyUI in pyUIs]

	def getHitUI( self, pyRoot, mousePos ) :
		pyUIs = self.getHitUIs( pyRoot, mousePos )
		if len( pyUIs ) : return pyUIs[0][1]
		return None

	def show( self, pyRender ) :
		modelInfos = pyRender.getViewInfos()
		if not len( modelInfos ) :
			# "û�пɵ�����ģ��"
			showAutoHideMessage( 5.0, 0x0c05, "" )
			return

		self.__pyRender = pyRender
		importPath = "tempconfigs/%s" % pyRender.cfgName			# ���õ���ʱ import ·��
		self.__tempPath = "common/" + importPath					# ��ʱ���õı���·��
		datas = gbref.PyConfiger().read( importPath, {}, True )		# ��ʱ�����ֵ�
		datas = self.__pyRender.configDatas_
		if datas is None :
			# "ģ�͹۲�����������__config�����ԣ����ܵ���"
			showAutoHideMessage( 5.0, 0x0c06, "" )
		else :
			datas.update( datas )
			self.__pyTPHelp.text = _helpTemplate.safe_substitute( \
				cfgPath = "res/entities/common/tempconfigs", cfgFile = pyRender.cfgName )
			modelInfos = pyRender.getViewInfos()
			for modelInfo in modelInfos :
				pyItem = ModelItem( self, pyRender, modelInfo )
				self.__pyLPModels.addItem( pyItem )
			Window.show( self )

	def hide( self ) :
		"""
		�ر�
		"""
		def close() :
			Window.hide( self )
			self.__pyLPModels.pyItems[0].setToOrigin()
			self.__pyRender = None
			self.__pyLPModels.clearItems()

		def saveAll() :
			for pyItem in self.__pyLPModels.pyItems :
				if pyItem.modified :
					pyItem.save()
			datas = self.__pyRender.configDatas_
			if gbref.PyConfiger().write( datas, self.__tempPath ) :
				# "����ɹ�!"
				showAutoHideMessage( 3.0, 0x0c02, "" )
			else :
				# "����ʧ�ܣ�·����%s��������"
				showAutoHideMessage( 5.0, mbmsgs[0x0c03] % self.__tempPath, "" )

		def respond( pyItem, res ) :
			if res == RS_YES :									# ����� �� ��ť
				saveAll()
				close()
			elif res == RS_NO :									# ����� �� ��ť
				close()
			else :												# ����� ȡ�� ��ť
				pyItem.selected = True							# ѡ��û�����ģ��

		pyMItem = None											# �ҳ��Ƿ���û�޸ĵ�ģ��
		for pyItem in self.__pyLPModels.pyItems :
			if pyItem.modified :
				pyMItem = pyItem
				break
		if pyMItem :											# �����û�޸ĵ�ģ�ͣ�����ʾ�޸�
			# "�е�ģ�͸����˻�û���棬��Ҫ������"
			showMessage( 0x0c01, "", MB_YES_NO_CANCEL, Functor( respond, pyMItem ) )
		else :
			close()


# --------------------------------------------------------------------
# implement model item
# --------------------------------------------------------------------
class ModelItem( SingleColListItem ) :
	def __init__( self, pyAdjuster, pyRender, modelInfo ) :
		item = GUI.load( "guis/clienttools/uimodeladjuster/modelitem.gui" )
		uiFixer.firstLoadFix( item )
		SingleColListItem.__init__( self, item )
		self.text = modelInfo.name
		self.__pyAdjuster = pyAdjuster
		self.__pyRender = pyRender
		self.__modelInfo = modelInfo
		self.__originModelInfo = copy.deepcopy( modelInfo )

		self.__mark = item.mark
		self.__mark.visible = False									# Ĭ��û���޸Ĺ�
		self.__modified = False


	# ----------------------------------------------------------------
	# pricate
	# ----------------------------------------------------------------
	def __toggleModified( self, modified ) :
		"""
		�����޸�״̬
		"""
		self.__modified = modified
		self.__mark.visible = True
		if modified :												# �޸Ĺ�û����
			util.setGuiState( self.__mark, ( 1, 2 ), ( 1, 1 ) )
		else :														# �޸Ĺ��Ѿ�����
			util.setGuiState( self.__mark, ( 1, 2 ), ( 1, 2 ) )
		self.__pyAdjuster.onModifiedChanged__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def assignToRender( self ) :
		"""
		����ѡ���Ӧ��ģ�͸�����Ⱦ��
		"""
		resetModel = self.__pyRender.resetModel
		argCount = resetModel.im_func.func_code.co_argcount
		if argCount == 3 :
			resetModel( self.__modelInfo.mark, False )
		else :
			resetModel( self.__modelInfo.mark )
		self.__pyRender.modelPos = self.__modelInfo.position
		self.__pyRender.pitch = self.__modelInfo.pitch

	def setToOrigin( self ) :
		"""
		����ģ��
		"""
		resetModel = self.__pyRender.resetModel
		argCount = resetModel.im_func.func_code.co_argcount
		if argCount == 3 :
			resetModel( self.__modelInfo.mark, False )
		else :
			resetModel( self.__modelInfo.mark )
		self.__pyRender.modelPos = self.__originModelInfo.position
		self.__pyRender.pitch = self.__originModelInfo.pitch

	# -------------------------------------------------
	def moveX( self, x ) :
		"""
		�� X ����ƽ��
		"""
		if x == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.modelX += x
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__toggleModified( True )
		return True

	def moveY( self, y ) :
		"""
		�� Y ����ƽ��
		"""
		if y == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.modelY += y
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__toggleModified( True )
		return True

	def moveZ( self, z ) :
		"""
		�� Z ����ƽ��
		"""
		if z == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.modelZ += z
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__toggleModified( True )
		return True

	def movePitch( self, deltaPitch ) :
		"""
		�޸���б��
		"""
		if deltaPitch == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.pitch += deltaPitch
		self.__modelInfo.pitch = self.__pyRender.pitch
		self.__toggleModified( True )
		return True

	def resume( self ) :
		"""
		�ָ��ϴα�����״̬
		"""
		if self.__pyRender.model is None : return False
		if self.__originModelInfo.position :
			self.__pyRender.modelPos = Math.Vector3( self.__originModelInfo.position )
			self.__pyRender.pitch = self.__originModelInfo.pitch
			self.__modelInfo.position = self.__pyRender.modelPos
			self.__modelInfo.pitch = self.__pyRender.pitch
			self.__toggleModified( False )
			self.__mark.visible = False
			return False
		else :
			self.autoAdjust()
			self.__toggleModified( False )
		return True

	def autoAdjust( self ) :
		"""
		�Զ�����
		"""
		if self.__pyRender.model is None : return False
		self.__pyRender.autoAdapt()
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__modelInfo.pitch = self.__pyRender.pitch
		self.__toggleModified( True )
		return True

	# ---------------------------------------
	def save( self ) :
		"""
		����
		"""
		self.__pyRender.saveViewInfo( self.__modelInfo )
		self.__originModelInfo = copy.deepcopy( self.__modelInfo )
		self.__toggleModified( False )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getModelInfo( self ) :
		return self.__modelInfo

	def _getModified( self ) :
		return self.__modified


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	modelInfo = property( _getModelInfo )						# ��ȡģ����Ϣ
	modified = property( _getModified )							# ָ���Ƿ��Ѿ��޸�

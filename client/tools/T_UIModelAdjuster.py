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

_helpText = "@F{fc=(205,97,44)}使用方法：@B@D"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "查看目录“$cfgPath”是否存在。如果不存在，则创建一个。@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "调整并保存后，把文件“$cfgFile”发给程序。@B@B"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}模型列表：@D@B"
_helpText += "@S{4}窗口上面第一个版面上列出了所有模型，选择一个模型 0.5 秒后，所选择的模型将会"
_helpText += "在模型版面中显示。选中模型后，便可以在下面的操作版面上调整模型的位置，如果"
_helpText += "某个模型的位置被调整了，但还没保存，则模型选项后面将会出现一个“勾”；如果"
_helpText += "某个模型的位置被调整了，并且保存了，则模型选项后面将会出现一个“点”。@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}模型位置操作指引：@D@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "向左移动模型：点击按钮@I{p=guis/clienttools/uimodeladjuster/leftbtn.gui}@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "向右移动模型：点击按钮@I{p=guis/clienttools/uimodeladjuster/rightbtn.gui}@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "向上移动模型：点击按钮@I{p=guis/clienttools/uimodeladjuster/upbtn.gui}@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "向下移动模型：点击按钮@I{p=guis/clienttools/uimodeladjuster/downbtn.gui}@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "向内/外移动模型：把鼠标放到窗口的控制版面上，滚动鼠标滚轮。@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "让模型倾斜：把鼠标放到窗口的控制版面上，并按住 ALT 键，然后滚动鼠标滚轮。@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "恢复为上一次保存后的状态(将会取消修改标记)：双击控制版面@B{2}"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/topic.gui}"
_helpText += "让模型自动适应渲染器：按住 CTRL 键，然后双击控制版面@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}保存：@D@B"
_helpText += "@S{4}如果当前选中的模型被改变，而还没保存的话，则“保存”按钮可用，否则“保存”"
_helpText += "按钮显示为灰色状态。@B"
_helpText += "@S{4}如果点击了“关闭”按钮，但还有模型没有保存，则会弹出一个提示框，提示你是否"
_helpText += "要保存还没保存的模型位置设置。@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}帮助的帮助：@D@B"
_helpText += "@S{4}点击帮助窗口右上角的按钮“@I{p=guis/clienttools/uimodeladjuster/closebtn.gui}”"
_helpText += "便可以关闭帮助窗口。@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(205,97,44)}创世浪漫城：@D@B"
_helpText += "@I{p=guis/clienttools/uimodeladjuster/riding.gui;m='show_tips'}@B"
_helpText += "A：浪漫不！想不想学我啊？@BB：嗯！@BA：想？那赶快去充值啊！大把大把钞票充。@B"
_helpText += "B：阿哥，我没钱，怎么办呐？@BA：贷款呗！我房子车子都抵押了。@B"
_helpText += "B：可我没房没车啊 T_T。@BA：那你有女朋友不？@B"
_helpText += "B：那倒有一个，还挺 PL 的。@BA：压了吧！再 PL 也顶不上创世啊！刚好我的贷款还有点剩的，我可以帮你。@B"
_helpText += "B：喔！英雄，你等我...@B{2}"

_helpText += "---------------------@B"
_helpText += "@F{fc=(138,236,94)}"
_helpText += "版本：2.0@B"
_helpText += "版权：光宇科诗特@B"
_helpText += "作者：黄永伟@B"
_helpText += "网址：@L{t=http://www.cogame.cn;m='goto_website';cfc=(0,0,255);hfc=(255,255,255)}@B"

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

		self.__pyRender = None											# 要调整的模型观察器
		self.__tempPath = ""											# 配置的保存路径
		self.width = 260												# 默认不显示帮助

	def __initialize( self, wnd ) :
		self.__pyLPModels = ListPanel( wnd.lpModels.clipPanel, wnd.lpModels.scrollBar )	# 模型列表版面
		self.__pyLPModels.onItemSelectChanged.bind( self.__onModelItemSelected )
		self.__pyLPModels.itemPerScroll = False
		self.__pyLPModels.perScroll = 76.0

		self.__pyAdjustPanel = Control( wnd.adjustPanel )				# 模型控制版面
		self.__pyAdjustPanel.focus = True
		self.__pyAdjustPanel.mouseScrollFocus = True
		self.__pyAdjustPanel.onLDBClick.bind( self.__onAPLDBClick )
		self.__pyAdjustPanel.onMouseScroll.bind( self.__onAPMouseScroll )

		self.__pyCloseHelpBtn = Button( wnd.tpHelp.closeBtn )			# 关闭帮助按钮
		self.__pyCloseHelpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseHelpBtn.onLClick.bind( self.onCloseHelp_ )
		self.__pyTPHelp = CSTextPanel( wnd.tpHelp.clipPanel, wnd.tpHelp.scrollBar )	# 帮助提示版面
		self.__pyTPHelp.perScroll = 60
		self.__pyTPHelp.onComponentLClick.bind( self.__onHelpLinkClick )
		self.__pyTPHelp.onComponentMouseEnter.bind( self.__onHelpShowTip )
		self.__pyTPHelp.onComponentMouseLeave.bind( self.__onHelpHideTip )

		self.__pyLBtn = Button( wnd.adjustPanel.leftBtn )				# 左移按钮
		self.__pyLBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyLBtn.onLMouseDown.bind( self.__leftMove )
		self.__pyRBtn = Button( wnd.adjustPanel.rightBtn )				# 右移按钮
		self.__pyRBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRBtn.onLMouseDown.bind( self.__rightMove )
		self.__pyUBtn = Button( wnd.adjustPanel.upBtn )					# 上移按钮
		self.__pyUBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyUBtn.onLMouseDown.bind( self.__upMove )
		self.__pyDBtn = Button( wnd.adjustPanel.downBtn )				# 下移按钮
		self.__pyDBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDBtn.onLMouseDown.bind( self.__downMove )

		self.__pyTBNuance = TextBox( wnd.tbNuance )						# 微调值输入
		self.__pyTBNuance.inputMode = InputMode.FLOAT
		self.__pyTBNuance.text = "10"

		self.__pySaveBtn = Button( wnd.saveBtn )						# 保存按钮
		self.__pySaveBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pySaveBtn.onLClick.bind( self.__onSaveBtnClick )

		self.__pyCloseBtn = Button( wnd.closeBtn1 )						# 取消按钮
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
		选中某个模型
		"""
		if pyItem is None : return
		if self.__pyRender.getConfigKey() == pyItem.modelInfo.mark :
			return
		pyItem.assignToRender()
		self.__pySaveBtn.enable = pyItem.modified

	# -------------------------------------------------
	def __leftMove( self ) :
		"""
		左移模型
		"""
		self.__pyLPModels.pySelItem.moveX( self.__getNuance() )

	def __rightMove( self ) :
		"""
		右移模型
		"""
		self.__pyLPModels.pySelItem.moveX( -self.__getNuance() )

	def __upMove( self ) :
		"""
		上移模型
		"""
		self.__pyLPModels.pySelItem.moveY( self.__getNuance() )

	def __downMove( self ) :
		"""
		下移模型
		"""
		self.__pyLPModels.pySelItem.moveY( -self.__getNuance() )

	def __onAPLDBClick( self, mods ) :
		"""
		双击模型控制版面
		"""
		if BigWorld.isKeyDown( KEY_LCONTROL ) :					# 按住 CTRL 键双击
			self.__pyLPModels.pySelItem.autoAdjust()			# 自动适配模型
		else :													# 直接双击
			self.__pyLPModels.pySelItem.resume()				# 恢复原来状态

	def __onAPMouseScroll( self, dz ) :
		"""
		鼠标滚轮在模型控制版面上滚动
		"""
		if BigWorld.isKeyDown( KEY_LALT ) :										# 按住 ALT 键
			if dz > 0 :
				self.__pyLPModels.pySelItem.movePitch( -self.__getNuance() )	# 调整昂角
			else :
				self.__pyLPModels.pySelItem.movePitch( self.__getNuance() )
		else :																	# 直接滚动
			if dz > 0 :
				self.__pyLPModels.pySelItem.moveZ( -self.__getNuance() )		# 调整远近
			else :
				self.__pyLPModels.pySelItem.moveZ( self.__getNuance() )

	def __onSaveBtnClick( self ) :
		"""
		点击保存按钮
		"""
		self.__pyLPModels.pySelItem.save()
		datas = self.__pyRender.configDatas_
		if gbref.PyConfiger().write( datas, self.__tempPath ) :
			# "保存成功"
			showAutoHideMessage( 3.0, 0x0c02, "" )
		else :
			# "保存失败，路径“%s”不存在"
			showAutoHideMessage( 5.0, mbmsgs[0x0c03] % self.__tempPath, "" )

	def __onCloseBtnClick( self ) :
		"""
		点击关闭按钮
		"""
		self.hide()

	# -------------------------------------------------
	def __onHelpLinkClick( self, pyCom ) :
		if pyCom.linkMark == "goto_website" :
			# "@A{C}我是大懒人，网站还没建设好，@B哈哈@I{p=maps/emote/emote_13.gui}"
			showAutoHideMessage( 5.0, 0x0c04, "" )

	def __onHelpShowTip( self, pyCom ) :
		if pyCom.linkMark == "show_tips" :
			toolbox.infoTip.showToolTips( self, "带老婆一起去玩创世喽！@A{C}@I{p=maps/emote/emote_13.gui}" )
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
		显示帮助
		"""
		self.width = 512.0

	def onCloseHelp_( self ) :
		"""
		关闭帮助
		"""
		self.width = 260


	# ----------------------------------------------------------------
	# friend methods of model item
	# ----------------------------------------------------------------
	def onModifiedChanged__( self, pyItem ) :
		"""
		选中的模型修改状态改变时被调用
		"""
		self.__pySaveBtn.enable = pyItem.modified


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCHName( self ) :
		return "UI 模型编辑器"

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
			# "没有可调整的模型"
			showAutoHideMessage( 5.0, 0x0c05, "" )
			return

		self.__pyRender = pyRender
		importPath = "tempconfigs/%s" % pyRender.cfgName			# 配置的临时 import 路径
		self.__tempPath = "common/" + importPath					# 临时配置的保存路径
		datas = gbref.PyConfiger().read( importPath, {}, True )		# 临时配置字典
		datas = self.__pyRender.configDatas_
		if datas is None :
			# "模型观察器不包含“__config”属性，不能调整"
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
		关闭
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
				# "保存成功!"
				showAutoHideMessage( 3.0, 0x0c02, "" )
			else :
				# "保存失败，路径“%s”不存在"
				showAutoHideMessage( 5.0, mbmsgs[0x0c03] % self.__tempPath, "" )

		def respond( pyItem, res ) :
			if res == RS_YES :									# 点击了 是 按钮
				saveAll()
				close()
			elif res == RS_NO :									# 点击了 否 按钮
				close()
			else :												# 点击了 取消 按钮
				pyItem.selected = True							# 选中没保存的模型

		pyMItem = None											# 找出是否有没修改的模型
		for pyItem in self.__pyLPModels.pyItems :
			if pyItem.modified :
				pyMItem = pyItem
				break
		if pyMItem :											# 如果有没修改的模型，则提示修改
			# "有的模型更改了还没保存，你要保存吗？"
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
		self.__mark.visible = False									# 默认没有修改过
		self.__modified = False


	# ----------------------------------------------------------------
	# pricate
	# ----------------------------------------------------------------
	def __toggleModified( self, modified ) :
		"""
		更改修改状态
		"""
		self.__modified = modified
		self.__mark.visible = True
		if modified :												# 修改过没保存
			util.setGuiState( self.__mark, ( 1, 2 ), ( 1, 1 ) )
		else :														# 修改过已经保存
			util.setGuiState( self.__mark, ( 1, 2 ), ( 1, 2 ) )
		self.__pyAdjuster.onModifiedChanged__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def assignToRender( self ) :
		"""
		将本选项对应的模型赋给渲染器
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
		设置模型
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
		在 X 轴上平移
		"""
		if x == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.modelX += x
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__toggleModified( True )
		return True

	def moveY( self, y ) :
		"""
		在 Y 轴上平移
		"""
		if y == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.modelY += y
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__toggleModified( True )
		return True

	def moveZ( self, z ) :
		"""
		在 Z 轴上平移
		"""
		if z == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.modelZ += z
		self.__modelInfo.position = self.__pyRender.modelPos
		self.__toggleModified( True )
		return True

	def movePitch( self, deltaPitch ) :
		"""
		修改倾斜度
		"""
		if deltaPitch == 0 : return False
		if self.__pyRender.model is None : return False
		self.__pyRender.pitch += deltaPitch
		self.__modelInfo.pitch = self.__pyRender.pitch
		self.__toggleModified( True )
		return True

	def resume( self ) :
		"""
		恢复上次保存后的状态
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
		自动调整
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
		保存
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
	modelInfo = property( _getModelInfo )						# 获取模型信息
	modified = property( _getModified )							# 指出是否已经修改

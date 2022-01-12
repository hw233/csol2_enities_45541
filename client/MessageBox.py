# -*- coding: gb18030 -*-
#
# $Id: MessageBox.py,v 1.11 2008-08-11 07:20:00 huangyongwei Exp $


import BigWorld
from Function import Functor
from config.client.msgboxtexts import Datas
messagebox = None

# --------------------------------------------------------------------
# 对话框返回值
# --------------------------------------------------------------------
RS_OK			= 0x01						# 点击了确定按钮
RS_CANCEL		= 0x02						# 点击的取消按钮
RS_YES			= 0x04						# 点击了是按钮
RS_NO			= 0x08						# 点击了否按钮
RS_SPE_CANCEL	= 0x10						# 点击了特殊的取消按钮
RS_SPE_OK       = 0x20						# 点击了立即传送按钮
RS_SPE_CAN		= 0x40						# 点击了取消传送按钮

# --------------------------------------------------------------------
# 对话框按钮值
# --------------------------------------------------------------------
MB_OK					= RS_OK							# 显示：确定按钮
MB_CANCEL				= RS_CANCEL						# 显示：取消按钮
MB_SPE_CANCEL			= RS_SPE_CANCEL					# 显示：特殊取消按钮
MB_OK_CANCEL			= RS_OK | RS_CANCEL				# 显示：确定、取消按钮
MB_YES_NO				= RS_YES | RS_NO				# 显示：是、否按钮
MB_YES_NO_CANCEL		= RS_YES | RS_NO | RS_CANCEL	# 显示：是、否、取消按钮
MB_SPE_OK_CANCEL		= RS_SPE_OK | RS_SPE_CAN        # 显示：立即传送、取消传送按钮

# --------------------------------------------------------------------
# 显示消息框
# --------------------------------------------------------------------
def showMessage( msgID, title, btns, callback = lambda rsbtn : rsbtn, pyOwner = None, gstStatus = None ) :
	"""
	@type		msgID	 : int/str
	@param		msgID	 : 消息 ID 或消息文本
	@type		title	 : str
	@param		title	 : 消息标题
	@type		btns	 : MACRO DEFINATION
	@param		btns	 : 显示按钮( MB_OK / MB_CANCEL / MB_OK_CANCEL / MB_YES_NO / MB_NONE )
	@type		callback : functor
	@param		callback : 回调，必须有一个参数，用以标示点击了哪个按钮：RS_OK / RS_CANCEL / RS_YES / RS_NO
	@type		pyOwner	 : python ui
	@param		pyOwner	 : 所属父窗口实例
	@type		gstStatus: MACRO Definations
	@param		gstStatus: 在指定状态下显示，如果当前不处于这种状态，将会等到该状态出现后才显示（在 Define.py 中定义：GST_XXX）
	@return				 : None
	"""
	msg = Datas.get( msgID, msgID )
	global messagebox
	if not messagebox :
		messagebox = __import__( "guis/tooluis/messagebox" )
	if btns == MB_OK :
		return messagebox.showOk( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_CANCEL :
		return messagebox.showCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_SPE_CANCEL :
		return messagebox.showSpecialCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_OK_CANCEL :
		return messagebox.showOkCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_YES_NO :
		return messagebox.showYesNo( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_YES_NO_CANCEL :
		return messagebox.showYesNoCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_SPE_OK_CANCEL:
		return messagebox.showSpecialOkCancel( msg, title, callback, pyOwner, gstStatus )

# --------------------------------------------------------------------
# 显示消息框（持续指定的一段时间后，自动按点击了默认按钮关闭）
# --------------------------------------------------------------------
__cbids = {}

def _agentCallback( delayOrder, callback, resID ) :
	"""
	callback 中转
	"""
	callback( resID )
	BigWorld.cancelCallback( __cbids.pop( delayOrder ) )

def __delayOption( pyBox ) :
	"""
	message box 的显示时间到期
	"""
	pyBox.hide()

def showAutoHideMessage( lastTime, msgID, title, btns = MB_OK, callback = lambda rsbtn : rsbtn, pyOwner = None, gstStatus = None ) :
	"""
	@type		lastTime : int
	@param		lastTime : 持续时间( 秒 )
	@type		msgID	 : int/str
	@param		msgID	 : 消息 ID 或消息文本
	@type		title	 : str
	@param		title	 : 消息标题
	@type		btns	 : MACRO DEFINATION
	@param		btns	 : 显示按钮( MB_OK / MB_OK_CANCEL / MB_YES_NO / MB_NONE )
	@type		callback : functor
	@param		callback : 回调，必须有一个参数，用以标示点击了哪个按钮：RS_OK / RS_CANCEL / RS_YES / RS_NO
	@type		pyOwner	 : python ui
	@param		pyOwner	 : 所属父窗口实例
	@return				 : None
	"""
	delayOrder = 0
	while delayOrder in __cbids : delayOrder += 1
	agentCallback = Functor( _agentCallback, delayOrder, callback )
	pyBox = showMessage( msgID, title, btns, agentCallback, pyOwner, gstStatus )
	__cbids[delayOrder] = BigWorld.callback( lastTime, Functor( __delayOption, pyBox ) )
	return pyBox

# -*- coding: gb18030 -*-
#
# $Id: Debug.py,v 1.12 2008-09-03 03:04:52 huangyongwei Exp $

"""
implement ui events are not contained by engine
-- 2008/05/29 : writen by huangyongwei
"""

# gui global( 按字母顺序排列 )
output_del_ScreenViewerWaklGuider	= True							# 是否输出删除角色移动提示指针的信息
output_del_ScriptWrapper			= False							# 是否输出删除引擎 UI Script 封装器的删除信息

# common( 按字母顺序排列 )
output_del_GUIBaseObject			= False							# 是否输出删除 GUIBaseObject 信息
output_del_PageWindow				= False							# 是否输出删除分页窗口的信息
output_del_RootGUI					= False							# 是否输出删除 Root 信息
output_del_ScriptObject				= False							# 是否输出删除 ScriptObject 信息
output_del_Window					= False							# 是否输出删除窗口信息
output_del_WndResizer				= False							# 是否输出删除窗口大小更换器信息

# controls( 按字母顺序排列 )
output_del_BaseObjectItem			= False							# 是否输出删除物品 Item 信息
output_del_BuffItem					= False							# 是否输出删除 Buff Item 信息
output_del_Button					= False							# 是否输出删除按钮信息
output_del_CheckBox					= False							# 是否输出删除复选框的信息
output_del_CheckerGroup				= False							# 是否输出删除选中控件组合框的信息
output_del_CircleCDCover			= False							# 是否输出删除CircleCDCover的消息
output_del_CircleShader				= False							# 是否输出删除CircleShader的消息
output_del_ClipPanel				= False							# 是否输出删除 ClipPanel 的信息
output_del_ClipShader				= False							# 是否输出删除 ClipShader 的信息
output_del_ComboBox					= False							# 是否输出删除组合框的信息
output_del_ContextMenu				= False							# 是否输出删除上下文菜单的信息
output_del_Control					= False							# 是否输出删除控件信息
output_del_ControlEvent				= False							# 是否输出删除控件事件信息
output_del_CooldownCover			= False							# 是否输出删除树视图的信息
output_del_Icon						= False							# 是否输出删除 Item 信息
output_del_Item						= False							# 是否输出删除 Item 信息
output_del_ItemsPanel				= False							# 是否输出删除多行多列子项的列表板面信息
output_del_Label					= False							# 是否输出删除标签控件信息
output_del_LinkImage				= False							# 是否输出删除超链接图像的信息
output_del_LinkLabel				= False							# 是否输出删除超链接标签的信息
output_del_ListItem					= False							# 是否输出删除列表选项信息
output_del_ListPanel				= False							# 是否输出删除单列子项列表板面信息
output_del_ModelRender				= False							# 是否输出删除模型 UI 渲染器的信息
output_del_MultilineRichTextBox		= False							# 是否输出删除多行输入控件的信息
output_del_ODListPanel				= False							# 是否输出删除自绘列表版面的信息
output_del_ODComboBox				= False							# 是否输出删除组合框的信息
output_del_ODListView				= False							# 是否输出删除列表视图的信息
output_del_ODPagesPanel				= False							# 是否输出删除翻页版面信息
output_del_RadioButton				= False							# 是否输出删除单选框的信息
output_del_RichText					= False							# 是否输出删除静态多行文本的信息
output_del_RichTextBox				= False							# 是否输出删除单行丰富文本信息
output_del_RichTextElem				= False							# 是否输出删除多行文本显示控件的信息
output_del_SelectorGroup			= False							# 是否输出删除选中控件组合框的信息
output_del_ScrollBar				= False							# 是否输出删除滚动条信息
output_del_ScrollPanel				= False							# 是否输出删除带滚动条板面信息
output_del_Skill					= False							# 是否输出删除技能 Item 信息
output_del_Splitter					= False							# 是否输出删除分隔条信息
output_del_StaticLabel				= False							# 是否输出删除静态标签信息
output_del_StaticText				= False							# 是否输出删除静态文本信息
output_del_TabCtrl					= False							# 是否输出删除选项卡信息
output_del_TabSwitcher				= False							# 是否输出删除焦点转移器信息
output_del_TextBox					= False							# 是否输出删除文本输入框信息
output_del_TextCheckBox				= False							# 是否输出删除带文本复选框的信息
output_del_TextPanel				= False							# 是否输出删除带滚动条文本框信息
output_del_TrackBar					= False							# 是否输出删除滑动条信息
output_del_TreeView					= False							# 是否输出删除树视图的信息

# tooluis( 按字母顺序排列 )
output_del_ColorBoard				= True							# 是否输出删除调色板的信息
output_del_EmotionBox				= True							# 是否输出删除表情选择窗口的信息
output_del_FullText					= True							# 是否输出删除浮动显示截断文本提示的信息
output_del_InfoTip					= True							# 是否输出删除提示框的信息
output_del_InputBox					= True							# 是否输出删除输入文本或数量的信息
output_del_ItemCover				= True							# 是否输出删除 Item 蒙板信息
output_del_Keyboard					= True							# 是否输出删除虚拟键盘信息
output_del_MessageBox				= True							# 是否输出删除消息框的信息
output_del_MoneyInputBox			= True							# 是否输出删除金钱输入框的消息
output_del_OperationTip				= True							# 是否输出删除 U I操作提示窗口的消息
output_del_RollBox					= True							# 是否输出删除消息框的信息

# login uis( 按字母顺序排列 )
output_LoginDialogGuarder			= True							# 是否输出删除密保界面的信息
output_del_AutoActWindow			= True							# 是否输出删除自动激活界面的信息

# general uis( 按字母顺序排列 )
output_del_AddRelationBox			= False							# 是否输出试衣间窗口销毁信息
output_del_AntiRabotWindow			= True							# 是否输出删除防外挂窗口信息
output_del_AutoFightWindow			= True							# 是否输出删除自动战斗设置窗口信息
output_del_BigMapNPCLister			= True							# 是否输出删除大地图中 NPC 列表窗口的信息
output_del_BigMapWorldSubBoard 		= True							# 是否输出删除世界地图中子地图板块的信息
output_del_ChallengeApplyWnd		= False							# 是否输出家族挑战窗口字信息
output_del_ChatChanneFilter			= True							# 是否输出删除频道过滤器的信息
output_del_ChatColorSetter			= True							# 是否输出删除频道颜色设置板面
output_del_ChatMSGPage				= True							# 是否输出删除聊天接收消息分页的信息
output_del_CommissionSale			= False							# 是否输出寄售模型选择窗口销毁信息
output_del_CSGoodsPanel				= True							# 是否输出删除寄售物品查询界面的信息
output_del_CSMerchantPanel			= True							# 是否输出删除寄售商人查询界面的信息
output_del_CSPetPanel				= True							# 是否输出删除寄售宠物查询界面的信息
output_del_EspialWindow				= True							# 是否输出删除宠物属性查看窗口的信息
output_del_Exp2Potential			= True							# 是否输出删除经验换潜能窗口的信息
output_del_ExplainWnd				= False							# 是否输出商城窗口销毁信息
output_del_FittingPanel				= False							# 是否输出试衣间窗口销毁信息
output_del_GameSetting				= True							# 是否输出删除游戏设置窗口的信息
output_del_GameLogWindow			= True							# 是否输出删除创世记事簿窗口的信息
output_del_KeyNotifier				= False							# 是否输出过程帮助提示按钮销毁信息
output_del_NavigateWindow			= False							# 是否输出寻路窗口销毁信息
output_del_ReadWindow				= False							# 是否输出邮件阅读窗口销毁信息
output_del_ReviveBox				= True							# 是否输出删除复活窗口的信息
output_del_SendDamageMsgs			= False							# 是否输出数据发布窗口信息
output_del_SystemWindow				= False							# 是否输出系统管理窗口的调试信息
output_del_TeammateBox				= True							# 是否输出删除队友创口信息
output_del_TongAD					= False							# 是否输出帮会传单窗口信息
output_del_TongMoneyGUI				= False							# 是否输出资金窗口调试信息
output_del_TSGoodsPanel				= True							# 是否输出删除寄售物品面板的信息
output_del_TSPetPanel				= True							# 是否输出删除寄售宠物面板的信息
output_del_UpgradeHelper			= True							# 是否输出删除升级提示窗口信
output_del_PLMChatWindow			= True							# 是否输出删除玩伴聊天窗口的消息
output_del_PLMLogWindow				= True							# 是否输出删除玩伴聊天记录窗口的消息
output_del_TbExplainWnd				= True							# 是否输出删除七夕活动说明窗口信息
output_del_TbVoteWnd				= True							# 是否输出删除七夕活动投票窗口信息
output_del_MsgBoard					= True							# 是否输出删除七夕留言窗口信息
output_del_ArtiRefine				= True							# 是否输出删除装备炼化窗口信息
output_del_ScenePlayer				= True							# 是否输出删除剧情播放窗口信息


# otheruis( 按字母顺序排列 )
output_del_BubbleTip				= False							# 是否输出删除冒泡窗口信息
output_del_CenterMessage			= False							# 是否输出删除屏幕中间显示信息的 UI
output_del_AnimatedGUI				= True							# 是否输出闪烁标记销毁信息
output_del_FloatName				= False							# 是否输出角色和怪物头顶文字信息
output_del_FlyText					= False							# 是否输出文冒冒血字信息


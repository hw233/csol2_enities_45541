# -*- coding: gb18030 -*-
#
# $Id: Debug.py,v 1.12 2008-09-03 03:04:52 huangyongwei Exp $

"""
implement ui events are not contained by engine
-- 2008/05/29 : writen by huangyongwei
"""

# gui global( ����ĸ˳������ )
output_del_ScreenViewerWaklGuider	= True							# �Ƿ����ɾ����ɫ�ƶ���ʾָ�����Ϣ
output_del_ScriptWrapper			= False							# �Ƿ����ɾ������ UI Script ��װ����ɾ����Ϣ

# common( ����ĸ˳������ )
output_del_GUIBaseObject			= False							# �Ƿ����ɾ�� GUIBaseObject ��Ϣ
output_del_PageWindow				= False							# �Ƿ����ɾ����ҳ���ڵ���Ϣ
output_del_RootGUI					= False							# �Ƿ����ɾ�� Root ��Ϣ
output_del_ScriptObject				= False							# �Ƿ����ɾ�� ScriptObject ��Ϣ
output_del_Window					= False							# �Ƿ����ɾ��������Ϣ
output_del_WndResizer				= False							# �Ƿ����ɾ�����ڴ�С��������Ϣ

# controls( ����ĸ˳������ )
output_del_BaseObjectItem			= False							# �Ƿ����ɾ����Ʒ Item ��Ϣ
output_del_BuffItem					= False							# �Ƿ����ɾ�� Buff Item ��Ϣ
output_del_Button					= False							# �Ƿ����ɾ����ť��Ϣ
output_del_CheckBox					= False							# �Ƿ����ɾ����ѡ�����Ϣ
output_del_CheckerGroup				= False							# �Ƿ����ɾ��ѡ�пؼ���Ͽ����Ϣ
output_del_CircleCDCover			= False							# �Ƿ����ɾ��CircleCDCover����Ϣ
output_del_CircleShader				= False							# �Ƿ����ɾ��CircleShader����Ϣ
output_del_ClipPanel				= False							# �Ƿ����ɾ�� ClipPanel ����Ϣ
output_del_ClipShader				= False							# �Ƿ����ɾ�� ClipShader ����Ϣ
output_del_ComboBox					= False							# �Ƿ����ɾ����Ͽ����Ϣ
output_del_ContextMenu				= False							# �Ƿ����ɾ�������Ĳ˵�����Ϣ
output_del_Control					= False							# �Ƿ����ɾ���ؼ���Ϣ
output_del_ControlEvent				= False							# �Ƿ����ɾ���ؼ��¼���Ϣ
output_del_CooldownCover			= False							# �Ƿ����ɾ������ͼ����Ϣ
output_del_Icon						= False							# �Ƿ����ɾ�� Item ��Ϣ
output_del_Item						= False							# �Ƿ����ɾ�� Item ��Ϣ
output_del_ItemsPanel				= False							# �Ƿ����ɾ�����ж���������б������Ϣ
output_del_Label					= False							# �Ƿ����ɾ����ǩ�ؼ���Ϣ
output_del_LinkImage				= False							# �Ƿ����ɾ��������ͼ�����Ϣ
output_del_LinkLabel				= False							# �Ƿ����ɾ�������ӱ�ǩ����Ϣ
output_del_ListItem					= False							# �Ƿ����ɾ���б�ѡ����Ϣ
output_del_ListPanel				= False							# �Ƿ����ɾ�����������б������Ϣ
output_del_ModelRender				= False							# �Ƿ����ɾ��ģ�� UI ��Ⱦ������Ϣ
output_del_MultilineRichTextBox		= False							# �Ƿ����ɾ����������ؼ�����Ϣ
output_del_ODListPanel				= False							# �Ƿ����ɾ���Ի��б�������Ϣ
output_del_ODComboBox				= False							# �Ƿ����ɾ����Ͽ����Ϣ
output_del_ODListView				= False							# �Ƿ����ɾ���б���ͼ����Ϣ
output_del_ODPagesPanel				= False							# �Ƿ����ɾ����ҳ������Ϣ
output_del_RadioButton				= False							# �Ƿ����ɾ����ѡ�����Ϣ
output_del_RichText					= False							# �Ƿ����ɾ����̬�����ı�����Ϣ
output_del_RichTextBox				= False							# �Ƿ����ɾ�����зḻ�ı���Ϣ
output_del_RichTextElem				= False							# �Ƿ����ɾ�������ı���ʾ�ؼ�����Ϣ
output_del_SelectorGroup			= False							# �Ƿ����ɾ��ѡ�пؼ���Ͽ����Ϣ
output_del_ScrollBar				= False							# �Ƿ����ɾ����������Ϣ
output_del_ScrollPanel				= False							# �Ƿ����ɾ����������������Ϣ
output_del_Skill					= False							# �Ƿ����ɾ������ Item ��Ϣ
output_del_Splitter					= False							# �Ƿ����ɾ���ָ�����Ϣ
output_del_StaticLabel				= False							# �Ƿ����ɾ����̬��ǩ��Ϣ
output_del_StaticText				= False							# �Ƿ����ɾ����̬�ı���Ϣ
output_del_TabCtrl					= False							# �Ƿ����ɾ��ѡ���Ϣ
output_del_TabSwitcher				= False							# �Ƿ����ɾ������ת������Ϣ
output_del_TextBox					= False							# �Ƿ����ɾ���ı��������Ϣ
output_del_TextCheckBox				= False							# �Ƿ����ɾ�����ı���ѡ�����Ϣ
output_del_TextPanel				= False							# �Ƿ����ɾ�����������ı�����Ϣ
output_del_TrackBar					= False							# �Ƿ����ɾ����������Ϣ
output_del_TreeView					= False							# �Ƿ����ɾ������ͼ����Ϣ

# tooluis( ����ĸ˳������ )
output_del_ColorBoard				= True							# �Ƿ����ɾ����ɫ�����Ϣ
output_del_EmotionBox				= True							# �Ƿ����ɾ������ѡ�񴰿ڵ���Ϣ
output_del_FullText					= True							# �Ƿ����ɾ��������ʾ�ض��ı���ʾ����Ϣ
output_del_InfoTip					= True							# �Ƿ����ɾ����ʾ�����Ϣ
output_del_InputBox					= True							# �Ƿ����ɾ�������ı�����������Ϣ
output_del_ItemCover				= True							# �Ƿ����ɾ�� Item �ɰ���Ϣ
output_del_Keyboard					= True							# �Ƿ����ɾ�����������Ϣ
output_del_MessageBox				= True							# �Ƿ����ɾ����Ϣ�����Ϣ
output_del_MoneyInputBox			= True							# �Ƿ����ɾ����Ǯ��������Ϣ
output_del_OperationTip				= True							# �Ƿ����ɾ�� U I������ʾ���ڵ���Ϣ
output_del_RollBox					= True							# �Ƿ����ɾ����Ϣ�����Ϣ

# login uis( ����ĸ˳������ )
output_LoginDialogGuarder			= True							# �Ƿ����ɾ���ܱ��������Ϣ
output_del_AutoActWindow			= True							# �Ƿ����ɾ���Զ�����������Ϣ

# general uis( ����ĸ˳������ )
output_del_AddRelationBox			= False							# �Ƿ�������¼䴰��������Ϣ
output_del_AntiRabotWindow			= True							# �Ƿ����ɾ������Ҵ�����Ϣ
output_del_AutoFightWindow			= True							# �Ƿ����ɾ���Զ�ս�����ô�����Ϣ
output_del_BigMapNPCLister			= True							# �Ƿ����ɾ�����ͼ�� NPC �б��ڵ���Ϣ
output_del_BigMapWorldSubBoard 		= True							# �Ƿ����ɾ�������ͼ���ӵ�ͼ������Ϣ
output_del_ChallengeApplyWnd		= False							# �Ƿ����������ս��������Ϣ
output_del_ChatChanneFilter			= True							# �Ƿ����ɾ��Ƶ������������Ϣ
output_del_ChatColorSetter			= True							# �Ƿ����ɾ��Ƶ����ɫ���ð���
output_del_ChatMSGPage				= True							# �Ƿ����ɾ�����������Ϣ��ҳ����Ϣ
output_del_CommissionSale			= False							# �Ƿ��������ģ��ѡ�񴰿�������Ϣ
output_del_CSGoodsPanel				= True							# �Ƿ����ɾ��������Ʒ��ѯ�������Ϣ
output_del_CSMerchantPanel			= True							# �Ƿ����ɾ���������˲�ѯ�������Ϣ
output_del_CSPetPanel				= True							# �Ƿ����ɾ�����۳����ѯ�������Ϣ
output_del_EspialWindow				= True							# �Ƿ����ɾ���������Բ鿴���ڵ���Ϣ
output_del_Exp2Potential			= True							# �Ƿ����ɾ�����黻Ǳ�ܴ��ڵ���Ϣ
output_del_ExplainWnd				= False							# �Ƿ�����̳Ǵ���������Ϣ
output_del_FittingPanel				= False							# �Ƿ�������¼䴰��������Ϣ
output_del_GameSetting				= True							# �Ƿ����ɾ����Ϸ���ô��ڵ���Ϣ
output_del_GameLogWindow			= True							# �Ƿ����ɾ���������²����ڵ���Ϣ
output_del_KeyNotifier				= False							# �Ƿ�������̰�����ʾ��ť������Ϣ
output_del_NavigateWindow			= False							# �Ƿ����Ѱ·����������Ϣ
output_del_ReadWindow				= False							# �Ƿ�����ʼ��Ķ�����������Ϣ
output_del_ReviveBox				= True							# �Ƿ����ɾ������ڵ���Ϣ
output_del_SendDamageMsgs			= False							# �Ƿ�������ݷ���������Ϣ
output_del_SystemWindow				= False							# �Ƿ����ϵͳ�����ڵĵ�����Ϣ
output_del_TeammateBox				= True							# �Ƿ����ɾ�����Ѵ�����Ϣ
output_del_TongAD					= False							# �Ƿ������ᴫ��������Ϣ
output_del_TongMoneyGUI				= False							# �Ƿ�����ʽ𴰿ڵ�����Ϣ
output_del_TSGoodsPanel				= True							# �Ƿ����ɾ��������Ʒ������Ϣ
output_del_TSPetPanel				= True							# �Ƿ����ɾ�����۳���������Ϣ
output_del_UpgradeHelper			= True							# �Ƿ����ɾ��������ʾ������
output_del_PLMChatWindow			= True							# �Ƿ����ɾ��������촰�ڵ���Ϣ
output_del_PLMLogWindow				= True							# �Ƿ����ɾ����������¼���ڵ���Ϣ
output_del_TbExplainWnd				= True							# �Ƿ����ɾ����Ϧ�˵��������Ϣ
output_del_TbVoteWnd				= True							# �Ƿ����ɾ����Ϧ�ͶƱ������Ϣ
output_del_MsgBoard					= True							# �Ƿ����ɾ����Ϧ���Դ�����Ϣ
output_del_ArtiRefine				= True							# �Ƿ����ɾ��װ������������Ϣ
output_del_ScenePlayer				= True							# �Ƿ����ɾ�����鲥�Ŵ�����Ϣ


# otheruis( ����ĸ˳������ )
output_del_BubbleTip				= False							# �Ƿ����ɾ��ð�ݴ�����Ϣ
output_del_CenterMessage			= False							# �Ƿ����ɾ����Ļ�м���ʾ��Ϣ�� UI
output_del_AnimatedGUI				= True							# �Ƿ������˸���������Ϣ
output_del_FloatName				= False							# �Ƿ������ɫ�͹���ͷ��������Ϣ
output_del_FlyText					= False							# �Ƿ������ððѪ����Ϣ


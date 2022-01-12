# -*- coding: gb18030 -*-
# TongPanelģ��ר��

from guis import *
from LabelGather import labelGather
from guis.controls.ContextMenu import DefMenuItem
from ChatFacade import chatFacade
from  Time import Time
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine

class PlayerNameMItem( DefMenuItem ):
	"""
	��ʾѡ�е��������
	"""
	def __init__( self, text = "" ) :
		DefMenuItem.__init__( self, text )
		self.enable = False

	def check( self, player, pyItem ):
		self.text = pyItem.getName()
		return True

	def do( self, player, pyItem ):
		pass

class SendMessageMItem( DefMenuItem ) :
	"""
	������Ϣ�Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:RelationPanel", "sendMsg" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() != player.databaseID and pyItem.isOnline()

	def do( self, player, pyItem ):
		chatFacade.whisperWithChatWindow( pyItem.getName() )

class InviteFriendMItem( DefMenuItem ) :
	"""
	���������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:RelationPanel", "addFriend" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() != player.databaseID

	def do( self, player, pyItem ):
		player.addFriend( pyItem.getName() )

class InviteTeamMItem( DefMenuItem ) :
	"""
	��������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:RelationPanel", "teamInvite" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() != player.databaseID and pyItem.isOnline()

	def do( self, player, pyItem ):
		player.inviteJoinTeam( pyItem.getName() )

class InviteSweetHeartMItem( DefMenuItem ) :
	"""
	���������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:RelationPanel", "sweetInvite" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() != player.databaseID and pyItem.isOnline()

	def do( self, player, pyItem ):
		player.addSweetieByName( pyItem.getName() )

class ChangeToBlackGroupMItem( DefMenuItem ) :
	"""
	�������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:RelationPanel", "blackList" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() != player.databaseID

	def do( self, player, pyItem ):
		player.addBlacklist( pyItem.getName() )

class QuitTongMItem( DefMenuItem ) :
	"""
	�˳�����Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:TongPanel", "quitTong" ), time = 0, name = "" ) :
		DefMenuItem.__init__( self, text )
		self.endTime = time
		self.tongName = name

	def check( self, player, pyItem ):
		return pyItem.getID() == player.databaseID and self.endTime <= Time.time()

	def do( self, player, pyItem ):
		def query( rs_id ):
			if rs_id == RS_OK:
				player.tong_quit()
		showMessage( mbmsgs[0x06e2] % self.tongName, "", MB_OK_CANCEL, query )

class CancelDismissTongMItem( DefMenuItem ) :
	"""
	ȡ����ɢ�Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:TongPanel", "cancelDiss" ), time = 0 ) :
		DefMenuItem.__init__( self, text )
		self.endTime = time

	def check( self, player, pyItem ):
		return pyItem.getID() == player.databaseID and player.tong_grade == csdefine.TONG_DUTY_CHIEF and self.endTime > Time.time()

	def do( self, player, pyItem ):
		player.tong_cancelDismissTong()

class AbdicationMItem( DefMenuItem ) :
	"""
	������λ�Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:TongPanel", "cheifYield" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() != player.databaseID and player.tong_grade == csdefine.TONG_DUTY_CHIEF

	def do( self, player, pyItem ):
		def query( rs_id ):
			if rs_id == RS_OK:
				player.tong_abdication( pyItem.getID() )
		# "ȷ��������֮λ�ø�%s?"
		showMessage( mbmsgs[0x06e3] % pyItem.getName(), "", MB_OK_CANCEL, query )

class KickOutMItem( DefMenuItem ) :
	"""
	�������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:TongPanel", "leaveTong" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		tong_grade = player.tong_grade
		tongGrade = player.tong_memberInfos[pyItem.getID()].getGrade()
		canKickMember = player.tong_checkDutyRights( tongGrade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
		return pyItem.getID() != player.databaseID and canKickMember and tong_grade > pyItem.getTongGrade()

	def do( self, player, pyItem ):
		def query( rs_id ):
			if rs_id == RS_OK:
				player.tong_kickMember( pyItem.getID() )
		# "ȷ��������֮λ�ø�%s?"
		showMessage( mbmsgs[0x06e4] % pyItem.getName(), "", MB_OK_CANCEL, query )

class DismissTongMItem( DefMenuItem ) :
	"""
	��ɢ����Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:TongPanel", "dissTong" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return pyItem.getID() == player.databaseID and player.tong_grade == csdefine.TONG_DUTY_CHIEF

	def do( self, player, pyItem ):
		player.cell.onDismissTong()

class RemarkMItem( DefMenuItem ) :
	"""
	����Ա��ע�˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:TongPanel", "memberMark" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return player.databaseID and player.tong_grade == csdefine.TONG_DUTY_CHIEF

	def do( self, player, pyItem ):
		ECenter.fireEvent( "EVT_ON_POPUP_REMARKBOX", pyItem.getID() ) #������Ա��ע��

class CloseMItem( DefMenuItem ):
	"""
	�رղ˵�
	"""
	def __init__( self, text = labelGather.getText( "RelationShip:RelationPanel", "shutDown" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player, pyItem ):
		return True

	def do( self, player, pyItem ):
		pass
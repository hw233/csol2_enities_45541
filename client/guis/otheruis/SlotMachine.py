# -*- coding: gb18030 -*-
#

from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.common.PyGUI import PyGUI
from guis.common.GUIBaseObject import GUIBaseObject
from config.client.msgboxtexts import Datas as mbmsgs
import Timer
import random
from Function import Functor
from guis.controls.Control import Control
from guis.otheruis.AnimatedGUI import AnimatedGUI

NUM_MULTIPLE = { 1:0,3:2,5:3 }	#������������Ը����Ķ�Ӧ��ϵ
TOTAL_IMAGE = 4

class SlotMachine( Window ):
	
	def __init__( self ):
		wnd = GUI.load( "guis/otheruis/slotMachine/slotMachine.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )		
		
		self.params = ()
		self.__controller = None
		self.__pyContainers = []
		self.__playSign = {0: False,1:False,2:False }
		
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		
	def __initialize( self, wnd ):
		self.__pyBtnGold = Button( wnd.btnGold )
		self.__pyBtnGold.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnGold.onLClick.bind( self.__lotteryUsingGold )
		
		self.__pyBtnQuit = Button( wnd.btnQuit )
		self.__pyBtnQuit.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnQuit.onLClick.bind( self.__quit )
		
		self.__pyHandGUI = HandGUI( wnd.btnStart,self )	#��������
		self.__pyHandGUI.initAnimation( 1, 12, ( 3, 4 ) )			# ��������һ�Σ���5֡��5��һ��
		self.__pyHandGUI.cycle = 1
		self.__pyHandGUI.visible = True
				
		pyContainer1 = Container( wnd.picture1 )
		pyContainer2 = Container( wnd.picture2 )
		pyContainer3 = Container( wnd.picture3 )
		self.__pyContainers.append( pyContainer1)
		self.__pyContainers.append( pyContainer2)
		self.__pyContainers.append( pyContainer3)	

	def __registerTriggers( self ):	
		self.__triggers["EVT_ON_SLOT_MACHINE_SHOW"] = self.__onShow	
		self.__triggers["EVT_ON_SLOT_MACHINE_RECEIVE_MULTIPLE"] = self.__onReceiveMutiple					
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
			
	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
			
	def __lotteryUsingGold( self ):
		"""
		ʹ��Ԫ���齱
		"""
		def query( rs_id ):
			if rs_id == RS_YES:
				self.__lottery( True )
		showMessage( mbmsgs[ 0x10af ] ,"", MB_YES_NO, query )
		
	def __lottery( self,useGold = False ):
		"""
		�齱
		"""
		questID, rewardIndex, codeStr, questTargetID = self.params
		player = BigWorld.player()
		player.getQuestRewardSlots( questID, rewardIndex, codeStr, questTargetID, useGold )
		
	def __quit( self ):
		self.hide()
		
	def __onShow( self, *args ):
		self.params = args
		self.__playSign = {0: False,1:False,2:False }
		Window.show( self )
		
	def __onReceiveMutiple( self, multiple ):
		"""
		���ս�� ͼ�������ͣ����
		"""
		assert multiple in [1,3,5],"multiple %d must in [1,3,5]"%multiple
		Timer.cancel( self.__controller )
		self.__controller = None
		self.__playSign = {0: False,1:False,2:False }
		sameNum = NUM_MULTIPLE[multiple]
		result = self.__getPIndex( sameNum )
		functor = Functor( self.__play, result )
		self.__controller = Timer.addTimer( 0,3, functor )
		
	def __play( self,showDict ):
		"""
		����ͼƬ����ͣ����
		"""
		
		for index, pyContainer in enumerate( self.__pyContainers ):
			if self.__playSign[index] == False:
				pyContainer.play( showDict[index])
				self.__playSign[index] = True
				return				
		Timer.cancel( self.__controller )
		self.__controller = None
		self.__pyHandGUI.focus = True 	#����ͼ��ȫ��ֹͣ���������������							
		
	def __getPIndex( self,sameNum ):
		"""
		������ͬ�ĸ��������ȡ��ÿһ�е�ͼƬ�������ڼ���ͼƬ����1��ʼ��
		"""
		result = {0:0,1:0, 2:0}
		
		b = range(1,TOTAL_IMAGE +1 )
		
		if sameNum == 0:
			bcopy = copy.copy(b)
			result[0] = random.choice( bcopy )
			bcopy.remove(result[0])
			result[1] = random.choice(bcopy)
			bcopy.remove(result[1])
			result[2] = random.choice(bcopy)
		if sameNum == 2:
			bcopy = copy.copy(b)
			keylist = result.keys()
			dif = random.choice( keylist )
			result[dif] = random.choice(bcopy)
			keylist.remove(dif)
			bcopy.remove(result[dif])
			
			result[keylist[0]] = random.choice(bcopy)
			result[keylist[1]] = result[keylist[0]]
		if sameNum == 3:
			result[0] = random.choice(b)
			result[1] = result[0]
			result[2] = result[0]
	
		return result	
		
		
	#----------------------------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def startLottert( self ):
		"""
		�ֶ���������
		"""
		self.__lottery()
		
	def hide( self ):
		self.params = ()
		Timer.cancel( self.__controller )
		self.__controller = None
		self.__playSign = {0: False,1:False,2:False }
		Window.hide( self )
		
	def onLeaveWorld( self ) :
		self.hide()
		
class Container( GUIBaseObject ):
	def __init__( self, gui ):
		GUIBaseObject.__init__( self, gui )
		self.__pyPicture = PictureGUI( gui.picture , self )
		self.__pyPicture.initAnimation( 2, 50, 4 )
		self.__pyPicture.cycle = 0.3
		self.__pyPicture.texture = "guis/otheruis/slotMachine/pictureStop.dds"	
								
	def play( self, showIndex = 1 ):		
		self.__pyPicture.playAnimation( showIndex)
	
class PictureGUI( GUIBaseObject ):
	
	PICTURE_DICT = { 1:119, 2:238, 3:357, 4:476}
	
	def __init__( self, gui, pyBinder = None ):
		GUIBaseObject.__init__( self, gui )
		self.__loopCounter = 0							# ��¼��ѭ�����ٴ�
		self.__loopAmount = -1							# ѭ����˸���ٴκ��Զ�ֹͣ(Ϊ��������ѭ��)
		self.__loopSpeed = 1.0							# ÿ֡��ʱ�䣨��λ���룩
		self.__space = 0								#�˶�״̬��һ���ƶ��ľ���
		self.__startTop = self.height * 4
		self.__pAmount = 0								#ͼƬ����
		self.__loopCBID = 0								# �˶�״̬��ѭ��timerID
		
		self.__state = 0 								#��ʼ״̬ 0��ֹͣ 1��ת��
		
		self.__preTop = 0								#Ҫ��ʾ��ͼƬ��ǰһ��ͼƬ��λ�ã��������ȵ�Ҫ��ʾ��ͼƬ
		self.__loopCBID2 = 0							# ��ֹ״̬��ѭ��timerID
		
		self.showIndex = 1
		
	def __loop( self ) :
		"""
		ѭ����˸
		"""
		if self.__startTop <=0 :	# ѭ����һȦ
			loopAmount = self.__loopAmount
			if loopAmount > 0 :							# ����趨��ѭ������
				self.__loopCounter += 1
				if self.__loopCounter >= loopAmount :	# ѭ�������ѵ�
					self.reset_()						# ѭ������
					self.stopPlay_()
					self.__showPicture()
					return
			self.__startTop = self.height * 4					# ���»ص���ʼλ��
		self.mapping = util.getGuiMapping( ( 128, 1024 ),0, 90, self.__startTop, self.__startTop + 119)
		self.__startTop -= self.__space
		self.__loopCBID = BigWorld.callback( self.__loopSpeed, self.__loop )
		
	def reset_( self ) :
		"""
		���趯��������
		"""
		self.__loopCounter = 0
		self.__startTop = self.height * 4	
		
	def stopPlay_( self ) :
		"""
		�˶�״̬��ֹͣ���Ŷ���
		"""	
		if self.__loopCBID :
			BigWorld.cancelCallback( self.__loopCBID )
			self.__loopCBID = 0
		
	def __showPicture( self ):
		"""
		����һ��ͼƬ��������
		"""
		if self.__loopCBID2 :
			BigWorld.cancelCallback( self.__loopCBID2 )
			self.__loopCBID2 = 0
		self.state = 0
		preTop = self.PICTURE_DICT[ self.showIndex]	
		self.__preTop = preTop
		self.__slip( )
		
	def __slip( self ):
		endTop = self.PICTURE_DICT[ self.showIndex] - 119
		if abs( endTop - self.__preTop ) < 30:
			self.stopPlay2_()		
			return		
		self.__preTop -= 20
		self.mapping = util.getGuiMapping( ( 128, 1024 ),0, 90, self.__preTop, self.__preTop + 119)
		self.__loopCBID2 = BigWorld.callback( 0.1, self.__slip )
		
	def stopPlay2_( self ) :
		"""
		"""	
		self.stopPlay_()
		if self.__loopCBID2 :
			BigWorld.cancelCallback( self.__loopCBID2 )
			self.__loopCBID2 = 0
		self.mapping = util.getStateMapping(( 90, 119 ),( 5, 1 ),( self.showIndex, 1 ) )		
		
	def initAnimation( self, loopAmount,space, pAmount ) :
		self.__loopAmount = loopAmount
		self.__space = space
		self.__pAmount = pAmount
				
	def playAnimation( self, showIndex ):
		"""
		���Ŷ���
		"""
		self.mapping = util.getStateMapping(( 90, 119 ),( 5, 1 ),( 1, 1 ) )
		self.showIndex = showIndex
		self.state = 1
		self.reset_()
		self.__loop()
		
	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getSpf( self ) :
		"""
		��ȡһ֡���ٶ�
		"""
		return self.__loopSpeed

	def _setSpf( self, spf ) :
		"""
		����һ֡���ٶ�
		"""
		self.__loopSpeed = spf

	def _getCycle( self ) :
		"""
		��ȡ����
		"""
		return self.__loopSpeed * ( (self.height*self.__pAmount)/float( self.__space ) )

	def _setCycle( self, cycle ) :
		"""
		��������
		"""
		self.__loopSpeed = float( cycle ) / ( (self.height*self.__pAmount)/float( self.__space ) )
	
	def _getState( self ):
		return self.__state
		
	def _setState( self, state ):
		if state == 0:		#ֹͣ״̬
			self.texture = "guis/otheruis/slotMachine/pictureStop.dds"
		else:				#�˶�״̬
			self.texture = "guis/otheruis/slotMachine/pictureMove.dds"
		self.__state = state
		
	state = property( _getState, _setState )
	spf = property( _getSpf, _setSpf )					# ��ȡ/����ÿ֡��ʱ��( second per frame )
	cycle = property( _getCycle, _setCycle )			# ��ȡ/�������ڣ�ѭ��һ�ε�ʱ�䣩
	
	
class HandGUI( Control, AnimatedGUI ):
	def __init__( self, gui, pyBinder = None ) :
		AnimatedGUI.__init__( self, gui )
		Control.__init__( self, gui, pyBinder )
		self.focus = True
		
	def onLClick_( self, mods ) :
		"""
		�����������ʱ������
		"""
		Control.onLClick_( self, mods )
		self.playAnimation()
		self.focus = False
		self.pyBinder.startLottert()
		return True
	
	def reset_( self ) :
		"""
		���趯��������
		"""
		AnimatedGUI.reset_( self)
		self.visible = True	
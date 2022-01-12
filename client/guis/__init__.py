# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.55 2008-08-19 09:26:55 huangyongwei Exp $

"""
implement global methods about ui
2006/09/07 : writen by huangyongwei
"""

# --------------------------------------------------------------------
# common imports
# --------------------------------------------------------------------
# import python modules
import sys
import math
import copy

# import engine modules
import BigWorld
import Math
import GUI
import csol
import ResMgr
import Language

# import global modules in common
from bwdebug import *
from cscollections import Stack
from cscollections import Queue
from cscollections import MapList
from Weaker import RefEx
from Weaker import WeakList
from Weaker import WeakSet
from Function import Functor
import csarithmetic as arithmetic
import Function

# import global modules in client
import Define
import utils
import keys
import gbref
import event.EventCenter as ECenter
from keys import *
from Color import cscolors
from gbref import rds
from GameMgr import gameMgr
from ShortcutMgr import shortcutMgr

from MessageBox import showMessage
from MessageBox import showAutoHideMessage
from MessageBox import MB_OK
from MessageBox import MB_OK_CANCEL
from MessageBox import MB_YES_NO
from MessageBox import RS_OK
from MessageBox import RS_CANCEL
from MessageBox import RS_YES
from MessageBox import RS_NO

# import my utils
import Debug
import guis.util as util
import guis.scale_util as s_util
import UIScriptWrapper
from guis.uidefine import *
from RootUIsMgr import ruisMgr
from UIHandlerMgr import uiHandlerMgr

from guis.UIFixer import uiFixer
from guis.Toolbox import toolbox

# extra events
from guis.ExtraEvents import ControlEvent
from guis.ExtraEvents import LastMouseEvent
from guis.ExtraEvents import LastKeyDownEvent
from guis.ExtraEvents import LastKeyUpEvent

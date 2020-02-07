#!/usr/bin/python
#
# Copyright (c) 2007
# Beerios Brewing Company
# Lakewood, OH, USA
#
# All Rights Reserved
#
################################################################################
#
# File: SmartDriveProd.py
#
# Author: Chris Harley
#
# Description:
#
################################################################################
#
# Version History:
#
# $Log$
#
################################################################################

import sys
import os
import time
#import calendar
import wx
#import md5
import random

#global constants
VERSION_STRING = 'v001 :: 22-Sept-2007'
PART_NUMBER = '001-001-001'
ABOUT_STRING = 'Behavior Modeling Utility \n%s\n%s\nCopyright (c) 2007 Beerios BC, Inc.' % (PART_NUMBER, VERSION_STRING)

DEFAULT_NUMBER_OF_TRIALS = 1000
DEFAULT_RANDOM_SEED = 8192

#State Descriptions
STATE_DESCRIPTION = [	'Approach', \
						'Return', \
						'Antennal Contact', \
						'Both Over', \
						'Split Contact', \
						'Both Under', \
						'Climb', \
						'Tunnel', \
						'End', \
						'NUM_STATES', \
					]

#Transition Probabilities
LIGHT_TRANSITION_DEFAULTS = [ 	0.079,	# T0  - 0 to 1: Approach to Return
								1.000,	# T1  - 1 to 0: Return to Approach
								0.921,	# T2  - 0 to 2: Approach to Antennal Contact
								0.222,	# T3  - 2 to 1: Antennal Contact to Return
								0.097,	# T4  - 2 to 3: Antennal Contact to Both Over
								0.181,	# T5  - 2 to 4: Antennal Contact to Split Contact
								0.500,	# T6  - 2 to 5: Antennal Contact to Both Under
								0.263,	# T7  - 3 to 4: Both Over to Split Contact
								0.643,	# T8  - 4 to 5: Split Contact to Both Under
								0.357,	# T9  - 4 to 3: Split Contact to Both Over
								0.185,	# T10 - 5 to 4: Both Under to Split Contact
								0.037,	# T11 - 5 to 3: Both Under to Both Over
								0.736,	# T12 - 3 to 6: Both Over to Climbing
								0.778,	# T13 - 5 to 7: Both Under to Tunneling
								1.000,	# T14 - 6 to 8: Climbing to End
								1.000,	# T15 - 7 to 8: Tunneling to End
								0.000,	# T16 - 5 to 3: Tunneling to Both Over
							]

DARK_TRANSITION_DEFAULTS = [ 	0.173,	# T0  - 0 to 1: Approach to Return
								1.000,	# T1  - 1 to 0: Return to Approach
								0.827,	# T2  - 0 to 2: Approach to Antennal Contact
								0.252,	# T3  - 2 to 1: Antennal Contact to Return
								0.113,	# T4  - 2 to 3: Antennal Contact to Both Over
								0.296,	# T5  - 2 to 4: Antennal Contact to Split Contact
								0.339,	# T6  - 2 to 5: Antennal Contact to Both Under
								0.208,	# T7  - 3 to 4: Both Over to Split Contact
								0.414,	# T8  - 4 to 5: Split Contact to Both Under
								0.586,	# T9  - 4 to 3: Split Contact to Both Over
								0.222,	# T10 - 5 to 4: Both Under to Split Contact
								0.000,	# T11 - 5 to 3: Both Under to Both Over
								0.792,	# T12 - 3 to 6: Both Over to Climbing
								0.778,	# T13 - 5 to 7: Both Under to Tunneling
								1.000,	# T14 - 6 to 8: Climbing to End
								0.980,	# T15 - 7 to 8: Tunneling to End
								0.020,	# T16 - 5 to 3: Tunneling to Both Over
							]

							
#global UI constants
ID_ABOUT=101
ID_EXIT=110 




class TrialSettingsPanel(wx.Panel):

	def __init__(self, Parent, *args, **kwargs):
		wx.Panel.__init__(self, Parent, *args, **kwargs)
		self.Parent = Parent

		self.NumTrialsText = wx.TextCtrl(self,1) #,style=wx.TE_READONLY)
		self.NumTrialsText.SetMaxLength(15)
		self.NumTrialsText.WriteText(str(DEFAULT_NUMBER_OF_TRIALS))
		self.LightsCheck = wx.CheckBox(self, label="Lights On")
		self.LightsCheck.SetValue(False)
		#self.LicenseCheck.Bind(wx.EVT_CHECKBOX, self.OnCheck, id=self.LicenseCheck.GetId())
		
		TrialsBox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Number of Trials"), wx.HORIZONTAL)
		TrialsBox.Add(self.NumTrialsText, 1, wx.ALL, 5)
		TrialsBox.Add(self.LightsCheck, 1, wx.ALL, 5)
		self.SetSizer(TrialsBox)

	#def OnCheck(self, event):
		
	def	Reset(self):
		self.NumTrialsText.Clear()
		self.NumTrialsText.WriteText(str(DEFAULT_NUMBER_OF_TRIALS))
		self.LightsCheck.SetValue(False)

		
class RandomPanel(wx.Panel):

	def __init__(self, Parent, *args, **kwargs):
		wx.Panel.__init__(self, Parent, *args, **kwargs)
		self.Parent = Parent

		self.RandomText = wx.TextCtrl(self,1) #,style=wx.TE_READONLY)
		self.RandomText.SetMaxLength(15)
		self.RandomText.WriteText(str(DEFAULT_RANDOM_SEED))
		self.RandomCheck = wx.CheckBox(self, label="Random Seed")
		self.RandomCheck.SetValue(False)
		self.RandomCheck.Bind(wx.EVT_CHECKBOX, self.OnCheck, id=self.RandomCheck.GetId())
		
		RandomBox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Seed Value"), wx.HORIZONTAL)
		RandomBox.Add(self.RandomText, 1, wx.ALL, 5)
		RandomBox.Add(self.RandomCheck, 1, wx.ALL, 5)
		self.SetSizer(RandomBox)

	def OnCheck(self, event):
		if self.RandomCheck.GetValue():
			self.RandomText.SetEditable(False)
			self.RandomText.Clear()
			self.RandomText.WriteText(str(random.seed()))
		else:
			self.Reset()
		
	def	Reset(self):
		self.RandomText.SetEditable(True)
		self.RandomText.Clear()
		self.RandomText.WriteText(str(DEFAULT_RANDOM_SEED))
		self.RandomCheck.SetValue(False)

class ResultsPanel(wx.Panel):
	def __init__(self, Parent, *args, **kwargs):
		wx.Panel.__init__(self, Parent, *args, **kwargs)
		self.Parent = Parent
		
		self.StartButton = wx.Button(self, label="Start Trials", size=(125, -1))
		self.StartButton.Bind(wx.EVT_BUTTON, self.Parent.RunAllTrials)

		self.ClearButton = wx.Button(self, label="Clear", size=(125, -1))
		self.ClearButton.Bind(wx.EVT_BUTTON, self.Parent.ResetFrame)

		self.ResultsText = wx.TextCtrl(self,1,style=wx.TE_MULTILINE)

		ResultsBox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Comments"), wx.VERTICAL)
		ButtonBox = wx.BoxSizer(wx.HORIZONTAL)
		ButtonBox.Add(self.StartButton, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		ButtonBox.Add(self.ClearButton, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		ResultsBox.Add(ButtonBox, 0, wx.EXPAND|wx.ALL, 5)
		ResultsBox.Add(self.ResultsText, 1, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(ResultsBox)

	def Reset(self):
		self.ResultsText.Clear()


class BehaviorModel(wx.Frame):

	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (400, 500),
		                             style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)

		# Setting up the menu.
		filemenu= wx.Menu()
		filemenu.Append(ID_ABOUT, "&About"," Information about this program")
		filemenu.AppendSeparator()
		filemenu.Append(ID_EXIT,"&Exit"," Terminate the program")
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
		wx.EVT_MENU(self, ID_ABOUT, self.OnAbout) # attach the menu-event ID_ABOUT to the method self.OnAbout
		wx.EVT_MENU(self, ID_EXIT, self.OnExit)   # attach the menu-event ID_EXIT to the method self.OnExit
		self.CreateStatusBar() # A StatusBar in the bottom of the window

		# Creating the Content Panels		                             
		self.TrialSettingsPanel = TrialSettingsPanel(self, wx.ID_ANY)
		self.RandomPanel = RandomPanel(self, wx.ID_ANY)
		self.ResultsPanel = ResultsPanel(self, wx.ID_ANY)

		#Arranging the Content Panels
		TopBox = wx.BoxSizer(wx.VERTICAL)
		TopBox.Add(self.TrialSettingsPanel, 4, wx.EXPAND|wx.ALL, 0)
		TopBox.Add(self.RandomPanel, 4, wx.EXPAND|wx.ALL, 0)
		TopBox.Add(self.ResultsPanel, 24, wx.EXPAND|wx.ALL, 0)
		self.SetSizer(TopBox)

		self.Show(True)

	#Set all values back to default		
	#def ResetFrame(self):
		
	def OnAbout(self,e):
		d= wx.MessageDialog( self, "%s" % ABOUT_STRING,
		                    "About Behavior Modeling Tool.", wx.OK)
		                    # Create a message dialog box
		d.ShowModal() # Shows it
		d.Destroy() # finally destroy it when finished.

	def OnExit(self,e):
		self.Close(True)  # Close the frame.


	def ResetFrame(self, event):
		self.TrialSettingsPanel.Reset()
		self.RandomPanel.Reset()
		self.ResultsPanel.Reset()
		
	#returns true if climb, false if tunnel.
	#prints path to the results panel
	def RunSingleTrial(self, transition):
		
		current_state = 0
		
		while current_state < 8 :
			choice = random.random()
			self.ResultsPanel.ResultsText.WriteText(STATE_DESCRIPTION[current_state])
			self.ResultsPanel.ResultsText.WriteText(', ')

			if current_state == 0:
				if transition[0] > choice :
					current_state = 1
				elif (transition[2] + transition[0]) > choice :
					current_state = 2
			elif current_state == 1:
				current_state = 0
			elif current_state == 2:
				if transition[4] > choice :
					current_state = 3
				elif (transition[5] + transition[4]) > choice :
					current_state = 4
				elif (transition[6] + transition[5] + transition[4]) > choice :
					current_state = 5
			elif current_state == 3:
				if transition[7] > choice :
					current_state = 4
				elif (transition[12] + transition[7]) > choice :
					current_state = 6
			elif current_state == 4:
				if transition[8] > choice :
					current_state = 5
				elif (transition[9] + transition[8]) > choice :
					current_state = 3
			elif current_state == 5:
				if transition[10] > choice :
					current_state = 4
				elif (transition[13] + transition[10]) > choice :
					current_state = 7
				elif (transition[11] + transition[13] + transition[10]) > choice :
					current_state = 3
			elif current_state == 6:
				current_state = 8
				return True 
			elif current_state == 7:
				if transition[15] > choice :
					current_state = 8
					return False
				elif (transition[16] + transition[15]) > choice :
					current_state = 3
			else:
				current_state = 8
				return None
		return None

		
	def PrintTransitions(self, transitions):
		self.ResultsPanel.ResultsText.WriteText('Transition Values Are:\n')
		for i in transitions :
			self.ResultsPanel.ResultsText.WriteText('%.3f\n' % i)
		self.ResultsPanel.ResultsText.WriteText('\n')	
		
	def RunAllTrials(self, event):
		
		#eventually get these from a transitions probability panel
		if self.TrialSettingsPanel.LightsCheck.GetValue() :
			self.ResultsPanel.ResultsText.WriteText("\nUsing Light Transitions\n")
			transitions = LIGHT_TRANSITION_DEFAULTS
		else :
			self.ResultsPanel.ResultsText.WriteText("\nUsing Dark Transitions\n")
			transitions = DARK_TRANSITION_DEFAULTS
		self.PrintTransitions(transitions)
			
		if not self.RandomPanel.RandomCheck.GetValue() :
			seed = int(self.RandomPanel.RandomText.GetValue())
			self.ResultsPanel.ResultsText.WriteText('Random Number Seed: %i\n' % (seed))
			random.seed(seed)
		else:
			self.ResultsPanel.ResultsText.WriteText('Random Number Seed: None\n')
		
		numClimb = 0	
		numTunnel = 0
				
		num_trials = int(self.TrialSettingsPanel.NumTrialsText.GetValue())
		self.ResultsPanel.ResultsText.WriteText('\nStarting %i Trials . . .\n' %(num_trials))
		for i in range(num_trials) :
			self.ResultsPanel.ResultsText.WriteText(str(i))
			self.ResultsPanel.ResultsText.WriteText(' - ')
			result = self.RunSingleTrial(transitions)
			self.ResultsPanel.ResultsText.WriteText('\n')
			if result is None :
				print 'Error in Run'
				return 0
			elif result :
				numClimb = numClimb + 1
			else:
				numTunnel = numTunnel + 1
		
		#Print to result panel
		precentClimb = (float(numClimb) / float(num_trials)) * 100
		percentTunnel = (float(numTunnel) / float(num_trials)) * 100
		print '\n\n%.2f%% (%i/%i) Climb\n%.2f%% (%i/%i) Tunnel\n\n' % (precentClimb, numClimb, num_trials, percentTunnel, numTunnel, num_trials)
		self.ResultsPanel.ResultsText.WriteText('\n\n%.2f%% (%i/%i) Climb\n%.2f%% (%i/%i) Tunnel\n\n' % (precentClimb, numClimb, num_trials, percentTunnel, numTunnel, num_trials))


#Starts the Program
SdProg = wx.PySimpleApp()
frame = BehaviorModel(None, wx.ID_ANY, "Shelf Behavior Modeling Tool")
SdProg.MainLoop()

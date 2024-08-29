'''
  A ticketless 50/50 raffle
  
  This program presents three main screens:
    
    - A Setup screen, to collect the cost
      per ticket and the name of an
      optional JSON file with a list of 
      names to begin the entries list. 
    - An entries screen, listing people's
      names, with a number of tickets
      bought beneath each name (initially
      zero). There's also a text field
      to add in new entrant's names. 
      Tapping on a name adds one ticket sold
      each time. Once all the purchases
      have been made, pressing Draw will
      draw a winning ticket. 
    - The winner's page, which shows the
      name drawn, the number of entries
      and the dollar amount received,
      and the winner's pot (half the total).
      
    - After each raffle, a log is created
      tracking the amount paid, the pot,
      the winner, and how many tickets
      each person purchased.
      
  Initially customized for use by KofC
  Council 3660, Indianapolis, Indiana.  
'''

import ui
import json
import random
from datetime import date
from pathlib import Path

version = '1.02'

class Participents:
	def __init__(self):
		self.items = []
		self.entries = 0
		self.total = 0.0
		self.pot = 0.0
		
	# data_source methods	
	def tableview_number_of_sections(self, tableview):
		# Return the number of sections (defaults to 1)
		return 1

	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return len(self.items)

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		cell = ui.TableViewCell(style='subtitle')
		cell.text_label.text = self.items[row]['text_label']
		cell.detail_text_label.text = self.items[row]['detail_text_label']
		return cell

	def tableview_title_for_header(self, tableview, section):
		# Return a title for the given section.
		# If this is not implemented, no section headers will be shown.
		return ''

	def tableview_can_delete(self, tableview, section, row):
		# Return True if the user should be able to delete the given row.
		return True

	def tableview_can_move(self, tableview, section, row):
		# Return True if a reordering control should be shown for the given row (in editing mode).
		return False

	def tableview_delete(self, tableview, section, row):
		# Called when the user confirms deletion of the given row.
		del(ev['participents'].data_source.items[row])
		ev['participents'].reload_data()
		self.save_names()

	def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
		# Called when the user moves a row with the reordering control (in editing mode).
		pass
		
	# delegate methods	
	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		if ev['participents'].editing:
			incr = -1
		else:
			incr = 1
		ev['participents'].data_source.items[row]['count'] += incr
		ev['participents'].data_source.items[row]['detail_text_label'] = f'{ev["participents"].data_source.items[row]["count"]} tickets'
		ev['participents'].reload_data()
		self.calculate_total()
		ev['total'].text = f"${ev['participents'].data_source.total:,.2f}"
		ev['pot'].text = f"${ev['participents'].data_source.pot:,.2f}"

	def tableview_did_deselect(self, tableview, section, row):
		# Called when a row was de-selected (in multiple selection mode).
		pass

	def tableview_title_for_delete_button(self, tableview, section, row):
		# Return the title for the 'swipe-to-***' button.
		return 'Delete'
		
	# load and save the data_source
	def load_names(self):
		try:
			with open(self.filename, "r") as f:
				names = json.load(f)
				self.items = [{'text_label': n, 'detail_text_label': ' ', 'count': 0} for n in names]
				self.items.sort(key=lambda n: n['text_label'])
				return True
		except FileNotFoundError:
			self.items = []
			return False
			
	def save_names(self):
		names = [n['text_label'] for n in self.items]
		with open(self.filename,"w") as f:
			json.dump(names, f)
	
	def calculate_total(self):
		self.entries = sum([n['count'] for n in self.items])
		self.total = self.entries * self.ticketCost
		self.pot = self.total / 2
		
def setupComplete(sender):
	ev['participents'].delegate = ev['participents'].data_source = Participents()
	ev['participents'].data_source.filename = sv['filename'].text or '3660.json'
	ev['participents'].data_source.ticketCost = float(sv['ticketCost'].text)
	ev['participents'].data_source.load_names()
	ev['participents'].allows_selection_during_editing = True
	ev['total'].text = f"${ev['participents'].data_source.total:,.2f}"
	ev['pot'].text = f"${ev['participents'].data_source.pot:,.2f}"
	v['navView'].push_view(ev)
	
	
def newName(sender):
	name = sender.text
	sender.text = ''
	ev['participents'].data_source.items.append({'text_label': name, 'detail_text_label': ' ', 'count': 0})
	ev['participents'].data_source.items.sort(key=lambda n: n['text_label'])
	ev['participents'].reload_data()
	ev['participents'].data_source.save_names()
	
def toggleEditing(sender):
	if ev['participents'].editing == True:
		ev['participents'].set_editing(False)
	else:
		ev['participents'].set_editing(True)
	
def drawWinner(sender):
	try:
		winner = random.choices([n['text_label'] for n in ev['participents'].data_source.items], weights=[c['count'] for c in ev['participents'].data_source.items])
		winner = winner[0]
	except ValueError:
		winner = 'no tickets sold'
	ev['participents'].data_source.save_names()
	wv['winner'].text = winner
	ev['participents'].data_source.calculate_total()
	create_log(winner)
	wv['entries'].text = f"{ev['participents'].data_source.entries}"
	wv['total'].text = f"${ev['participents'].data_source.total:,.2f}"
	wv['pot'].text = f"${ev['participents'].data_source.pot:,.2f}"
	v['navView'].push_view(wv)
	
def create_log(winner):
	data = ev['participents'].data_source
	p = Path(data.filename).stem + '.log'
	entries = {d['text_label']: d['count'] for d in data.items}
	with open(p, "a") as f:
		print(f'{{ "timestamp": "{date.today()}", "winner": "{winner}", "total": {data.total:,.2f}, "entries": {data.entries}, "pot": {data.pot:,.2f} "salesrec": {entries} }}', file=f)

v = ui.load_view()
v.name = 'Fifty50'

sv = ui.load_view('setupView.pyui')
sv['logoImage'].image = ui.Image('IMG_0002.JPG')
sv['version'].text = f'version {version}'

ev = ui.load_view('entryView.pyui')

wv = ui.load_view('winnerView.pyui')

v['navView'].push_view(sv)

v.present('sheet')
from ._anvil_designer import RowTemplate1Template
from anvil import *


class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

  def button_1_click(self, **event_args):
    self.parent.raise_event("x-anmelden", kurs_id=self.item["kurs_id"])
from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
from .Anmelden import Anmelden


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.repeating_panel_1.items = anvil.server.call("get_kurse")
    self.set_event_handler("x-refresh", self.refresh_kurse)
    self.set_event_handler("x-anmelden", self.oeffne_anmeldung)

  def refresh_kurse(self, **event_args):
    self.repeating_panel_1.items = anvil.server.call("get_kurse")

  def oeffne_anmeldung(self, kurs_id=None, **event_args):
    alert(
      content=Anmelden(kurs_id=kurs_id),
      title="Mitglied anmelden",
      large=True,
      buttons=[]
    )
    self.refresh_kurse()
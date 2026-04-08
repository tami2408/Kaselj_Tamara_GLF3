from ._anvil_designer import AnmeldenTemplate
from anvil import *
import anvil.server


class Anmelden(AnmeldenTemplate):
  def __init__(self, kurs_id=None, **properties):
    self.init_components(**properties)
    self.kurs_id = kurs_id
    self.drop_down_1.items = anvil.server.call("get_mitglieder")

  def button_1_click(self, **event_args):
    try:
      mitglied_id = self.drop_down_1.selected_value
      anvil.server.call("anmelden", mitglied_id, self.kurs_id)
      alert("Anmeldung erfolgreich.")
      self.raise_event("x-close-alert")
      get_open_form().raise_event("x-refresh")
    except Exception as e:
      alert(str(e))
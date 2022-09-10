import json

from kivy.app import App
from kivy.factory import Factory
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
    StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class AddLocationForm(BoxLayout):
    search_input = ObjectProperty()
    search_results = ObjectProperty()
    def search_pokemon(self):
        poke = self.search_input.text
        url = f"https://pokeapi.co/api/v2/pokemon/{poke}"
        UrlRequest(
            url,
            on_success=self.found_location,
            on_failure=self.falhou,
        )

    def falhou(self, request, result):
        print("falhou", result)

    def found_location(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        pokes = []
        if self.search_input.text == "":
            for poke in data['results']:
                pokes += [{'text': f"{poke['name']}, ({poke['url']})"}]
        else:
            pokes = [{'text': f"{data['species']['name']}, ({data['species']['url']})"}]
        # print(pokes)
        self.search_results.data.extend(pokes)


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            App.get_running_app().root.show_pokemon(rv.data[index]['text'])
        else:
            print("selection removed for {0}".format(rv.data[index]))


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []


class WeatherRoot(BoxLayout):
    current_poke = ObjectProperty()

    def show_pokemon(self, pokename=None):
        self.clear_widgets()
        if self.current_poke is None:
            self.current_poke = CurrentPokemon()
        if pokename is not None:
            self.current_poke.pokename = pokename.split(',')[0]
        self.current_poke.update_pokemon()
        self.add_widget(self.current_poke)

    def search_pokemon_form(self):
        self.clear_widgets()
        self.add_widget(AddLocationForm())


class CurrentPokemon(BoxLayout):
    pokename = StringProperty([])
    type = StringProperty()
    sprite = StringProperty()

    def update_pokemon(self):
        url = f"https://pokeapi.co/api/v2/pokemon/{self.pokename}"
        UrlRequest(
            url,
            on_success=self.found_poke,
        )

    def found_poke(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.pokename = data['name']
        self.sprite = data['sprites']['front_default']
        self.type = data['types'][0]['type']['name']
        self.order = data['id']


class WeatherApp(App):
    pass


if __name__ == '__main__':
    WeatherApp().run()

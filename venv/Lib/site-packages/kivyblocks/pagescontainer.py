from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

class PageContainer(FloatLayout):
    def __init__(self,**kw):
        super().__init__(**kw)
        self.pageWidgets = []
        self.backButton = Button(text='<',size_hint=(None,None),height=40,width=40)
        self.backButton.bind(on_press=self.previous)

    def showLastPage(self):
        self.clear_widgets()
        if len(self.pageWidgets) < 1:
            return 
        w = self.pageWidgets[-1]
        w.pos = 0,0
        w.size = self.size
        self.add_widget(w)
        if len(self.pageWidgets) > 1:
            self.showBackButton()

    def previous(self,v):
        w = self.pageWidgets[-1]
        self.pageWidgets = self.pageWidgets[:-1]
        del w
        self.showLastPage()

    def add(self,widget):
        self.pageWidgets.append(widget)
        self.showLastPage()

    def showBackButton(self):
        self.backButton.pos = (4,self.height - self.backButton.height)
        self.add_widget(self.backButton)


if __name__ == '__main__':
    class Page(Button):
        def __init__(self,container,page_cnt = 1):
            self.container = container
            self.page_cnt = page_cnt
            Button.__init__(self,text = 'page' + str(page_cnt))
            self.bind(on_press=self.newpage)

        def newpage(self,v):
            p = Page(self.container,self.page_cnt + 1)
            self.container.add(p)

    class MyApp(App):
        def build(self):
            x = PageContainer()
            p = Page(x)
            x.add(p)
            return x

    MyApp().run()

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from kivymd.app import MDApp
from kivymd.uix.button import MDRoundFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout

import sqlite3
import os

Window.size = (360, 640)

def setup_database():
    if not os.path.exists("database"):
        os.makedirs("database")

    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

    def setup_ui(self):
        layout = FloatLayout()
        self.add_widget(layout)

        logo = Image(source='turbo_auto_pecas.png', size_hint=(1, 1.5), height=dp(100))
        layout.add_widget(logo)
        
        self.email_input = MDTextField(
            hint_text="E-mail",
            mode="rectangle",
            size_hint_y=None,
            height=dp(35)
        )
        self.email_input.pos_hint = {"center_x": 0.5, "center_y": 0.55}
        layout.add_widget(self.email_input)

        self.senha_input = MDTextField(
            hint_text="Senha",
            password=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(35)
        )
        self.senha_input.pos_hint = {"center_x": 0.5, "center_y": 0.45}
        layout.add_widget(self.senha_input)

        login_btn = MDRoundFlatButton(
            text="Login",
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            on_release=self.login
        )
        layout.add_widget(login_btn)

        cadastro_btn = MDRoundFlatButton(
            text="Cadastrar-se",
            pos_hint={"center_x": 0.5, "center_y": 0.25},
            on_release=self.go_to_cadastro
        )
        layout.add_widget(cadastro_btn)

    def login(self, instance):
        email = self.email_input.text
        senha = self.senha_input.text

        connection = sqlite3.connect('usuarios.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email=? AND senha=?', (email, senha))
        user = cursor.fetchone()
        connection.close()

        if user:
            dialog = MDDialog(
                title="Sucesso",
                text=f"Login realizado com sucesso!\nE-mail: {email}",
                size_hint=(0.8, 0.4)
            )
            dialog.open()
            self.manager.current = 'products'
        else:
            dialog = MDDialog(
                title="Erro",
                text="E-mail ou senha inválidos!",
                size_hint=(0.8, 0.4)
            )
            dialog.open()

    def go_to_cadastro(self, instance):
        self.manager.current = 'cadastro'

class CadastroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

    def setup_ui(self):
        layout = FloatLayout()
        self.add_widget(layout)

        self.nome_input = MDTextField(
            hint_text="Nome",
            mode="rectangle",
            size_hint_y=None,
            height=dp(40)
        )
        self.nome_input.pos_hint = {"center_x": 0.5, "center_y": 0.6}
        layout.add_widget(self.nome_input)

        self.email_input = MDTextField(
            hint_text="E-mail",
            mode="rectangle",
            size_hint_y=None,
            height=dp(40)
        )
        self.email_input.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        layout.add_widget(self.email_input)

        self.senha_input = MDTextField(
            hint_text="Senha",
            password=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(40)
        )
        self.senha_input.pos_hint = {"center_x": 0.5, "center_y": 0.4}
        layout.add_widget(self.senha_input)

        cadastrar_btn = MDRoundFlatButton(
            text="Cadastrar",
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            on_release=self.cadastrar
        )
        layout.add_widget(cadastrar_btn)

        voltar_btn = MDIconButton(
            icon='arrow-left',
            pos_hint={"right": 0.13, "top": 0.95},
            on_release=self.go_back
        )
        layout.add_widget(voltar_btn)

    def cadastrar(self, instance):
        nome = self.nome_input.text
        email = self.email_input.text
        senha = self.senha_input.text

        if nome and email and senha:
            try:
                connection = sqlite3.connect('usuarios.db')
                cursor = connection.cursor()
                cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
                connection.commit()
                connection.close()

                dialog = MDDialog(
                    title="Sucesso",
                    text=f"Cadastro realizado com sucesso!\nNome: {nome}\nE-mail: {email}",
                    size_hint=(0.8, 0.4)
                )
                dialog.open()
            except sqlite3.IntegrityError:
                dialog = MDDialog(
                    title="Erro",
                    text="E-mail já cadastrado!",
                    size_hint=(0.8, 0.4)
                )
                dialog.open()
        else:
            dialog = MDDialog(
                title="Erro",
                text="Preencha todos os campos!",
                size_hint=(0.8, 0.4)
            )
            dialog.open()

    def go_back(self, instance):
        self.manager.current = 'login'

class ProductsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = [] 
        self.setup_ui()

    def setup_ui(self):
        layout = FloatLayout()
        self.add_widget(layout)

        menu_button = MDIconButton(
            icon="menu",
            pos_hint={"x": 0.02, "top": 0.99},
            on_release=self.menu_action
        )
        layout.add_widget(menu_button)

        catalog_label = MDLabel(
            text="Catálogo",
            halign="left",
            pos_hint={"x": 0.15, "top": 0.9867},
            font_style="H5",
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(catalog_label)

        search_button = MDIconButton(
            icon="magnify",
            pos_hint={"right": 0.98, "top": 0.99},
            on_release=self.search_action
        )
        layout.add_widget(search_button)

        cart_button = MDIconButton(
            icon="cart",
            pos_hint={"right": 0.88, "top": 0.99},
            on_release=self.go_to_cart
        )
        layout.add_widget(cart_button)

        separator_card = MDCard(
            size_hint=(0.9, None),
            height=dp(7),
            pos_hint={"center_x": 0.5, "top": 0.92},
            orientation='vertical'
        )
        separator_card.md_bg_color = (0.2, 0.2, 0.2, 1)
        layout.add_widget(separator_card)

        self.grid_layout = GridLayout(cols=2, padding=10, spacing=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.produtos = [
            {"nome": "Abafador", "preco": 29.99, "imagem": "assets/imagens/Abafador.png"},
            {"nome": "Caixa Cambio", "preco": 49.99, "imagem": "assets/imagens/Caixa_Cambio.png"},
            {"nome": "Correia", "preco": 39.99, "imagem": "assets/imagens/Correia.png"},
            {"nome": "Embreagem", "preco": 59.99, "imagem": "assets/imagens/Embreagem.png"},
            {"nome": "Suspensão", "preco": 19.99, "imagem": "assets/imagens/Suspensão.png"},
            {"nome": "Vela", "preco": 99.99, "imagem": "assets/imagens/Vela.png"}
        ]   

        for produto in self.produtos:
            card = MDCard(orientation="vertical", size_hint=(0.5, None), height=250, padding=10)
            card.add_widget(MDLabel(text=produto["nome"], halign="center", theme_text_color="Primary"))

            imagem = Image(
                source=produto["imagem"],
                size_hint=(1, 2.8),
                allow_stretch=True,
                keep_ratio=False
            )
            card.add_widget(imagem)

            price_cart_layout = FloatLayout(size_hint_y=None, height=40)
            preco_label = MDLabel(
                text=f"R$ {produto['preco']:.2f}",
                halign="center",
                theme_text_color="Hint",
                pos_hint={"center_x": 0.3, "center_y": 0.5}
            )
            price_cart_layout.add_widget(preco_label)

            btn_add = MDIconButton(
                icon="cart",
                pos_hint={"center_x": 0.8, "center_y": 0.5},
                on_release=lambda instance, produto=produto: self.add_to_cart(produto)
            )
            price_cart_layout.add_widget(btn_add)

            card.add_widget(price_cart_layout)
            self.grid_layout.add_widget(card)

        scroll_view = ScrollView(size_hint=(1, 0.9), pos_hint={"top": 0.9})
        scroll_view.add_widget(self.grid_layout)
        layout.add_widget(scroll_view)

        self.nav_drawer = MDNavigationDrawer()
        layout.add_widget(self.nav_drawer)

        menu = MDList()
        menu.add_widget(OneLineListItem(text="Início", on_release=self.menu_action))
        menu.add_widget(OneLineListItem(text="Produtos", on_release=self.menu_action))
        menu.add_widget(OneLineListItem(text="Carrinho", on_release=self.go_to_cart))
        menu.add_widget(OneLineListItem(text="Sair", on_release=self.logout))

        self.nav_drawer.add_widget(menu)

    def add_to_cart(self, produto):
        self.cart.append(produto)

    def go_to_cart(self, instance):
        self.manager.current = "cart"
        cart_screen = self.manager.get_screen("cart")
        cart_screen.cart = self.cart 
        cart_screen.setup_ui()  

    def search_action(self, instance):
        dialog = MDDialog(
            title="Pesquisar",
            text="Ação de pesquisa aqui",
            size_hint=(0.8, 0.4)
        )
        dialog.open()

    def menu_action(self, instance):
        self.nav_drawer.set_state("open")

    def logout(self, instance):
        self.nav_drawer.set_state("close")  
        self.manager.current = "login"

class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = [] 
        self.setup_ui()

    def setup_ui(self):
        self.clear_widgets()

        main_layout = FloatLayout()

        back_button = MDIconButton(
            icon="arrow-left",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"x": 0.0, "top": 0.98},
            on_release=self.go_back_to_products
        )
        main_layout.add_widget(back_button)

        title_label = Label(
            text="Carrinho de Compras",
            font_size='24sp',
            halign="center",
            size_hint_y=None,
            height=dp(50),
            pos_hint={"center_x": 0.5, "top": 0.98}
        )
        main_layout.add_widget(title_label)

        separator_card = MDCard(
            size_hint=(1, None),
            height=dp(7),
            pos_hint={"center_x": 0.5, "top": 0.90},
            orientation='vertical'
        )
        separator_card.md_bg_color = (0.2, 0.2, 0.2, 1)
        main_layout.add_widget(separator_card)

        scroll_view = ScrollView(size_hint=(1, None), size=(self.width, self.height - 100))
        cart_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        cart_layout.bind(minimum_height=cart_layout.setter('height'))

        if not self.cart:
            empty_label = MDLabel(
                text="Seu carrinho está vazio!",
                halign="center",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(40)
            )
            cart_layout.add_widget(empty_label)

        for product in self.cart:
            product_card = MDCard(size_hint=(1, None), height=dp(80))
            product_label = Label(
                text=f"{product['nome']} - R$ {product['preco']:.2f}",
                size_hint=(1, None),
                height=dp(60)
            )
            product_card.add_widget(product_label)

            remove_button = MDIconButton(
                icon="delete",
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                pos_hint={"right": 1, "center_y": 0.5},
                on_release=lambda instance, product=product: self.remove_from_cart(product)
            )
            product_card.add_widget(remove_button)
            cart_layout.add_widget(product_card)

        scroll_view.add_widget(cart_layout)
        main_layout.add_widget(scroll_view)

        checkout_button = MDRaisedButton(
            text="Finalizar Compra",
            size_hint=(1, None),
            height=dp(50),
            pos_hint={"center_x": 0.5}
        )
        main_layout.add_widget(checkout_button)

        self.add_widget(main_layout)

    def remove_from_cart(self, product):
        self.cart.remove(product)
        self.setup_ui()

    def go_back_to_products(self, instance):
        self.manager.current = "products"

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Gray"  
        self.theme_cls.primary_hue = "700"  
        self.theme_cls.accent_palette = "Orange"  
        self.theme_cls.theme_style = "Dark"  

        setup_database() 
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CadastroScreen(name='cadastro'))
        sm.add_widget(ProductsScreen(name='products'))
        sm.add_widget(CartScreen(name='cart'))

        return sm   

if __name__ == '__main__':
    MainApp().run()

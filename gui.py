import tkinter as gui
from tkinter import ttk
import sqlite3


class Contacts(gui.Tk):

	def __init__(self, *args, **kwargs):
		gui.Tk.__init__(self, *args, **kwargs)
		gui.Tk.title(self, 'Contact Book')
		self.resizable(False, False)

		recipient = gui.Frame(self, width=500, height=400, bg='grey')
		recipient.grid(row=0, column=0, sticky='nsew')

		self.frame = {}

		for F in (ViewClient, AddClient):
			frame = F(recipient, self)
			self.frame[F] = frame
			frame.grid(row=0, column=0, sticky='nsew')

		self.show_frame(ViewClient)

	def show_frame(self, container):
		frame = self.frame[container]
		frame.tkraise()


class ViewClient(gui.Frame):
	def __init__(self, parent, controller):
		gui.Frame.__init__(self, parent)

		self.mainframe = gui.Frame(master=self)
		self.mainframe.grid(row=0, column=0, sticky='nsew')

		self.parent = parent
		self.controller = controller
		self.interface()
		self.show_contacts()

		estilo = ttk.Style()
		estilo.configure('Treeview', font=('Console', 8))
		estilo.configure('Treeview.Heading', font=('Console', 10, 'bold'))

	def frames(self):
		self.topframe = gui.Frame(master=self.mainframe)
		self.topframe.grid(row=0, column=0, columnspan=2)
		self.midframe = gui.Frame(master=self.mainframe)
		self.midframe.grid(row=1, column=0, columnspan=4)
		self.lastframe = gui.Frame(master=self.mainframe)
		self.lastframe.grid(row=2, column=0, columnspan=2)

	def interface(self):
		self.frames()
		self.butoes_esquerda()
		self.lblframe_search()
		self.label_msg()
		self.tabela()
		self.scroll()
		self.butoes_baixo()

	def butoes_esquerda(self):
		btn_add = gui.Button(self.topframe, text='Adicionar', command=lambda: self.controller.show_frame(AddClient),
							 width=20,
							 height=1)
		btn_pesquisar = gui.Button(self.topframe, text='Pesquisar', command=self.pesquisar_contacto, width=20, height=1)
		btn_add.grid(row=0, column=0, padx=30, pady=5)
		btn_pesquisar.grid(row=1, column=0, padx=30)

	def lblframe_search(self):
		gui.Label(master=self.topframe, text='', width=30).grid(row=0, column=1, rowspan=2, sticky='ew')

		lbf_pesquisa = gui.LabelFrame(self.topframe, text='Pesquisar Contacto', width=100, bg='sky blue')
		lbf_pesquisa.grid(row=0, column=2, padx=20, pady=5, rowspan=2, sticky='e')

		lbl_psqnome = gui.Label(lbf_pesquisa, text='Nome:', bg='sky blue')
		self.ent_psqnome = gui.Entry(lbf_pesquisa, width=50)
		lbl_psqnum = gui.Label(lbf_pesquisa, text='Numero:', bg='sky blue')
		self.ent_psqnum = gui.Entry(lbf_pesquisa, width=50)
		lbl_psqnome.grid(row=0, column=0, sticky='w')
		lbl_psqnum.grid(row=1, column=0, sticky='w')
		self.ent_psqnome.grid(row=0, column=1, padx=(2, 5), pady=(0, 5))
		self.ent_psqnum.grid(row=1, column=1, padx=(2, 5), pady=(0, 5))

	def label_msg(self):
		self.msg = gui.Label(self.topframe, text='', fg='red')
		self.msg.grid(row=2, column=0, columnspan=3, sticky='ew')

	def tabela(self):
		self.tree = ttk.Treeview(master=self.midframe, height=10, columns=('numero', 'numero 2', 'email'),
								 style='Treeview')
		self.tree.grid(row=0, column=0, padx=(20, 0), columnspan=4)
		self.tree.heading('#0', text='Nome')
		self.tree.heading('numero', text='Numero de Telefone')
		self.tree.heading('numero 2', text='Telefone Alternativo')
		self.tree.heading('email', text='E-Mail')

	def scroll(self):
		self.scrollbar = gui.Scrollbar(master=self.midframe, orient='vertical', command=self.tree.yview)
		self.scrollbar.grid(row=0, column=4, rowspan=9, sticky='sn')

	def butoes_baixo(self):
		self.btn_del = gui.Button(self.lastframe, text='Apagar', width=20, height=1, command=self.apagar_contacto)
		self.btn_edit = gui.Button(self.lastframe, text='Editar', width=20, height=1, command=self.dados_modificar)
		self.btn_refresh = gui.Button(self.lastframe, text='Actualizar', width=20, height=1, command=self.show_contacts)
		self.btn_refresh.grid(row=0, column=0, padx=10, pady=(10, 15), sticky='ew')
		gui.Label(self.lastframe, text='', width=40).grid(row=0, column=1)
		self.btn_del.grid(row=0, column=2, padx=5, pady=(10, 15), sticky='ew')
		self.btn_edit.grid(row=0, column=3, padx=5, pady=(10, 15), sticky='ew')

	def show_contacts(self):
		self.msg['text'] = ''
		items = self.tree.get_children()
		for item in items:
			self.tree.delete(item)
		query = 'SELECT * FROM contacts_list order by id desc'
		connector = ConectDB()
		contact_entries = connector.execute_query(query)
		for row in contact_entries:
			self.tree.insert('', 0, text=row[1], values=(row[2], row[3], row[4]))

	def apagar_contacto(self):
		if self.tree.selection():
			try:
				nome = self.tree.item(self.tree.selection())['text']
				query = 'DELETE FROM contacts_list WHERE fullname = ?'
				db = ConectDB()
				db.execute_query(query, (nome,))
				self.show_contacts()
				self.msg['text'] = f'"{nome}" apagado com sucesso!'
			except Exception:
				self.msg['text'] = 'Não foi possível apagar contacto(s), por favor seleccione apenas 1 contacto por vez'
		else:
			self.msg['text'] = f'Por favor seleccione um contacto!'

	def dados_modificar(self):
		if self.tree.selection():
			self.curr_name = self.tree.item(self.tree.selection())['text']
			self.curr_nrmain = self.tree.item(self.tree.selection())['values'][0]
			self.curr_nrsec = self.tree.item(self.tree.selection())['values'][1]
			self.curr_email = self.tree.item(self.tree.selection())['values'][2]
			self.janela_modificar(self.curr_name, self.curr_nrmain, self.curr_nrsec, self.curr_email)
		else:
			self.msg['text'] = f'Por favor seleccione um contacto!'

	def janela_modificar(self, nome, mobile, altmobile, email):
		self.popup = gui.Toplevel()
		self.popup.geometry('400x120')
		self.popup.title('Actualizar Detalhes do Contacto')
		gui.Label(self.popup, text='Nome Completo').grid(row=0, column=0)
		gui.Entry(self.popup, textvariable=gui.StringVar(self.popup, value=nome), width=40, state='readonly').grid(row=0, column=1)
		gui.Label(self.popup, text='Numero Principal').grid(row=1, column=0, padx=10)
		self.novo_mobile = gui.Entry(self.popup, textvariable=gui.StringVar(self.popup, value=mobile), width=40)
		self.novo_mobile.grid(row=1, column=1, padx=10)
		gui.Label(self.popup, text='Numero Alternativo').grid(row=2, column=0)
		self.novo_altmobile = gui.Entry(self.popup, textvariable=gui.StringVar(self.popup, value=altmobile), width=40)
		self.novo_altmobile.grid(row=2, column=1, padx=10)
		gui.Label(self.popup, text='E-mail').grid(row=3, column=0)
		self.novo_email = gui.Entry(self.popup, textvariable=gui.StringVar(self.popup, value=email), width=40)
		self.novo_email.grid(row=3, column=1, padx=10)
		gui.Button(self.popup, text='Actualizar', command=self.actualizar_contacto).grid(row=4, column=0, columnspan=2, pady=5)

		self.popup.mainloop()

	def actualizar_contacto(self):
		query = 'UPDATE contacts_list SET main_num=?, alt_num=?, email=? WHERE fullname=?'
		parameters = (self.novo_mobile.get(), self.novo_altmobile.get(), self.novo_email.get(), self.curr_name)
		db = ConectDB()
		db.execute_query(query, parameters)
		self.popup.destroy()
		self.show_contacts()
		self.msg['text'] = f'Detalhes do contacto {self.curr_name} actualizados!'

	def pesquisar_contacto(self):
		query = 'SELECT fullname,main_num,alt_num,email FROM contacts_list WHERE fullname like ? or main_num like ?'
		pesq_nome = pesq_num = ''

		if self.ent_psqnome.get():
			pesq_nome = f'%{self.ent_psqnome.get()}%'

		if self.ent_psqnum.get():
			pesq_num = f'%{self.ent_psqnum.get()}%'

		if self.ent_psqnome.get() == '' and self.ent_psqnum.get() == '':
			pesq_nome = '%'

		parameters = (pesq_nome, pesq_num)
		db = ConectDB()
		pesquisados = db.execute_query(query, parameters)

		items = self.tree.get_children()
		for item in items:
			self.tree.delete(item)
		for row in pesquisados:
			self.tree.insert('', 0, text=row[0], values=(row[1], row[2], row[3]))


class AddClient(gui.Frame):
	def __init__(self, parent, controller):
		gui.Frame.__init__(self, parent)
		self.parent = parent
		self.controller = controller
		self.lblframe_addcontact()

	def lblframe_addcontact(self):
		lbf_addcontact = gui.LabelFrame(self, text='Adicionar Contacto', width=200)
		lbf_addcontact.grid(row=0, column=0, padx=40, pady=40, columnspan=2, sticky='nsew')

		self.message = gui.Label(lbf_addcontact, text='', fg='red')
		lbl_addnome = gui.Label(lbf_addcontact, text='Nome:', width=30)
		self.ent_addnome = gui.Entry(lbf_addcontact, width=80)
		lbl_addapelido = gui.Label(lbf_addcontact, text='Apelido:', width=30)
		self.ent_addapelido = gui.Entry(lbf_addcontact, width=80)
		lbl_addnum1 = gui.Label(lbf_addcontact, text='Numero principal:', width=30)
		self.ent_addnum1 = gui.Entry(lbf_addcontact, width=80)
		lbl_addnum2 = gui.Label(lbf_addcontact, text='Numero alternativo:', width=30)
		self.ent_addnum2 = gui.Entry(lbf_addcontact, width=80)
		lbl_addemail = gui.Label(lbf_addcontact, text='Email:', width=30)
		self.ent_addemail = gui.Entry(lbf_addcontact, width=80)
		self.btn_gravar = gui.Button(lbf_addcontact, text='Gravar', width=15, command=self.add_contact)
		self.btn_cancelar = gui.Button(lbf_addcontact, text='Cancelar/Voltar', width=15, command=self.cancelar)

		self.message.grid(row=0, column=0, columnspan=2, sticky='ew')
		lbl_addnome.grid(row=1, column=0, pady=5, sticky='e')
		lbl_addapelido.grid(row=2, column=0, pady=5, sticky='w')
		lbl_addnum1.grid(row=3, column=0, pady=5, sticky='w')
		lbl_addnum2.grid(row=4, column=0, pady=5, sticky='w')
		lbl_addemail.grid(row=5, column=0, pady=5, sticky='w')
		self.ent_addnome.grid(row=1, column=1, padx=(0, 10))
		self.ent_addapelido.grid(row=2, column=1, padx=(0, 10))
		self.ent_addnum1.grid(row=3, column=1, padx=(0, 10))
		self.ent_addnum2.grid(row=4, column=1, padx=(0, 10))
		self.ent_addemail.grid(row=5, column=1, padx=(0, 10))
		self.btn_gravar.grid(row=6, column=1, sticky='w', padx=60, pady=(15, 5))
		self.btn_cancelar.grid(row=6, column=1, sticky='e', padx=120, pady=(15, 5))

	def validate_data(self):
		self.name_ok = False
		self.surname_ok = False
		self.num1_ok = False
		self.email_ok = False
		if len(self.ent_addnome.get()) != 0:
			self.name_ok = True
		else:
			self.name_ok = False

		if len(self.ent_addapelido.get()) != 0:
			self.surname_ok = True
		else:
			self.surname_ok = False

		if len(self.ent_addnum1.get()) != 0:
			self.num1_ok = True
		else:
			self.num1_ok = False

		if '@' in self.ent_addemail.get() or self.ent_addemail.get() == '':
			self.email_ok = True
		else:
			self.email_ok = False
		if self.name_ok and self.surname_ok and self.num1_ok and self.email_ok:
			return True

	def add_contact(self):
		if self.validate_data():
			query = 'INSERT INTO contacts_list VALUES(NULL, ?, ?, ?, ?)'
			full_name = f'{self.ent_addnome.get()} {self.ent_addapelido.get()}'
			parameters = (full_name, self.ent_addnum1.get(), self.ent_addnum2.get(), self.ent_addemail.get())
			connector = ConectDB()
			connector.execute_query(query, parameters)
			self.message['text'] = f'{full_name} adicionado aos contactos'
			self.limpar_campos()
		else:
			self.message['text'] = f'Deve ter pelo menos 1 nome, apelido e número de telefone \n' \
								   f'e o email deve estar no formato correcto (alias@dominio.com)'

	def cancelar(self):
		self.limpar_campos()
		self.message['text'] = ''
		self.controller.show_frame(ViewClient)

	def limpar_campos(self):
		self.ent_addnome.delete(0, gui.END)
		self.ent_addapelido.delete(0, gui.END)
		self.ent_addnum1.delete(0, gui.END)
		self.ent_addnum2.delete(0, gui.END)
		self.ent_addemail.delete(0, gui.END)


class ConectDB:
	db_name = 'contacts.db'

	def execute_query(self, query, parameters=()):
		with sqlite3.connect(self.db_name) as db_conn:
			print('Database Connected!')
			cursor = db_conn.cursor()
			query_result = cursor.execute(query, parameters)
			db_conn.commit()
		return query_result


sistema = Contacts()
sistema.mainloop()

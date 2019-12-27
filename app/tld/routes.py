#coding:utf-8
from flask import *
from wtforms import *
from iota import *
from wtforms import ValidationError
from random import SystemRandom
from wtforms.validators import InputRequired,Email
from flask import current_app
from app.totangle.tld.tld_register import check_tld_exist, generate_tld_content, generate_new_seed, create_owner_auth,create_tld_content
from app.totangle.tld.tld_search import get_tld_content
from app.totangle.tld.tld_modify import tld_modify_run,check_tld_owner
from pprint import pprint
import json,linecache
import hashlib
import os
import re


main = Blueprint('main', __name__)

#tldname search
class tld_search_form(Form):
    tldname_search = StringField(validators=[validators.required()])
    tldsearch = SubmitField("Search")

@main.route('/', methods = ['POST', 'GET'])
def tldname_search():
    message = ''
    tldname = ''
    form = tld_search_form(request.form)
    if request.method == "POST":
        tldname_search = request.form['tldname_search']
        if form.validate():
            #if re.search('.*([0-9]+).*', tldname_search) == True:
            #    print("Registration failed!")
            #    flash("不能包含數字！")
            print("Someone is asking for register a TLD name !")

            if check_tld_exist(tldname_search) == False:
                session['tldname_search'] = tldname_search
                flash(tldname_search)
                # if tld name is avaliabe  goto '/to'

                print("This TLD name is avaliable.")

                return redirect(url_for('main.tld_available'))
            else:
                # if tld name is used go then back

                print("This TLD name is already exist !")

                message = "This TLD name is already exist !"
                return render_template('tld_search.html', runForm=form, a=message)
    return render_template('tld_search.html', runForm=form, a=message , d=tldname)

class tld_available_form(Form):
    tldavailable = SubmitField("Register")

@main.route('/to', methods = ['POST','GET'])
def tld_available():
    form = tld_available_form(request.form)
    if request.method == "POST":
        if form.validate():
            return redirect(url_for('main.tld_register'))
    return render_template('tld_available.html', runForm=form)

#tld register
class tld_register_form(Form):
    admin_name = StringField(validators=[validators.required("your name is wrong!")])
    admin_email = StringField(validators=[validators.required("your email is wrong!"),Email(message=None)],render_kw={"placeholder": "your email address..."})
    admin_phone = IntegerField(validators=[validators.required()])
    admin_submit = SubmitField("GO")
'''
def my_length_check(form, field):
        if len(field.data) > 50:
            raise ValidationError('Field must be less than 50 characters')

def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("WRONG！")
'''    
@main.route('/to/tld_register', methods = ['POST', 'GET'])
def tld_register():
    tld_name = session.get('tldname_search', None)
    check = ''
    form = tld_register_form(request.form)
    if request.method == "POST":
        admin_name = request.form['admin_name']
        admin_email = request.form['admin_email']
        admin_phone = request.form['admin_phone']
        #if form.validate() == False:
        if '@' not in admin_email:
            print("Registration failed!")
            wrong_email = "!"
            flash("請輸入正確的格式")
            return render_template('tld_register.html', runForm=form, wrong_email=wrong_email,b=tld_name)
        if form.validate():
            seed = generate_new_seed()
            key = create_owner_auth(seed)
            tld_content = create_tld_content(tld_name,admin_name,admin_email,admin_phone,key)
            tld_info = generate_tld_content(tld_name,tld_content,seed)
            info = "\nAddress:\n".join(tld_info)
            check = [info,tld_name,admin_name,admin_email,admin_phone]
            return render_template('tldregister_success.html', runForm=form, b=check)
    return render_template('tld_register.html', runForm=form, b=tld_name)

# if reg success then show 
class tldregister_sucs_form(Form):
    done = SubmitField("Done")

@main.route('/to/tld_register/sucs',methods = ['POST','GET'])
def tldregister_sucs():
    form = tldregister_sucs_form(request.form)
    if request.method == "POST":
        if form.validate():
            return redirect(url_for('main.tldname_search'))
    return render_template('tldregister_success.html', runForm=form)

class tld_explorer_form(Form):
    tldexp = StringField(validators=[validators.required()])
    tldexpbtn = SubmitField("Search")

# tld explore
@main.route('/tld_exp',methods = ['POST','GET'])
def tld_explorer():
    find = ''
    form = tld_explorer_form(request.form)
    if request.method == "POST":

        print("Someone is asking for explorer a TLD name !")

        tldexp = request.form['tldexp']
        keyword = ""
        if form.validate():
            if check_tld_exist(tldexp) == True:

                print("TLD name is exist.")

                session['tldexp'] = tldexp
                return redirect(url_for('main.tldexp_info'))
            else:
                
                print("Can't find the TLD name.")

                find = "NOT FOUND!"
                return render_template('tld_explorer.html', runForm = form, f = find)
    return render_template('tld_explorer.html', runForm=form)

@main.route('/tld_exp/info')
def tldexp_info():
    tld_exp_name = session.get('tldexp', None)
    tld_content_info = get_tld_content(tld_exp_name)
    tld_content = tld_content_info[0]
    tld_hashe = tld_content_info[1]
    message = tld_content['TLD_Content']['Domain_list']
    if message == {}:
        message = {'No Value':'No Value'}
    message_key = []
    message_value = []
    for key,value in message.items():
        message_key.append(key)
        message_value.append(value)
    key = message_key
    value = message_value
    return render_template('tldexp_info.html', key=key, value=value, tldexp=tld_exp_name, tld_hashe=tld_hashe)

#tld managlog
class tld_managlog_form(Form):
    manag_name = StringField(validators=[validators.required()])
    manag_seed = StringField(validators=[validators.required()])
    tld_log = SubmitField("GO")

#tld modify
class tld_modify_form(Form):
    name_modify = StringField(validators=[validators.required()])
    root_modify = StringField(validators=[validators.required()])
    add = SubmitField("+")
    done = SubmitField("Done")

#tld modify sucs
class tld_modify_sucs_form(Form):
    back = SubmitField("Done")

@main.route('/tld_mana',methods = ['POST','GET'])
def tld_manage():
    message = ''
    form = tld_managlog_form(request.form)
    if request.method == "POST":
        manag_name = request.form['manag_name']
        manag_seed = request.form['manag_seed']
        if form.validate():
            if check_tld_owner(manag_seed,manag_name) == True:
                session['manag_name'] = manag_name
                session['manag_seed'] = manag_seed
                return redirect(url_for('main.tld_modify'))
            else :
                message = "Seed is wrong."
                return render_template('tld_manage.html', runForm=form, message=message)
    return render_template('tld_manage.html', runForm=form)

@main.route('/tld_mana/modify',methods = ['POST','GET'])
def tld_modify():
    modify = ''
    modify_key = []
    modify_value = []
    manag_name = session.get('manag_name', None)
    manag_seed = session.get('manag_seed', None)
    tld_content_info = get_tld_content(manag_name)
    tld_content = tld_content_info[0]
    tld_hash = tld_content_info[1]
    domain_dict = tld_content['TLD_Content']['Domain_list']
    raw_count = len(domain_dict)
    for key,value in domain_dict.items():
        modify_key.append(key)
        modify_value.append(value)
    key = modify_key
    value = modify_value
    form = tld_modify_form(request.form)
    if request.method == "POST":
        name_modify = request.form['name_modify']
        root_modify = request.form['root_modify']
        if request.form["add"] == "add":
            name_modify = request.form['name_modify']
            root_modify = request.form['root_modify']
            modify = [name_modify,root_modify]
            keys = [name_modify]
            values = [root_modify]
            modify_dict = dict(zip(keys, values))
            global domain_new
            domain_new = {}
            f = open(manag_name,"a")
            f.write(str(modify_dict)+"\n")
            f.close()
            fp = open(manag_name,"r")
            temp_dict = {}
            for modify_new in fp.readlines():
                modify_new = modify_new.split("\n")[0].replace("'",'"')
                modify_new = json.loads(modify_new)
                temp_dict.update(modify_new)
                domain_new = dict(domain_dict, **temp_dict)
            modify_key1 =[]
            modify_value1=[]
            for key,value in domain_new.items():
                modify_key1.append(key)
                modify_value1.append(value)
            key_new = modify_key1
            value_new = modify_value1
            return render_template('tld_modify.html', runForm=form, key=key_new, value=value_new, show=modify, manag_name=manag_name, tld_hash=tld_hash)
        elif request.form["add"] == "done":
            if domain_new == {}:
                render_template('tld_modify.html', runForm=form, show=modify, manag_name=manag_name, manag_seed=manag_seed, key=key, value=value, tld_hash=tld_hash)
            else:
                new_address = tld_modify_run(manag_seed,manag_name,domain_new,tld_content)
                domain_new = {}
                os.remove(manag_name)
                return render_template('tldmodify_success.html', new_address=new_address, manag_name=manag_name)
    return render_template('tld_modify.html', runForm=form, show=modify, manag_name=manag_name, manag_seed=manag_seed, key=key, value=value, tld_hash=tld_hash)

@main.route('/tld_mana/modify/sucs',methods = ['POST','GET'])
def tld_modify_sucs():
    form = tld_modify_sucs_form(request.form)
    if request.method == "POST":
        if form.validate():
            return redirect(url_for('main.tld_manage'))
    return render_template('tldmodify_success.html', runForm=form)
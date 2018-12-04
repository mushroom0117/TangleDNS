from flask import *
from wtforms import *
from iota import *
from random import SystemRandom
from pprint import pprint
import json, time, ast, os
from wtforms.validators import Email
from app.totangle.domain.domain_register import domain_register_to_tangle,check_domain_exist,create_owner_auth,create_domain_content,generate_new_seed
from app.totangle.domain.domain_search import find_domain
from app.totangle.domain.domain_update import find_domain, domain_update_to_tangle, modify_domain_content,check_domain_owner

domain = Blueprint('domain', __name__)

class domain_explorer_form(Form):
    domainexp = StringField(validators=[validators.required()])
    domainexpbtn = SubmitField("Search")

def removeLine(filename, lineno):
    fro = open(filename, "r",encoding='UTF-8')
    current_line = 0
    while current_line < lineno:
        fro.readline()
        current_line += 1

    seekpoint = fro.tell()
    frw = open(filename, "r+")
    frw.seek(seekpoint, 0)
    fro.readline() 
    chars = fro.readline()
    while chars:
        frw.writelines(chars)
        chars = fro.readline()
    fro.close()
    frw.truncate()
    frw.close()

@domain.route('/domain_exp',methods = ['POST','GET'])
def domain_explorer():
    form = domain_explorer_form(request.form)
    if request.method == "POST":
        keyword = ""
        domainexp = request.form['domainexp']
        if form.validate():
            if check_domain_exist(domainexp) == "tld_not_found":
                find = "TLD Name IS NOT FOUND!"
                return render_template('domain_explorer.html', runForm=form, f=find)

            elif check_domain_exist(domainexp) == "domain_available":
                find = "Domain Name IS NOT FOUND!"
                return render_template('domain_explorer.html', runForm=form, f=find)

            elif check_domain_exist(domainexp) == "domain_exist":
                session['domainexp'] = domainexp
                return redirect(url_for('domain.domainexp_info'))

    return render_template('domain_explorer.html', runForm=form)

@domain.route('/domain_exp/info',methods = ['POST','GET'])
def domainexp_info():
    domain_exp_name = session.get('domainexp', None)
    domain_info = find_domain(domain_exp_name)
    domain_content = json.loads(domain_info[0])
    message = domain_content['AnswerSection']
    if message == [{}]:
        message = [{'Name': 'No Value', 'TTL': 'No Value', 'Type': 'No Value', 'Address': 'No Value'}]
    print(message)
    count = (len(message))
    return render_template('domainexp_info.html',count=count, message=message, tldexp=domain_exp_name, doamin_root=domain_info[1])

###############################

class domain_search_form(Form):
    domainname_search = StringField(validators=[validators.required()])
    domainsearch = SubmitField("Search")

@domain.route('/domain', methods = ['POST', 'GET'])
def domainname_search():
    message = ''
    domainname = ''
    form = domain_search_form(request.form)
    if request.method == "POST":
        domainname_search = request.form['domainname_search']
        if form.validate():
            if check_domain_exist(domainname_search) == "domain_available":
                session['domainname_search'] = domainname_search
                flash("Domain Name is available.")
                return redirect(url_for('domain.domain_available'))

            elif check_domain_exist(domainname_search) == "domain_exist":
                message = "Domain Name is already exist."
                if domainname_search.split('.')[-3]:
                    message = "Third level Domain is not available for now, please register with the second level domain owner."
                return render_template('domain_search.html', runForm=form, a=message)

            elif check_domain_exist(domainname_search) == "tld_not_found":
                message = "TLD Name not found, please register TLD Name first."
                return render_template('domain_search.html', runForm=form, a=message)

    return render_template('domain_search.html', runForm=form, a=message , d=domainname)

class domain_available_form(Form):
    domainavailable = SubmitField("Register")

@domain.route('/domain/to', methods = ['POST','GET'])
def domain_available():
    form = domain_available_form(request.form)
    if request.method == "POST":
        if form.validate():
            return redirect(url_for('domain.domain_register'))
    return render_template('domain_available.html', runForm=form)
    
class domain_register_form(Form):
    admin_name = StringField(validators=[validators.required()])
    admin_email = StringField(validators=[validators.Email()])
    admin_phone = IntegerField(validators=[validators.required()])
    #tld_seed = StringField(validators=[validators.required()])
    admin_submit = SubmitField("GO")

@domain.route('/domain/to/register', methods = ['POST', 'GET'])
def domain_register():
    check = ''
    url = session.get('domainname_search', None)
    form = domain_register_form(request.form)
    if request.method == "POST":
        admin_name = request.form['admin_name']
        admin_email = request.form['admin_email']
        admin_phone = request.form['admin_phone']
        #tld_seed = request.form['tld_seed']
        if '@' not in admin_email:
            print("Registration failed!")
            wrong = "!"
            flash("請輸入正確的格式")
            return render_template('domain_register.html', runForm=form, b=url,wrong=wrong)
        if form.validate():
            seed = generate_new_seed()
            key = create_owner_auth(seed)
            '''
            with open('./app/totangle/demo_json/domain/domain_demo.json' , 'r') as reader:
                tld_demo_dict = json.loads(reader.read())
                domain_content = json.dumps(tld_demo_dict)
            '''
            domain_content = create_domain_content(admin_email, admin_phone, key)
            domain_info = domain_register_to_tangle(url,domain_content,seed)#,tld_seed)
            #info = "\nMAM Root:\n"+"\nTLD Address:\n".join(domain_info)
            mam_seed = domain_info[0]
            mam_root = domain_info[1]
            new_tld_address = domain_info[2]
            check = [mam_seed,mam_root,new_tld_address,url,admin_name,admin_email,admin_phone]
            return render_template('domainregister_success.html', runForm=form, b=check)
    return render_template('domain_register.html', runForm=form, b=url)

class domainregister_sucs_form(Form):
    done = SubmitField("Done")

@domain.route('/domain/to/register/sucs',methods = ['POST','GET'])
def domainregister_sucs():
    form = domainregister_sucs_form(request.form)
    if request.method == "POST":
        if form.validate():
            return redirect(url_for('domain.domainname_search'))
    return render_template('domainregister_success.html', runForm=form)

#domain managlog
class domain_managlog_form(Form):
    manag_name = StringField(validators=[validators.required()])
    manag_seed = StringField(validators=[validators.required()])
    domain_log = SubmitField("GO")

#domain form
class domain_modify_form(Form):
    name = StringField(validators=[validators.required()])
    type = SelectField(validators=[validators.required()] , choices=[('A', 'A'),('AAAA','AAAA'),('CAA','CAA'),('CNAME','CNAME'),('DS','DS'),('MX','MX'),('NS','NS'),('PTR','PTR'),('SPF','SPF'),('SRV','SRV'),('SSHFP','SSHFP'),('TLSA','TLSA'),('TXT','TXT')])
    ttl = IntegerField(validators=[validators.required()])
    address = StringField(validators=[validators.required()])
    add = SubmitField("Add")


class domain_modify_sucs_form(Form):
    back = SubmitField("Done")

@domain.route('/domain_mana',methods = ['POST','GET'])
def domain_manage():
    message = ''
    form = domain_managlog_form(request.form)
    if request.method == "POST":
        manag_name = request.form['manag_name']
        manag_seed = request.form['manag_seed']
        if form.validate():
            if check_domain_owner(manag_seed,manag_name) == True:
                session['manag_name'] = manag_name
                session['manag_seed'] = manag_seed
                return redirect(url_for('domain.domain_modify'))
            else :
                message = "Seed is wrong."
                return render_template('domain_manage.html', runForm=form, message=message)
    return render_template('domain_manage.html', runForm=form)

@domain.route('/domain_mana/modify', methods = ['POST', 'GET'])
def domain_modify():
    show = ''
    modify = ''
    manag_name = session.get('manag_name', None)
    manag_seed = session.get('manag_seed', None)
    domain_info = find_domain(manag_name)
    domain_content = json.loads(domain_info[0])
    session['domain_content'] = domain_content
    answer_section = domain_content['AnswerSection']
    if answer_section[0]=={}:
        del answer_section[0]
    else:
        if os.path.exists(manag_name) == False:
            n = 0
            while(n <= len(answer_section)):
                f_tangle = open(manag_name,"a")
                f_tangle.write(str(answer_section[n])+"\n")
                f_tangle.close()
                n+=1
                if n ==len(answer_section):
                    break
    
    mam_start_count = int(domain_content['Domain_Info']['Index']) + 1
    session['mam_start_count'] = mam_start_count
    count = (len(answer_section))
    form = domain_modify_form(request.form)
    if request.method == "POST":
        name = request.form['name']
        type = request.form['type']
        ttl = request.form['ttl']
        address = request.form['address']
        if request.form["action"] == "add":
            name = request.form['name']
            type = request.form['type']
            ttl = request.form['ttl']
            address = request.form['address']
            add_info = "{\n \"Name\":"+"\""+name+"\""+",\n \"TTL\":"+"\""+str(ttl)+"\""+",\n \"Type\":"+"\""+type+"\""+",\n \"Address\":"+"\""+address+"\"\n}"
            add_info_dict = json.loads(add_info)
            f = open(manag_name,"a")
            f.write(str(add_info_dict)+"\n")
            f.close()
            answer_section = []
            fp = open(manag_name,"r")
            for read_file in fp.readlines():
                read_file = read_file.split("\n")[0].replace("'",'"')
                answer_section.append(ast.literal_eval(read_file))
                session['answer_section'] = answer_section
            count = len(answer_section)
            i = 1
            while(True):
                message = Markup("<button type="+"\""+"submit"+"\""+" value="+"\""+str(i)+"\""+" name="+"\""+"action"+"\""+" class="+"\""+"btn btn-outline-danger btn-sm btn1 mx-1 butsub"+"\""+">Remove</button><br>")
                flash(message)
                if i == count :
                    break
                i+=1
            #for n in range(count):
            return render_template('domain_modify.html', runForm=form, c=show ,manag_name=manag_name, count=count, answer_section=answer_section)
        if (request.form["action"]):
            n = 1
            while(True):
                if request.form["action"] == str(n):
                    answer_section = session.get('answer_section', None)
                    removeLine(manag_name,n-1)
                    del answer_section[n-1]
                    session['answer_section'] = answer_section
                    m = 1
                    button_html_table = ''
                    count = len(answer_section)
                    while(m <= count):
                        button_html = Markup("<button type="+"\""+"submit"+"\""+" value="+"\""+str(m)+"\""+" name="+"\""+"action"+"\""+" class="+"\""+"btn btn-outline-danger btn-sm btn1 mx-1 butsub"+"\""+">Remove</button><br>")
                        button_html_table = button_html_table + button_html
                        m+=1
                    message = Markup(button_html_table)
                    flash(message)
                    return render_template('domain_modify.html', runForm=form, c=show ,manag_name=manag_name,n=n, count=count, answer_section=answer_section)
                    if n == len(answer_section):
                        break
                n+=1
    return render_template('domain_modify.html', runForm=form, c=show ,manag_name=manag_name,answer_section=answer_section, count=count)

@domain.route('/domain_mana/modify/sucs',methods = ['POST','GET'])
def domain_modify_sucs():
    manag_name = session.get('manag_name', None)
    manag_seed = session.get('manag_seed', None)
    mam_start_count = session.get('mam_start_count', None)
    domain_content = session.get('domain_content', None)
    fopen = open(manag_name,"r")
    answer_section = []
    for read_file in fopen.readlines():
        read_file = read_file.split("\n")[0].replace("'",'"')
        answer_section.append(ast.literal_eval(read_file))

    domain_json = modify_domain_content(domain_content, mam_start_count, answer_section)
    new_domain_address = domain_update_to_tangle(manag_name,domain_json,mam_start_count,manag_seed)
    os.remove(manag_name)
    form = domain_modify_sucs_form(request.form)
    return render_template('domainmodify_success.html', runForm=form, manag_name=manag_name, new_root=new_domain_address)
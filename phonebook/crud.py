# CRUD for upload, add, update and delete contacts into datstore data model
from phonebook import get_model
from flask import Blueprint, current_app, redirect, render_template, request, \
    session, url_for
from werkzeug.exceptions import BadRequest
import re
crud = Blueprint('crud', __name__)
CACHED_FILE = None
@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    contacts, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        contacts=contacts,
        next_page_token=next_page_token)

@crud.route('/upload', methods=['GET', 'POST'])
def upload():
    '''
    Upload a csv file contains name and Email
    :return: contacts_list
    '''
    global CACHED_FILE
    # check extension of uploaded file
    if request.method == 'POST':
        _is_unique = True
        contacts_list = []
        csvdata = request.files.get('csvFile').read().decode().split("\r")
        _file = request.files
        if eval(request.form.to_dict(flat=True).get('force')) and CACHED_FILE:
            for line in CACHED_FILE:
                _items = line.split(',')
                if _items and _is_email_valid(_items[1]):
                    contacts_list.append({
                        'name': line.split(',')[0],
                        'email': line.split(',')[1]
                    })
            get_model().bulk_create(contacts_list)
            return redirect(url_for('.list'))
        if csvdata:
            CACHED_FILE = csvdata
        else:
            return render_template("upload.html", action="Empty or Corrupted File")
        try:
            _check_extension(_file.get('csvFile').filename, current_app.config['ALLOWED_EXTENSIONS'])
        except BadRequest:
            return render_template("upload.html", action="not allowed extension")
        for line in csvdata:
            _items = line.split(',')
            if _items and _is_email_valid(_items[1]):
                contacts_list.append({
                    'name': line.split(',')[0],
                    'email': line.split(',')[1]
                })

        for contact in contacts_list:
            if not check_email_uniqueness(contact):
                _is_unique = False
        if _is_unique:
            get_model().bulk_create(contacts_list)
        else:
            return render_template("upload.html", action="Confirming required")
        return redirect(url_for('.list'))

    return render_template("upload.html", action="Upload", contact={})

@crud.route('/add', methods=['GET', 'POST'])
def add(force=None):
    '''
    add just one contact each time inside a profile
    :return: contact data
    '''
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        if not _is_email_valid(data.get('email')):
            return render_template("form.html", action="Wrong E-mail", contact=data)
        if check_email_uniqueness(data):
                contact = get_model().create(data)
                return redirect(url_for('.list'))
        elif eval(data.get('force')):
            # 'Email Exist and user confirm to update
            contact = update_existing_contact(data)
            return redirect(url_for('.list'))
        else:
            return render_template("form.html", action="Confirming", contact=data)
    return render_template("form.html", action="Add", contact={})

@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    contact = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        contact = get_model().update(data, id)

        return redirect(url_for('.list', id=contact['id']))

    return render_template("form.html", action="Edit", contact=contact)

@crud.route('/<id>', methods=['GET'])
def view(id):
    contact = get_model().read(id)

    return render_template("form.html", action="View", contact=contact)


@crud.route('/<id>/delete', methods=['POST'])
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))

@crud.route('/search', methods=['GET'])
def search():
    name = request.args.get('name').lower()
    contacts = get_list()
    for contact in contacts:
        if name and name in contact.get('name', None).lower():
            id = contact.get('id')
            return render_template("form.html", action="View", contact=contact)
    return redirect(url_for('.list'))

def check_email_uniqueness(data):
    _email = data.get('email')
    contacts = get_list()
    print (contacts)
    for contact in contacts:
        if _email and _email in contact.get('email', None):
            return False
    return True

def get_list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    contacts, next_page_token = get_model().list()
    return contacts

def update_existing_contact(data):
    _email = data.get('email')
    contacts = get_list()
    for contact in contacts:
        if _email and _email in contact.get('email', None):
            id = contact.get('id')
            return get_model().update(data, id)

def _check_extension(filename, allowed_extensions):
    if ('.' not in filename or
            filename.split('.').pop().lower() not in allowed_extensions):
        raise BadRequest(
            "{0} has an invalid name or extension".format(filename))

def _is_email_valid(email):
    return re.search(r'[\w.-]+@[\w.-]+.\w+', email) is not None

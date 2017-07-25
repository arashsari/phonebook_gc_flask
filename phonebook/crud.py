# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from phonebook import get_model, oauth2, storage
from flask import Blueprint, current_app, redirect, render_template, request, \
    session, url_for, current_app

crud = Blueprint('crud', __name__)

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
    if request.method == 'POST':
        _is_unique = True
        contacts_list = []
        csvdata = request.files.get('csvFile').read().decode().split("\r")
        for line in csvdata:
            _name, _email = line.split(',')
            contacts_list.append({
                'name': _name,
                'email': _email
            })

        for contact in contacts_list:
            if not check_email_uniqueness(contact):
                _is_unique = False
        if _is_unique:
            contact = get_model().create(contacts_list)
        else:
            return render_template("upload.html", action="Confirmation")
        return redirect(url_for('.list'))

    return render_template("upload.html", action="Add", contact={})

@crud.route('/add', methods=['GET', 'POST'])
def add(force=None):
    '''
    add just one contact each time inside a profile
    :return: contact data
    '''
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        if check_email_uniqueness(data):
                contact = get_model().create(data)
                return redirect(url_for('.list'))
        elif eval(data.get('force')):
            # 'Email Exist and user confirm to update
            contact = update_existing_contact(data)
            return redirect(url_for('.list'))
        else:
            return render_template("form.html", action="Confirmation", contact=data)
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
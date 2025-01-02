from flask import Flask, render_template, request, redirect, url_for, flash
import random
import csv
import io
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

# Dictionary to store names and their assignment status
names_pool = {}  # Format: {name: {'is_assigned_to': None, 'has_picked': False}}

@app.route('/')
def index():
    # Only show names that haven't picked yet
    available_names = [name for name, status in names_pool.items() 
                      if not status['has_picked']]
    return render_template('index.html', names=available_names)

@app.route('/admin')
def admin():
    return render_template('admin.html', names=names_pool)


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin'))

    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.reader(stream)
            
            names_pool.clear()
            for row in csv_reader:
                if row:  # Skip empty rows
                    name = row[0].strip()
                    if name:  # Skip empty names
                        names_pool[name] = {
                            'is_assigned_to': None,  # Who this person is Secret Santa for
                            'has_picked': False      # Whether they've picked their person
                        }
            
            flash('Names uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
    else:
        flash('Please upload a CSV file', 'error')

    return redirect(url_for('admin'))

@app.route('/pick_friend', methods=['POST'])
def pick_friend():
    current_person = request.form.get('name', '')
    
    # Check if person has already picked
    if current_person not in names_pool or names_pool[current_person]['has_picked']:
        flash('You have already picked your Secret Santa friend!', 'error')
        return redirect(url_for('index'))
    
    # Get list of available names (not assigned and not the current person)
    available_names = [name for name, status in names_pool.items() 
                      if status['is_assigned_to'] is None and name != current_person]
    
    if not available_names:
        flash('No more friends available to pick!', 'error')
        return redirect(url_for('index'))
    
    chosen_friend = random.choice(available_names)
    names_pool[current_person]['has_picked'] = True
    names_pool[chosen_friend]['is_assigned_to'] = current_person
    
    return render_template('result_popup.html', 
                         current_person=current_person,
                         chosen_friend=chosen_friend)

if __name__ == '__main__':
    app.run(debug=True)

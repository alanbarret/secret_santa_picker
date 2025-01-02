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
<<<<<<< Updated upstream
    # Only show names that haven't picked yet
    available_names = [name for name, status in names_pool.items() 
                      if not status['has_picked']]
    return render_template('index.html', names=available_names)
=======
    if not numbers_pool:
        return render_template('index.html', waiting_for_admin=True)
    
    # Check if user has already picked
    if session.get('has_picked'):
        return render_template('index.html', 
                             has_picked=True, 
                             picked_number=session.get('picked_number'))
    
    # Only show numbers that haven't picked yet
    available_numbers = [num for num, status in numbers_pool.items() 
                        if not status['has_picked']]
    return render_template('index.html', 
                         waiting_for_admin=False, 
                         has_picked=False,
                         numbers=sorted(available_numbers))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
@app.route('/pick_friend', methods=['POST'])
def pick_friend():
    current_person = request.form.get('name', '')
    
    # Check if person has already picked
    if current_person not in names_pool or names_pool[current_person]['has_picked']:
        flash('You have already picked your Secret Santa friend!', 'error')
=======
@app.route('/clear_numbers', methods=['POST'])
def clear_numbers():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first', 'error')
        return redirect(url_for('login'))
        
    try:
        numbers_pool.clear()
        save_numbers_pool(numbers_pool)
        # Clear all user sessions
        session.clear()
        # Restore admin session
        session['admin_logged_in'] = True
        flash('All numbers have been cleared successfully!', 'success')
    except Exception as e:
        flash('An error occurred while clearing numbers', 'error')
    
    return redirect(url_for('admin'))
@app.route('/pick_number', methods=['POST'])
def pick_number():
    try:
        # Check if user has already picked
        if session.get('has_picked'):
            flash('You have already picked your number!', 'error')
            return redirect(url_for('index'))
            
        # Load current state but don't overwrite the global pool
        current_pool = load_numbers_pool()
        
        if not current_pool:
            flash('Please wait for the admin to set up the numbers.', 'error')
            return redirect(url_for('index'))
        
        available_picker_numbers = [num for num, status in current_pool.items() 
                                 if not status['has_picked']]
        
        if not available_picker_numbers:
            flash('All numbers have been assigned!', 'error')
            return redirect(url_for('index'))
        
        current_number = random.choice(available_picker_numbers)
        
        available_numbers = [num for num, status in current_pool.items() 
                           if status['is_assigned_to'] is None and num != current_number]
        
        if not available_numbers:
            flash('No more numbers available to pick!', 'error')
            return redirect(url_for('index'))
        
        chosen_number = random.choice(available_numbers)
        current_pool[current_number]['has_picked'] = True
        current_pool[chosen_number]['is_assigned_to'] = current_number
        
        # Store in session that this user has picked
        session['has_picked'] = True
        session['picked_number'] = current_number
        
        save_numbers_pool(current_pool)
        
        return render_template('result_popup.html', 
                             current_number=current_number,
                             chosen_number=chosen_number)
    except Exception as e:
        flash('An error occurred while picking numbers', 'error')
>>>>>>> Stashed changes
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

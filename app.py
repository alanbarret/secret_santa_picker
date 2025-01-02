from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

# Dictionary to store numbers and their assignment status
numbers_pool = {}  # Format: {number: {'is_assigned_to': None, 'has_picked': False}}

# Admin credentials (in a real app, use proper authentication and hashing)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secretsanta2025"

@app.route('/')
def index():
    # Only show numbers that haven't picked yet
    available_numbers = [num for num, status in numbers_pool.items() 
                        if not status['has_picked']]
    return render_template('index.html', numbers=sorted(available_numbers))

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

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html', numbers=numbers_pool)

@app.route('/set_range', methods=['POST'])
def set_range():
    try:
        max_number = int(request.form.get('max_number', 0))
        if max_number < 2:
            flash('Please enter a number greater than 1', 'error')
            return redirect(url_for('admin'))
        
        numbers_pool.clear()
        for num in range(1, max_number + 1):
            numbers_pool[num] = {
                'is_assigned_to': None,
                'has_picked': False
            }
        
        flash('Number range set successfully!', 'success')
    except ValueError:
        flash('Please enter a valid number', 'error')
    
    return redirect(url_for('admin'))

@app.route('/pick_number', methods=['POST'])
def pick_number():
    try:
        # Get list of numbers that haven't picked yet
        available_picker_numbers = [num for num, status in numbers_pool.items() 
                                 if not status['has_picked']]
        
        if not available_picker_numbers:
            flash('All numbers have been assigned!', 'error')
            return redirect(url_for('index'))
        
        # Randomly select a number for the current user
        current_number = random.choice(available_picker_numbers)
        
        # Get list of available numbers to be picked (not assigned and not the current number)
        available_numbers = [num for num, status in numbers_pool.items() 
                           if status['is_assigned_to'] is None and num != current_number]
        
        if not available_numbers:
            flash('No more numbers available to pick!', 'error')
            return redirect(url_for('index'))
        
        chosen_number = random.choice(available_numbers)
        numbers_pool[current_number]['has_picked'] = True
        numbers_pool[chosen_number]['is_assigned_to'] = current_number
        
        return render_template('result_popup.html', 
                             current_number=current_number,
                             chosen_number=chosen_number)
    except Exception as e:
        flash('An error occurred while picking numbers', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
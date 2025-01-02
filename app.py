from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Supabase client
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials")
        
    supabase = create_client(
        supabase_url,
        supabase_key
    )
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    raise

def load_numbers_pool():
    try:
        response = supabase.table('numbers_pool').select("*").execute()
        if response.data:
            # Convert the array of records to our desired format
            pool = {}
            for record in response.data:
                pool[record['number']] = {
                    'is_assigned_to': record['is_assigned_to'],
                    'has_picked': record['has_picked']
                }
            return pool
        return {}
    except Exception as e:
        print(f"Error loading numbers pool: {e}")
        import traceback
        print(traceback.format_exc())
        return {}

def save_numbers_pool(pool):
    try:
        # First, clear existing records
        supabase.table('numbers_pool').delete().neq('number', '0').execute()
        
        # Insert new records
        records = []
        for number, status in pool.items():
            records.append({
                'number': number,
                'is_assigned_to': status['is_assigned_to'],
                'has_picked': status['has_picked']
            })
        
        if records:
            supabase.table('numbers_pool').insert(records).execute()
            
    except Exception as e:
        print(f"Error saving numbers pool: {e}")
        import traceback
        print(traceback.format_exc())

# Dictionary to store numbers and their assignment status
numbers_pool = load_numbers_pool()  # Format: {number: {'is_assigned_to': None, 'has_picked': False}}

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME','admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD','secretsanta2025')

@app.route('/')
def index():
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

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    # Reload numbers pool from JSON file
    current_pool = load_numbers_pool()
    return render_template('admin.html', numbers=current_pool)

@app.route('/set_range', methods=['POST'])
def set_range():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first', 'error')
        return redirect(url_for('login'))
        
    try:
        max_number = int(request.form.get('max_number', 0))
        if max_number < 2:
            flash('Please enter a number greater than 1', 'error')
            return redirect(url_for('admin'))
        
        numbers_pool.clear()
        for num in range(1, max_number + 1):
            numbers_pool[str(num)] = {
                'is_assigned_to': None,
                'has_picked': False
            }
        
        save_numbers_pool(numbers_pool)
        flash('Number range set successfully!', 'success')
    except ValueError:
        flash('Please enter a valid number', 'error')
    
    return redirect(url_for('admin'))


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
        return redirect(url_for('index'))
    
    # Get list of available names (not assigned and not the current person)
    available_names = [name for name, status in names_pool.items() 
                      if status['is_assigned_to'] is None and name != current_person]
    
    if not available_names:
        flash('No more friends available to pick!', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
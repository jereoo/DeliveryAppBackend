# start-django.ps1
# Change directory to project root
Set-Location "C:\Users\360WEB\DeliveryAppBackend"

# Allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate the virtual environment
& ".\venv\Scripts\Activate.ps1"

# Start the Django development server
python manage.py runserver


Read-Host -Prompt "Press Enter to exit"

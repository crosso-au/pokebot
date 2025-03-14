# install_python.ps1
# Check if Python is installed (optional)
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "Python is already installed."
    exit
}

# Download the Python installer
$pythonUrl = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe"
$output = "python-installer.exe"
Write-Host "Downloading Python from $pythonUrl..."
Invoke-WebRequest -Uri $pythonUrl -OutFile $output

# Run the installer silently with options to install for all users and add Python to PATH
Write-Host "Installing Python..."
Start-Process -FilePath $output -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

# Clean up
Remove-Item $output
Write-Host "Python installation complete."

# SolarCrypto Miner Automation

## What is This?
This project automates cryptocurrency mining based on surplus solar power from your Tesla Powerwall. By monitoring the energy export levels, the script automatically starts or stops mining to maximize profits using excess solar energy.

It integrates with the Tesla Powerwall API and the T-Rex miner, providing control over when mining starts—either through automated thresholds or manual overwrites.

---

## How It Works
1. **Monitors Solar Export**: Connects to your Tesla Powerwall and checks the amount of power being exported to the grid.
2. **Starts/Stops Mining**: If you're exporting more than a set threshold (e.g., 1000W), the miner starts. If export drops below a lower threshold (e.g., 500W), the miner stops.
3. **Manual Override**: The `.env` file allows manual control to force the miner on or off regardless of solar export.

---

## Prerequisites

### 1. **Install Python and Dependencies**
Ensure you have Python 3.9+ installed. It is recommended to use a virtual environment.

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
python3 -m venv solarCrypto
source solarCrypto/bin/activate
pip install -r requirements.txt
```

### 2. **Install T-Rex Miner**
Download and install the [T-Rex Miner](https://github.com/trexminer/T-Rex/releases):

```bash
cd ~/SolarCrypto
wget https://github.com/trexminer/T-Rex/releases/download/0.26.8/t-rex-0.26.8-linux.tar.gz
tar -xvf t-rex-0.26.8-linux.tar.gz
```

Ensure the miner is executable:

```bash
chmod +x t-rex-0.26.8-linux/t-rex
```

### 3. **Get a Crypto Wallet**
If you don't already have one, set up a wallet. [Atomic Wallet](https://atomicwallet.io/) is a good option that supports multiple cryptocurrencies.

Once created, copy your wallet address—you'll need it in the `.env` configuration.

---

## Setting Up the `.env` File
Create a `.env` file in the project directory with the following structure:

```ini
# Powerwall Configuration
POWERWALL_IP=192.168.1.1  # Replace with your Powerwall's IP
POWERWALL_EMAIL=your_email@example.com  # Tesla account email
POWERWALL_PASSWORD=your_powerwall_password  # Powerwall password

# Overwrite Settings
Overwrite_Miner=false  # Set to 'true' to manually control mining
Overwrite_Miner_State=Off  # Set to 'On' or 'Off' for manual control

# Export Thresholds (in Watts)
EXPORT_START_THRESHOLD=1000  # Start mining when exporting more than 1000W
EXPORT_STOP_THRESHOLD=500   # Stop mining when export drops below 500W

# Miner Configuration
Miner_Location=/path/to/t-rex  # Path to your T-Rex miner binary
Coin_Type=etchash  # Algorithm to mine (e.g., 'etchash' for Ethereum Classic)
Mining_Pool=stratum+tcp://asia-etc.2miners.com:1010  # Mining pool URL
Crypto_Wallet=YOUR_CRYPTO_WALLET_ADDRESS.HomeServer1  # Replace with your wallet

# Poll Interval (in seconds)
POLL_INTERVAL=60  # Frequency to check Powerwall data
```

### **Find Your Powerwall Password**
To get your Tesla Powerwall password, follow the instructions on Tesla's official support page:

[Connecting Tesla Powerwall to a Network](https://www.tesla.com/en_au/support/energy/powerwall/own/connecting-network)

---

## Running the Script
Run the script manually to ensure everything is configured correctly:

```bash
python3 solarCrypto.py
```

Logs will be saved to `solar_mining.log` in the project directory.

---

## Setting Up as a Service on Ubuntu
To ensure the miner runs on startup and in the background, set it up as a **systemd** service.

### 1. **Create the Service File**

```bash
sudo nano /etc/systemd/system/solarCrypto.service
```

Paste the following configuration:

```ini
[Unit]
Description=Solar Crypto Mining Automation
After=network.target

[Service]
WorkingDirectory=/home/YOUR_USERNAME/SolarCrypto
ExecStart=/home/YOUR_USERNAME/SolarCrypto/solarCrypto/bin/python /home/YOUR_USERNAME/SolarCrypto/solarCrypto.py
Environment="PYTHONUNBUFFERED=1"
Restart=always
RestartSec=10
User=YOUR_USERNAME
Group=YOUR_USERNAME
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. **Enable and Start the Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable solarCrypto.service
sudo systemctl start solarCrypto.service
```

### 3. **Check the Service Status and Logs**

To check if the service is running:

```bash
sudo systemctl status solarCrypto.service
```

For live logs:

```bash
journalctl -u solarCrypto.service -f
```

---

## Troubleshooting
- **Not connecting to Powerwall?** Make sure your IP address and password are correct.
- **Mining not starting?** Check the `.env` file to ensure thresholds or overwrite settings are configured properly.
- **Service not running?** Check logs with `journalctl -u solarCrypto.service -f` to debug.

---

## Contributing
Feel free to fork this repository and contribute improvements or bug fixes via pull requests!

---

## Disclaimer
Mining cryptocurrency may reduce the lifespan of your hardware and may have legal or tax implications in your region. This script is provided for educational purposes. Use at your own risk.


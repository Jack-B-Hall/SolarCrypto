#!/usr/bin/env python3

import os
import time
import asyncio
import logging
import subprocess
from dotenv import load_dotenv
from tesla_powerwall import Powerwall, ApiError

# Configure logging
logging.basicConfig(
    filename="solar_mining.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log_info(message: str):
    """Log to both console and file."""
    print(message)
    logging.info(message)

async def main():
    # 1) Load .env once at startup
    load_dotenv(override=True)

    # 2) Read all relevant config ONCE
    powerwall_ip = os.getenv("POWERWALL_IP", "")
    powerwall_email = os.getenv("POWERWALL_EMAIL", "")
    powerwall_password = os.getenv("POWERWALL_PASSWORD", "")

    overwrite_miner = os.getenv("Overwrite_Miner", "false").lower() == "true"
    overwrite_miner_state = os.getenv("Overwrite_Miner_State", "off").lower()

    try:
        export_start = float(os.getenv("EXPORT_START_THRESHOLD", "1500"))
        export_stop = float(os.getenv("EXPORT_STOP_THRESHOLD", "500"))
    except ValueError:
        export_start = 1500.0
        export_stop = 500.0

    try:
        poll_interval = int(os.getenv("POLL_INTERVAL", "60"))
    except ValueError:
        poll_interval = 60

    miner_location = os.getenv("Miner_Location", "")
    coin_type = os.getenv("Coin_Type", "etchash")
    mining_pool = os.getenv("Mining_Pool", "stratum+tcp://asia-etc.2miners.com:1010")
    crypto_wallet = os.getenv("Crypto_Wallet", "0xYourWalletAddress.RigName")

    # Build the miner command
    miner_cmd = [
        miner_location,
        "-a", coin_type,
        "-o", mining_pool,
        "-u", crypto_wallet,
        "-p", "x",
        "--devices", "0,1"
    ]

    log_info("=== Starting solarCrypto ===")
    log_info(f"Powerwall IP: {powerwall_ip}")
    log_info(f"Export Start Threshold: {export_start} W, Stop Threshold: {export_stop} W")
    log_info(f"Overwrite Miner: {overwrite_miner}, Overwrite State: {overwrite_miner_state}")
    log_info(f"Miner Cmd: {' '.join(miner_cmd)}")
    log_info(f"Polling Interval: {poll_interval} sec")

    # 3) Connect to Powerwall
    powerwall = Powerwall(powerwall_ip, verify_ssl=False)

    try:
        await powerwall.login(powerwall_password, powerwall_email)
        if not powerwall.is_authenticated():
            log_info("Login failed: Not authenticated.")
            return
        log_info("Successfully logged into the Powerwall.")
    except ApiError as err:
        log_info(f"Failed to authenticate to Powerwall: {err}")
        return

    # 4) Prepare for miner tracking
    miner_process = None
    miner_start_time = None
    total_miner_seconds = 0.0

    # We'll keep old_overwrite_miner to detect changes
    old_overwrite_miner = overwrite_miner
    old_overwrite_state = overwrite_miner_state

    while True:
        load_dotenv(override=True)

        # 5) Re-check ONLY Overwrite variables each loop
        new_overwrite_miner = os.getenv("Overwrite_Miner", "false").lower() == "true"
        new_overwrite_state = os.getenv("Overwrite_Miner_State", "off").lower()

        if (new_overwrite_miner != old_overwrite_miner) or (new_overwrite_state != old_overwrite_state):
            log_info(f"Overwrite changed -> Miner={new_overwrite_miner}, State={new_overwrite_state}")
            old_overwrite_miner = new_overwrite_miner
            old_overwrite_state = new_overwrite_state

        try:
            if new_overwrite_miner:
                # 6) Overwrite logic: we ignore thresholds, just see if we want miner "on" or "off"
                if new_overwrite_state == "on":
                    # Force miner on
                    if not miner_process or miner_process.poll() is not None:
                        log_info("Overwrite: Forcing miner ON.")
                        miner_process = subprocess.Popen(miner_cmd)
                        miner_start_time = time.time()
                else:
                    # Force miner off
                    if miner_process and miner_process.poll() is None:
                        run_time = time.time() - miner_start_time if miner_start_time else 0
                        total_miner_seconds += run_time
                        log_info(f"Overwrite: Forcing miner OFF. Session={run_time:.1f}s, Total={total_miner_seconds:.1f}s.")
                        miner_process.terminate()
                        miner_process.wait()
                        miner_process = None
                        miner_start_time = None
            else:
                # 7) Normal threshold logic
                meters = await powerwall.get_meters()
                site_power = meters.site.instant_power

                # If negative means exporting, you might do:
                # site_power = -site_power

                if site_power >= export_start:
                    # Start miner if not running
                    if not miner_process or miner_process.poll() is not None:
                        log_info("Threshold: Starting miner.")
                        miner_process = subprocess.Popen(miner_cmd)
                        miner_start_time = time.time()
                elif site_power <= export_stop:
                    # Stop miner if running
                    if miner_process and miner_process.poll() is None:
                        run_time = time.time() - miner_start_time if miner_start_time else 0
                        total_miner_seconds += run_time
                        log_info(f"Threshold: Stopping miner. Session={run_time:.1f}s, Total={total_miner_seconds:.1f}s.")
                        miner_process.terminate()
                        miner_process.wait()
                        miner_process = None
                        miner_start_time = None

        except Exception as e:
            log_info(f"Error reading Powerwall or controlling miner: {e}")

        await asyncio.sleep(poll_interval)

if __name__ == "__main__":
    asyncio.run(main())

# Cloooock - High Precision NTP Desktop Clock

A desktop clock application that synchronizes with Network Time Protocol (NTP) servers and displays time accurate to 0.01 seconds (10 millisecond precision).

## Features

- **High Precision**: Displays time with centisecond accuracy (±0.01 seconds)
- **NTP Synchronization**: Automatically syncs with multiple NTP servers
- **Always On Top**: Clock window stays visible above other applications
- **Real-time Updates**: Clock updates every 10ms for smooth precision display
- **Multiple NTP Servers**: Fallback to backup servers if primary fails
- **Manual Sync**: Force immediate synchronization with NTP servers
- **Status Monitoring**: Shows last sync time and time offset

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- ntplib

## Installation

1. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the application:
    ```bash
    python Cloooock.py
    ```

## Usage

- The clock will automatically start and display the current time with centisecond precision
- It syncs with NTP servers every 5 minutes automatically
- Click "Sync Now" to manually synchronize with NTP servers
- Click "Settings" to view NTP server configuration
- The status bar shows last sync time and current time offset

## NTP Servers

The application uses multiple NTP servers for reliability:
- pool.ntp.org (primary)
- time.google.com
- time.cloudflare.com  
- time.nist.gov

## Precision

- Display precision: 0.01 seconds (centiseconds)
- Update frequency: 10ms (100 Hz)
- NTP accuracy: Typically within 1-50ms of true time
- Network latency compensation included

## Technical Details

The application:
1. Queries NTP servers to calculate local clock offset
2. Applies offset correction to system time
3. Updates display every 10ms for smooth centisecond display
4. Automatically re-syncs every 5 minutes to maintain accuracy
5. Uses threading to prevent GUI blocking during network operations

## License

MIT License - See LICENSE file for details.

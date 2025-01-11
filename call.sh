#!/bin/bash

CONTACT_NUMBER="123456789"
DEVICE_PASSWORD="1234"

# Function to check if device is connected
check_device() {
    if ! adb devices | grep -q "device$"; then
        echo "No device connected or device not authorized"
        exit 1
    fi
}

# Function to unlock device
unlock_device() {
    echo "Checking device state..."
    # Check if device is awake
    if adb shell dumpsys power | grep -q 'mHoldingDisplaySuspendBlocker=false'; then
        echo "Waking device..."
        adb shell input keyevent KEYCODE_WAKEUP
        sleep 1
    fi
    
    # Check if device is locked
    if adb shell dumpsys window | grep -q 'mDreamingLockscreen=true\|mShowingLockscreen=true'; then
        echo "Unlocking device..."
        adb shell input keyevent 82
        sleep 1
        adb shell input swipe 300 1000 300 300
        sleep 1
        echo "Entering password..."
        adb shell input text "$DEVICE_PASSWORD"
        adb shell input keyevent 66
        sleep 2
    fi
}

# Function to make call
make_call() {
    echo "Launching dialer..."
    adb shell am start -a android.intent.action.CALL -d tel:${CONTACT_NUMBER}
    sleep 3
    
    # No need to simulate call button press as ACTION.CALL directly initiates the call
    echo "Call in progress..."
    sleep 180  # Adjust duration as needed
    
    echo "Ending call..."
    adb shell input keyevent KEYCODE_ENDCALL
    sleep 2
}

# Main execution
echo "Starting script..."
check_device
unlock_device
make_call

# Cleanup
echo "Cleaning up..."
adb shell am force-stop com.android.dialer
echo "Script execution completed."
# Blynk App Setup Guide - SOS Alert System

This guide will help you set up a full-screen SOS-style alert in your Blynk mobile app with proper widgets and datastream assignments.

## 📱 Prerequisites

1. **Install Blynk App**
   - Download "Blynk" from Google Play Store (Android) or App Store (iOS)
   - Create a free account at https://blynk.cloud/
   - Login to your account

2. **Get Your Auth Token**
   - Go to https://blynk.cloud/
   - Click on "Templates" → Create New Template or select existing
   - Copy your Auth Token
   - Update `server/config.py` with your token:
     ```python
     BLYNK_AUTH_TOKEN = "YOUR_TOKEN_HERE"
     ```

---

## 🎨 Creating the SOS Alert Screen

### Step 1: Create a New Project in Blynk App

1. Open Blynk app on your phone
2. Tap "+" to create new project
3. Name it: **"Priority Vehicle Alert"**
4. Choose **Template**: "Blank" or "Custom"
5. **Hardware**: Select "ESP32" or "Raspberry Pi" (doesn't matter, we're using cloud API)
6. Tap **"Create"**

---

## 🔧 Widget Setup - Step by Step

### **Widget 1: Alert Status (V0) - Trigger Widget**

**Purpose**: Controls when the alert screen is shown (ON/OFF)

1. **Add Widget**: Tap "+" → Search "Button" → Select **"Button"** widget
2. **Settings**:
   - **Name**: "Alert Status"
   - **Output**: Virtual Pin **V0**
   - **Mode**: **Switch** (toggle ON/OFF)
   - **ON Label**: "ALERT ACTIVE"
   - **OFF Label**: "Normal"
3. **Appearance**: 
   - Set color to **Red** (#EF4444)
   - Make it **large** (full width)
   - Position at **top** of screen
4. **Advanced Settings**:
   - Enable "Read only" (so it shows status but user can't manually toggle during alerts)

---

### **Widget 2: Alert Title (V0) - Label Widget**

**Purpose**: Displays "ALERT" text at the top

1. **Add Widget**: Tap "+" → Search "Label" → Select **"Label"** widget
2. **Settings**:
   - **Name**: "Alert Title"
   - **Output**: Virtual Pin **V0** (or create a separate pin if needed)
   - **Text Format**: `{{value}}`
   - **Default Text**: "ALERT"
3. **Appearance**:
   - **Font Size**: **48** or larger (very large)
   - **Font Color**: **White** (#FFFFFF)
   - **Background**: **Black** (#000000)
   - **Text Alignment**: **Center**
   - **Position**: Just below Alert Status button
   - **Size**: Make it **full width**, height about **80 pixels**

---

### **Widget 3: Vehicle Name (V1) - Label Widget**

**Purpose**: Shows vehicle type (Ambulance/Firetruck)

1. **Add Widget**: Tap "+" → Select **"Label"** widget
2. **Settings**:
   - **Name**: "Vehicle Name"
   - **Output**: Virtual Pin **V1**
   - **Text Format**: `{{value}}`
   - **Default Text**: "—"
3. **Appearance**:
   - **Font Size**: **36** (large)
   - **Font Color**: **White** (#FFFFFF)
   - **Background**: **Black** (#000000)
   - **Text Alignment**: **Center**
   - **Position**: Below "ALERT" title, centered
   - **Size**: Full width, height about **60 pixels**

---

### **Widget 4: Vehicle ID (V2) - Label Widget**

**Purpose**: Shows vehicle ID (AMB001/FIRT001)

1. **Add Widget**: Tap "+" → Select **"Label"** widget
2. **Settings**:
   - **Name**: "Vehicle ID"
   - **Output**: Virtual Pin **V2**
   - **Text Format**: `{{value}}`
   - **Default Text**: "—"
3. **Appearance**:
   - **Font Size**: **28** (medium-large)
   - **Font Color**: **White** (#FFFFFF)
   - **Background**: **Black** (#000000)
   - **Text Alignment**: **Center**
   - **Position**: Below Vehicle Name, centered
   - **Size**: Full width, height about **50 pixels**

---

### **Widget 5: Direction (V3) - Label Widget**

**Purpose**: Shows direction (NS/EW)

1. **Add Widget**: Tap "+" → Select **"Label"** widget
2. **Settings**:
   - **Name**: "Direction"
   - **Output**: Virtual Pin **V3**
   - **Text Format**: `Direction: {{value}}`
   - **Default Text**: "Direction: —"
3. **Appearance**:
   - **Font Size**: **32** (large)
   - **Font Color**: **White** (#FFFFFF)
   - **Background**: **Black** (#000000)
   - **Text Alignment**: **Center**
   - **Position**: Below Vehicle ID, centered
   - **Size**: Full width, height about **55 pixels**

---

### **Widget 6: Distance (V4) - Label Widget**

**Purpose**: Shows distance in meters

1. **Add Widget**: Tap "+" → Select **"Label"** widget
2. **Settings**:
   - **Name**: "Distance"
   - **Output**: Virtual Pin **V4**
   - **Text Format**: `Distance: {{value}} m`
   - **Default Text**: "Distance: — m"
3. **Appearance**:
   - **Font Size**: **32** (large)
   - **Font Color**: **White** (#FFFFFF)
   - **Background**: **Black** (#000000)
   - **Text Alignment**: **Center**
   - **Position**: Below Direction, centered
   - **Size**: Full width, height about **55 pixels**

---

### **Widget 7: Buzzer (V5) - Buzzer Widget**

**Purpose**: Makes sound when alert is triggered

1. **Add Widget**: Tap "+" → Search "Buzzer" → Select **"Buzzer"** widget
2. **Settings**:
   - **Name**: "Alert Buzzer"
   - **Output**: Virtual Pin **V5**
   - **Mode**: **On/Off** (value 1 = ON, 0 = OFF)
3. **Advanced Settings**:
   - Enable **"Play sound when value changes"**
   - Set **Sound**: "Alert" or "Beep" (choose a loud, attention-grabbing sound)
   - Set **Volume**: **Maximum** (100%)
   - Enable **"Repeat"** if you want continuous beeping
4. **Appearance**:
   - Position at **bottom** of screen (small button)
   - Color: **Red** for visibility

---

### **Widget 8: LED/Blinker (V6) - LED Widget**

**Purpose**: Visual flashing indicator

1. **Add Widget**: Tap "+" → Search "LED" → Select **"LED"** widget
2. **Settings**:
   - **Name**: "Alert Blinker"
   - **Output**: Virtual Pin **V6**
   - **Mode**: **Brightness** (0-255, where 255 = ON)
3. **Advanced Settings**:
   - Enable **"Blink when value > 0"**
   - Set **Blink Rate**: **"Fast"** or **"Very Fast"**
   - Set **Color**: **Red** (#EF4444) for maximum visibility
4. **Appearance**:
   - Make it **large** (at least 100x100 pixels)
   - Position at **top-right** corner
   - Color: **Red** with bright glow effect

---

### **Widget 9: Color Indicator (V7) - Optional**

**Purpose**: Shows color theme (Blue for Ambulance, Red for Firetruck)

1. **Add Widget**: Tap "+" → Search "Color Picker" → Select **"Color Picker"** widget
2. **Settings**:
   - **Name**: "Alert Color"
   - **Output**: Virtual Pin **V7**
   - **Mode**: **Read Only** (shows color but doesn't allow changes)
3. **Appearance**:
   - Position at **top-left** corner
   - Size: Small circle (about 50x50 pixels)

---

## 📐 Layout Arrangement (SOS Style)

Arrange your widgets in this order from top to bottom:

```
┌─────────────────────────────────┐
│ [LED Blinker V6] (top-right)    │
│ [Color Indicator V7] (top-left)  │
│                                 │
│        [ALERT Title] V0         │  ← Large, centered
│                                 │
│     [Vehicle Name] V1           │  ← Ambulance/Firetruck
│                                 │
│     [Vehicle ID] V2            │  ← AMB001/FIRT001
│                                 │
│     Direction: [V3]            │  ← NS/EW
│                                 │
│     Distance: [V4] m           │  ← 120.5 m
│                                 │
│ [Alert Status Button] V0       │  ← At bottom
│ [Buzzer] V5                     │  ← At bottom
└─────────────────────────────────┘
```

### **Screen Settings for Full-Screen Alert Effect:**

1. **Set Background to BLACK**:
   - Go to Project Settings → **Background Color** → Set to **#000000** (Black)

2. **Make Labels Full-Width**:
   - Each Label widget should span the full width of the screen
   - Center all text

3. **Font Sizes**:
   - "ALERT": **48-60px** (very large)
   - Vehicle Name: **36px** (large)
   - Vehicle ID: **28px** (medium-large)
   - Direction: **32px** (large)
   - Distance: **32px** (large)

---

## 🔗 Datastream Assignment Summary

| Virtual Pin | Widget Type | Purpose | Value Format |
|------------|------------|---------|--------------|
| **V0** | Button + Label | Alert Status & Title | 1 = Active, 0 = Inactive |
| **V1** | Label | Vehicle Name | "Ambulance" or "Firetruck" |
| **V2** | Label | Vehicle ID | "AMB001" or "FIRT001" |
| **V3** | Label | Direction | "NS" or "EW" |
| **V4** | Label | Distance | "120.5" (meters) |
| **V5** | Buzzer | Sound Alert | 1 = ON, 0 = OFF |
| **V6** | LED | Visual Blinker | 255 = ON (blinking), 0 = OFF |
| **V7** | Color Picker | Color Theme | "3B82F6" (blue) or "EF4444" (red) |

---

## ✅ Testing Your Setup

1. **Start your server**:
   ```bash
   python -m server.server
   ```

2. **Run a vehicle simulator**:
   ```bash
   python -m vehicle.vehicle_sim --repeat --interval 3
   ```

3. **Watch your Blynk app**:
   - When vehicle gets within 120 meters, you should see:
     - Alert Status button turns ON (red)
     - "ALERT" text appears (large, white on black)
     - Vehicle name appears (Ambulance/Firetruck)
     - Vehicle ID appears (AMB001/FIRT001)
     - Direction appears (NS/EW)
     - Distance appears (e.g., "120.5 m")
     - Buzzer sounds
     - LED blinks/flashes
     - Color indicator changes (blue or red)

4. **Alert auto-resets** after 10 seconds

---

## 🎯 Tips for Best SOS Alert Effect

1. **Full-Screen Mode**: 
   - Set all labels to full width
   - Use black background
   - Large, white text for maximum contrast

2. **Blinking Effect**:
   - LED widget should be set to "Very Fast" blink rate
   - Position at top-right for maximum visibility

3. **Sound**:
   - Choose a loud, attention-grabbing sound
   - Enable "Repeat" for continuous beeping during alert

4. **Layout**:
   - Center all text vertically
   - Use consistent spacing
   - Make "ALERT" text the largest and most prominent

5. **Colors**:
   - Black background (#000000)
   - White text (#FFFFFF)
   - Red for alert indicators (#EF4444)
   - Blue for ambulance theme (#3B82F6)

---

## 🔧 Troubleshooting

### Alert not appearing?
- Check Auth Token in `server/config.py`
- Verify device is connected to Blynk Cloud
- Check server logs for errors

### Widgets not updating?
- Verify virtual pin numbers match (V0, V1, V2, etc.)
- Check widget output settings
- Ensure datastream is set to correct virtual pin

### Buzzer not working?
- Check virtual pin is V5
- Enable "Play sound when value changes"
- Check device volume is not muted
- Try different sound options

### LED not blinking?
- Check virtual pin is V6
- Enable "Blink when value > 0"
- Set blink rate to "Fast" or "Very Fast"
- Verify value is 255 when alert is active

### Text not showing properly?
- Check text format: `{{value}}` for Label widgets
- Verify font size is large enough
- Ensure text color contrasts with background (white on black)

---

## 📞 Need Help?

If you encounter issues:
1. Check server logs for Blynk API errors
2. Verify all virtual pins are correctly assigned
3. Test each widget individually
4. Ensure Blynk app is connected to internet

---

**Happy Alerting! 🚨**



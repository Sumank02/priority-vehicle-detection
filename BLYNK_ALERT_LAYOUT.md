# Blynk SOS Alert - Visual Layout Reference

This document shows how your Blynk app should look when an alert is triggered.

## 📱 Alert Screen Layout

When an alert is active (V0 = 1), your screen should look like this:

```
┌─────────────────────────────────────────┐
│  [🔴 Blinking LED]  [🔵 Color Dot]     │  ← Top corners
│                                         │
│                                         │
│              ALERT                      │  ← Large, white text (48px+)
│                                         │
│                                         │
│           Ambulance                     │  ← Vehicle Name (36px)
│                                         │
│                                         │
│            AMB001                       │  ← Vehicle ID (28px)
│                                         │
│                                         │
│         Direction: NS                   │  ← Direction (32px)
│                                         │
│                                         │
│        Distance: 120.5 m                │  ← Distance (32px)
│                                         │
│                                         │
│  [Alert Status: ACTIVE]  [🔊 Buzzer]    │  ← Bottom controls
└─────────────────────────────────────────┘
```

## 🎨 Color Scheme

- **Background**: **Black** (#000000)
- **Text**: **White** (#FFFFFF)
- **Alert Indicators**: **Red** (#EF4444)
- **Ambulance Theme**: **Blue** (#3B82F6)
- **Firetruck Theme**: **Red** (#EF4444)

## 📐 Widget Sizes & Positions

### Top Section
- **LED Blinker (V6)**: Top-right corner, 100x100px, Red, Fast blinking
- **Color Indicator (V7)**: Top-left corner, 50x50px, Blue/Red based on vehicle

### Alert Title
- **"ALERT" Text**: 
  - Font: Large (48-60px)
  - Color: White
  - Background: Black
  - Position: Centered, top third of screen
  - Width: Full screen width

### Vehicle Information (Centered)
- **Vehicle Name (V1)**: 
  - Font: Large (36px)
  - Color: White
  - Position: Below "ALERT", centered

- **Vehicle ID (V2)**: 
  - Font: Medium-Large (28px)
  - Color: White
  - Position: Below Vehicle Name, centered

- **Direction (V3)**: 
  - Font: Large (32px)
  - Color: White
  - Position: Below Vehicle ID, centered
  - Format: "Direction: NS" or "Direction: EW"

- **Distance (V4)**: 
  - Font: Large (32px)
  - Color: White
  - Position: Below Direction, centered
  - Format: "Distance: 120.5 m"

### Bottom Section
- **Alert Status Button (V0)**: 
  - Position: Bottom, left side
  - Color: Red when active
  - Text: "ALERT ACTIVE" (when V0 = 1)

- **Buzzer Widget (V5)**: 
  - Position: Bottom, right side
  - Small button, visible when active

## 🔄 Alert States

### Normal State (V0 = 0)
- Alert Status: "Normal" (grey)
- All labels: "—" or empty
- LED: OFF
- Buzzer: OFF
- Background: Black

### Alert State (V0 = 1)
- Alert Status: "ALERT ACTIVE" (red)
- Vehicle Name: "Ambulance" or "Firetruck"
- Vehicle ID: "AMB001" or "FIRT001"
- Direction: "NS" or "EW"
- Distance: "120.5 m" (actual distance)
- LED: ON (blinking fast)
- Buzzer: ON (beeping)
- Background: Black
- Color indicator: Blue (ambulance) or Red (firetruck)

## 📱 Responsive Design Tips

1. **Full Width Labels**: All Label widgets should span full screen width
2. **Centered Text**: All text should be center-aligned
3. **Vertical Spacing**: Use consistent spacing between widgets (about 20-30px)
4. **Large Fonts**: Use large fonts for maximum visibility
5. **High Contrast**: White text on black background for best readability

## 🎯 Example Alert Display

### When Ambulance Detected:
```
┌─────────────────────────────────┐
│  [🔴]  [🔵 Blue]                 │
│                                  │
│         ALERT                    │
│                                  │
│       Ambulance                  │
│                                  │
│        AMB001                    │
│                                  │
│     Direction: NS                │
│                                  │
│    Distance: 95.3 m              │
│                                  │
│  [ACTIVE]  [🔊]                  │
└─────────────────────────────────┘
```

### When Firetruck Detected:
```
┌─────────────────────────────────┐
│  [🔴]  [🔴 Red]                  │
│                                  │
│         ALERT                    │
│                                  │
│       Firetruck                 │
│                                  │
│        FIRT001                   │
│                                  │
│     Direction: EW                │
│                                  │
│    Distance: 110.2 m             │
│                                  │
│  [ACTIVE]  [🔊]                  │
└─────────────────────────────────┘
```

## 🔧 Using Eventor for Conditional Display

You can use Blynk's **Eventor** widget to automatically show "ALERT" text when V0 = 1:

1. Add **Eventor** widget
2. Set condition: **IF V0 = 1**
3. Action: **Show "ALERT"** or change Label widget visibility
4. This makes the alert appear automatically when triggered

## 💡 Pro Tips

1. **Test Layout**: Arrange widgets in edit mode first, then test
2. **Full Screen**: Use full-screen widgets for maximum impact
3. **Blinking Effect**: LED should blink "Very Fast" for attention
4. **Sound**: Use loud, attention-grabbing buzzer sound
5. **Auto-Reset**: Alert resets after 10 seconds automatically

---

**This layout creates a full-screen SOS-style alert that's impossible to miss! 🚨**



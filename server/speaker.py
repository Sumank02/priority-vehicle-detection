# -----------------------------------------------------------------------------
# 🔊 Speaker Announcement Module
# -----------------------------------------------------------------------------
# Handles audio announcements for priority vehicle detection:
# 1. Pre-recorded sound: "Firetruck Detected. Make Space."
# 2. Dynamic TTS: "Firetruck Detected. Heading from Direction. At distance."
# 
# Uses TTS (gTTS) as primary, pyttsx3 as fallback
# -----------------------------------------------------------------------------

import os
import threading
import subprocess
import platform

# Try to import TTS libraries
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# Global variables for audio state
_audio_lock = threading.Lock()
_pyttsx3_engine = None


def _init_pyttsx3():
    """Initialize pyttsx3 engine (lazy initialization)"""
    global _pyttsx3_engine
    if _pyttsx3_engine is None and PYTTSX3_AVAILABLE:
        try:
            _pyttsx3_engine = pyttsx3.init()
            # Set speech rate (words per minute)
            _pyttsx3_engine.setProperty('rate', 150)
            # Set volume (0.0 to 1.0)
            _pyttsx3_engine.setProperty('volume', 1.0)
        except Exception as e:
            print(f"[SPEAKER] Failed to initialize pyttsx3: {e}")
            return None
    return _pyttsx3_engine


def _play_audio_file(file_path):
    """Play an audio file using platform-appropriate method"""
    if not os.path.exists(file_path):
        print(f"[SPEAKER] Audio file not found: {file_path}")
        return False
    
    try:
        system = platform.system()
        if system == "Windows":
            # Windows: use built-in player
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["afplay", file_path], check=False)
        else:  # Linux
            subprocess.run(["aplay", file_path], check=False)
        return True
    except Exception as e:
        print(f"[SPEAKER] Error playing audio file: {e}")
        return False


def _play_audio_with_pygame(file_path):
    """Play audio file using pygame (for better control)"""
    if not GTTS_AVAILABLE:
        return False
    
    try:
        # Initialize pygame mixer (only once)
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        return True
    except Exception as e:
        print(f"[SPEAKER] Error playing audio with pygame: {e}")
        try:
            pygame.mixer.quit()
        except:
            pass
        return False


def _speak_with_gtts(text, lang='en'):
    """Generate and play speech using gTTS (requires internet)"""
    if not GTTS_AVAILABLE:
        return False
    
    try:
        # Create temporary audio file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_path = tmp_file.name
        
        # Generate speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(tmp_path)
        
        # Play the audio
        success = _play_audio_with_pygame(tmp_path)
        
        # Clean up
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return success
    except Exception as e:
        print(f"[SPEAKER] gTTS error: {e}")
        return False


def _speak_with_pyttsx3(text):
    """Speak text using pyttsx3 (offline, no internet required)"""
    engine = _init_pyttsx3()
    if engine is None:
        return False
    
    try:
        with _audio_lock:
            engine.say(text)
            engine.runAndWait()
        return True
    except Exception as e:
        print(f"[SPEAKER] pyttsx3 error: {e}")
        return False


def play_prerecorded_alert(vehicle_type="firetruck"):
    """
    Play pre-recorded sound: "{Vehicle} Detected. Make Space."
    Looks for audio file in assets/audio/{vehicle_type}_make_space.mp3
    
    Args:
        vehicle_type: "firetruck" or "ambulance"
    """
    # Get the project root directory (parent of server/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    audio_file = os.path.join(project_root, "assets", "audio", f"{vehicle_type}_make_space.mp3")
    
    if os.path.exists(audio_file):
        print(f"[SPEAKER] Playing pre-recorded alert: {audio_file}")
        return _play_audio_file(audio_file)
    else:
        print(f"[SPEAKER] Pre-recorded audio file not found: {audio_file}")
        print(f"[SPEAKER] Please create the file or use TTS fallback")
        return False


def announce_vehicle_detection(vehicle_type, direction, distance):
    """
    Announce vehicle detection with dynamic TTS:
    "{Vehicle} Detected. From {direction}. At {distance} meters."
    
    Uses gTTS as primary, pyttsx3 as fallback.
    
    Args:
        vehicle_type: "Firetruck" or "Ambulance"
        direction: Direction string (e.g., "North-South", "NS", "East-West", "EW")
        distance: Distance in meters (float)
    """
    # Format direction for speech
    direction_text = direction
    if direction == "NS":
        direction_text = "North-South"
    elif direction == "EW":
        direction_text = "East-West"
    
    # Format distance (round to nearest integer for speech)
    distance_int = int(round(distance))
    if distance_int == 1:
        distance_text = "1 meter"
    else:
        distance_text = f"{distance_int} meters"
    
    # Construct announcement text
    text = f"{vehicle_type} Detected. From {direction_text}. At {distance_text}."
    
    print(f"[SPEAKER] Announcing: {text}")
    
    # Try gTTS first (requires internet, better quality)
    if GTTS_AVAILABLE:
        if _speak_with_gtts(text):
            print("[SPEAKER] ✓ Announcement played using gTTS")
            return True
    
    # Fallback to pyttsx3 (offline, no internet required)
    if PYTTSX3_AVAILABLE:
        if _speak_with_pyttsx3(text):
            print("[SPEAKER] ✓ Announcement played using pyttsx3")
            return True
    
    print("[SPEAKER] ✗ No TTS engine available. Please install gTTS or pyttsx3")
    return False


def announce_firetruck_detection(direction, distance):
    """
    Announce firetruck detection (backward compatibility wrapper).
    """
    return announce_vehicle_detection("Firetruck", direction, distance)


def announce_vehicle_simple(vehicle_type="Firetruck"):
    """
    Simple announcement: "{Vehicle} Detected. Make Space."
    First tries pre-recorded sound, then falls back to TTS.
    
    Args:
        vehicle_type: "Firetruck" or "Ambulance"
    """
    # Determine vehicle type for file lookup (lowercase)
    vehicle_type_lower = vehicle_type.lower()
    
    # Try pre-recorded sound first
    if play_prerecorded_alert(vehicle_type_lower):
        return True
    
    # Fallback to TTS
    text = f"{vehicle_type} Detected. Make Space."
    print(f"[SPEAKER] Announcing: {text}")
    
    # Try gTTS first
    if GTTS_AVAILABLE:
        if _speak_with_gtts(text):
            print("[SPEAKER] ✓ Simple announcement played using gTTS")
            return True
    
    # Fallback to pyttsx3
    if PYTTSX3_AVAILABLE:
        if _speak_with_pyttsx3(text):
            print("[SPEAKER] ✓ Simple announcement played using pyttsx3")
            return True
    
    print("[SPEAKER] ✗ No audio method available")
    return False


def announce_firetruck_simple():
    """
    Simple firetruck announcement (backward compatibility wrapper).
    """
    return announce_vehicle_simple("Firetruck")


def announce_in_thread(func, *args, **kwargs):
    """Run announcement in a separate thread to avoid blocking"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


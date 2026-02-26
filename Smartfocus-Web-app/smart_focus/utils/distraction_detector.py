import threading
import time
import pygetwindow as gw


#  Always Blocked Platforms
SOCIAL_KEYWORDS = [
    "facebook",
    "instagram",
    "twitter",
    "tiktok"
]

# ⏱ Auto stop after 30 sec continuous distraction
DISTRACTION_THRESHOLD = 30


class DistractionDetector:

    def __init__(self, tracker):
        self.tracker = tracker
        self.running = True
        self.distraction_time = 0

    def start(self):
        thread = threading.Thread(target=self._monitor, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

    def _monitor(self):
        while self.running and self.tracker:
            time.sleep(2)

            try:
                window = gw.getActiveWindow()
                if not window:
                    continue

                title = window.title.lower()

                # 🔥 Safely get activity & topic
                activity = getattr(self.tracker, "activity", "").lower()
                topic = getattr(self.tracker, "topic", "").lower()

                distracted = False

                # ==================================================
                # 🚫 SOCIAL MEDIA (Always Blocked)
                # ==================================================
                if any(word in title for word in SOCIAL_KEYWORDS):
                    distracted = True

                # ==================================================
                # 🎥 YOUTUBE SMART LOGIC
                # ==================================================
                elif "youtube" in title:

                    # If activity is NOT youtube study → block
                    if activity != "youtube_study":
                        distracted = True

                    else:
                        topic_words = topic.split()

                        # If no topic entered → block
                        if not topic_words:
                            distracted = True

                        # If topic words not found in title → block
                        elif not any(word in title for word in topic_words):
                            distracted = True

                # ==================================================
                # ✅ UPDATE STATUS
                # ==================================================
                if distracted:
                    self.distraction_time += 2
                    self.tracker.session.update_status("Distracted")
                else:
                    self.distraction_time = 0
                    self.tracker.session.update_status("Focused")

                # ==================================================
                # 🚨 AUTO STOP SESSION
                # ==================================================
                if self.distraction_time >= DISTRACTION_THRESHOLD:
                    print("⚠ Auto-stopping session due to distraction")

                    self.tracker.auto_stopped = True
                    self.tracker.stop()

                    self.running = False
                    break

            except Exception:
                pass
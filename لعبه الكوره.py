# ==============================================================================
#                 NEON FOOTBALL CLASSIC (PING PONG) - BY RAYAN
# ==============================================================================
# تم التطوير والترقية بواسطة مهندس برمجيات ومصمم ألعاب محترف
# Refactored & Enhanced with Professional Clean OOP & Futuristic Visuals
# strictly maintaining all core mechanics, dimensions, and original physics.
# ==============================================================================

import turtle
import time
import random
import threading
import winsound
import os

class GameConfig:
    """
    تخزين جميع الثوابت والإعدادات لتجنب الأرقام السحرية وتحسين جودة الكود.
    Stores all game constants to eliminate magic numbers and conform to PEP8.
    """
    # Screen Settings (إعدادات الشاشة)
    WIDTH = 1500
    HEIGHT = 800
    
    # Speeds and Dynamics multipliers (السرعة وديناميكية الحركة)
    BALL_ACCELERATION = 1.05       # Progressive challenge (تسريع الكرة قليلاً عند الارتداد)
    
    # Boundaries & Original Physics (الحدود الفيزيائية الأصلية من كود ريان)
    Y_LIMIT = 390                 # Original bounce limit for upper/lower walls
    X_GOAL_LIMIT = 740            # Original goal boundary limit
    PADDLE_COLLISION_Y_RANGE = 55 # Original half-height span for paddle hit check
    
    # Target Goal (النتيجة المستهدفة للفوز)
    MAX_SCORE = 10

    # Theme database containing gorgeous harmonized retro-neon setups
    THEMES = {
        "EMERALD": {
            "bg": "#0D1117",
            "lines": "#1F2937",
            "paddle_right": "#10B981", # Neon Emerald Green (Player 1)
            "paddle_left": "#F59E0B",  # Neon Gold (Player 2 / AI)
            "ball": "#F8FAFC",
            "text": "#E2E8F0"
        },
        "GOLDEN": {
            "bg": "#120E08",
            "lines": "#2D2214",
            "paddle_right": "#D97706", # Deep Amber
            "paddle_left": "#FBBF24",  # Yellow Glow
            "ball": "#FFFBEB",
            "text": "#FDE68A"
        },
        "CYBER RED": {
            "bg": "#0F0505",
            "lines": "#3B0F0F",
            "paddle_right": "#EF4444", # Cyber Red
            "paddle_left": "#3B82F6",  # Cyber Blue
            "ball": "#F3F4F6",
            "text": "#FECACA"
        },
        "STEEL": {
            "bg": "#0B0F19",
            "lines": "#1E293B",
            "paddle_right": "#0ea5e9", # Electric Sky Blue
            "paddle_left": "#64748B",  # Industrial Slate
            "ball": "#F1F5F9",
            "text": "#E2E8F0"
        }
    }


class SoundManager:
    """
    نظام الصوت الاحترافي لإصدار النغمات دون التسبب في بطء استجابة الرسوم.
    A professional, zero-dependency async Sound Engine for Windows PCs.
    """
    def __init__(self):
        self._muted = False
        self.volume_scale = 1.0 # Standard multiplier
        
    @property
    def muted(self):
        return self._muted
        
    @muted.setter
    def muted(self, value):
        self._muted = value
        if value:
            # Stop any playing background music
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        else:
            # Restart background music if unmuted
            self.play_bg_music()
        
    def play_beep_async(self, freq, duration):
        """تشغيل نغمة أحادية بشكل غير متزامن لتجنب تجميد الشاشة"""
        if self._muted:
            return
        
        # Scale duration slightly to reflect volume changes safely
        scaled_dur = int(duration * self.volume_scale)
        if scaled_dur <= 0:
            return
            
        def run_beep():
            try:
                # winsound is synchronous on the executing thread; running in Thread solves lag
                winsound.Beep(int(freq), scaled_dur)
            except Exception:
                pass
        threading.Thread(target=run_beep, daemon=True).start()

    def play_paddle_hit(self):
        self.play_beep_async(620, 80) # Retro-arcade synth beep
        
    def play_wall_bounce(self):
        self.play_beep_async(440, 60) # Lower tone
        
    def play_score(self):
        self.play_beep_async(880, 150) # Triumphant beep
        
    def play_winner(self):
        """عزف مقطوعة نصر حماسية عند انتهاء المباراة"""
        if self._muted:
            return
        def play_fanfare():
            notes = [523, 659, 784, 1046]
            for n in notes:
                try:
                    winsound.Beep(n, 120)
                except:
                    pass
                time.sleep(0.04)
        threading.Thread(target=play_fanfare, daemon=True).start()
        
    def play_click(self):
        self.play_beep_async(700, 45) # Fast clean tick
        
    def play_pause(self):
        self.play_beep_async(500, 100)
        
    def play_resume(self):
        self.play_beep_async(950, 100)

    def play_bg_music(self):
        """تشغيل موسيقى الخلفية إذا توفر ملف صوتي باسم music.wav"""
        if self._muted:
            return
        if not os.path.exists("music.wav"):
            return
        def loop():
            try:
                # SND_FILENAME=131072 | SND_ASYNC=1 | SND_LOOP=8 | SND_NODEFAULT=2
                winsound.PlaySound("music.wav", winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP | winsound.SND_NODEFAULT)
            except Exception:
                pass
        threading.Thread(target=loop, daemon=True).start()


class Paddle(turtle.Turtle):
    """
    يمثل المضرب في اللعبة ويرث من كلاس تورتل الأساسي.
    Represents a paddle, extending turtle.Turtle.
    """
    def __init__(self, start_x, color):
        super().__init__()
        self.shape("square") # الشكل المربع الأصلي
        self.color(color)
        self.penup()
        self.goto(start_x, 0)
        self.speed(0)
        self.speed_level = 12 # Smooth speed setting
        # Dimensions: 5.5 stretch height (110px) and 1 stretch width (20px)
        # تطابق تام لأبعاد المضرب الأصلي لتجنب إتلاف اللعب
        self.shapesize(stretch_wid=5.5, stretch_len=1)
        
    def move_up(self):
        """تحريك المضرب إلى الأعلى مع الحفاظ على حدود الشاشة"""
        y = self.ycor()
        if y < 330:  # Prevent paddle from going off the upper border
            self.sety(y + self.speed_level)
            
    def move_down(self):
        """تحريك المضرب إلى الأسفل مع الحفاظ على حدود الشاشة"""
        y = self.ycor()
        if y > -330:  # Prevent paddle from going off the lower border
            self.sety(y - self.speed_level)


class Ball(turtle.Turtle):
    """
    يمثل الكرة في اللعبة ويرث من كلاس تورتل الأساسي.
    Represents the ball, extending turtle.Turtle.
    """
    def __init__(self):
        super().__init__()
        self.shape("square") # الحفاظ على شكل المربع الكلاسيكي
        self.color("#F8FAFC")
        self.penup()
        self.goto(0, 0)
        self.speed(0)
        self.base_dx = 4.5
        self.base_dy = 4.5
        self.dx = self.base_dx
        self.dy = self.base_dy
        
    def set_base_speed(self, speed_option):
        """تعديل سرعة البداية بناء على لوحة التحكم"""
        if speed_option == "SLOW":
            self.base_dx, self.base_dy = 3.0, 3.0
        elif speed_option == "NORMAL":
            self.base_dx, self.base_dy = 4.5, 4.5
        elif speed_option == "FAST":
            self.base_dx, self.base_dy = 6.5, 6.5
        self.reset_speed()
        
    def reset_speed(self):
        """إعادة تعيين السرعة الافتراضية للكرة"""
        self.dx = self.base_dx if self.dx > 0 else -self.base_dx
        self.dy = self.base_dy if self.dy > 0 else -self.base_dy
        
    def move(self):
        """تحديث موقع الكرة حسب سرعتها الحالية"""
        self.setx(self.xcor() + self.dx)
        self.sety(self.ycor() + self.dy)
        
    def bounce_y(self):
        """عكس الاتجاه على المحور الصادي (ارتداد من الحوائط)"""
        self.dy *= -1
        
    def bounce_x(self):
        """عكس الاتجاه على المحور السيني (ارتداد من المضارب)"""
        self.dx *= -1
        
    def reset_to_center(self):
        """إعادة الكرة للمنتصف وعكس اتجاه الانطلاق"""
        self.goto(0, 0)
        self.reset_speed()
        self.dx *= -1  # Reverse starting direction for fairness


class StadiumHUD:
    """
    مسؤول عن رسم تخطيط الملعب الجمالي ولوحة النتائج.
    Responsible for drawing the stadium pitch markings and scoreboard HUD.
    """
    def __init__(self):
        # Draw static field lines using a dedicated turtle to keep rendering fast and isolated
        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.hideturtle()
        self.pen.penup()
        
        # Create a dedicated turtle for score display text
        self.score_pen = turtle.Turtle()
        self.score_pen.speed(0)
        self.score_pen.hideturtle()
        self.score_pen.penup()
        self.score_pen.color("#E2E8F0")
        
    def draw_pitch_with_color(self, color):
        """إعادة رسم مخطط الملعب باللون المختار من لوحة الإعدادات"""
        self.pen.clear()
        self.pen.pensize(2)
        
        # Outer pitch border (الحدود الخارجية للملعب)
        self.pen.color(color)
        self.pen.goto(-730, 380)
        self.pen.pendown()
        for _ in range(2):
            self.pen.forward(1460)
            self.pen.right(90)
            self.pen.forward(760)
            self.pen.right(90)
        self.pen.penup()
        
        # Halfway line (خط المنتصف)
        self.pen.goto(0, 380)
        self.pen.setheading(270)
        self.pen.pendown()
        self.pen.forward(760)
        self.pen.penup()
        
        # Center Circle (دائرة المنتصف)
        self.pen.goto(0, -90)
        self.pen.setheading(0)
        self.pen.pendown()
        self.pen.circle(90)
        self.pen.penup()
        
        # Left Goal box (منطقة مرمى اليسار)
        self.pen.goto(-730, 180)
        self.pen.pendown()
        self.pen.forward(90)
        self.pen.right(90)
        self.pen.forward(360)
        self.pen.right(90)
        self.pen.forward(90)
        self.pen.penup()
        
        # Right Goal box (منطقة مرمى اليمين)
        self.pen.goto(730, 180)
        self.pen.pendown()
        self.pen.backward(90)
        self.pen.right(90)
        self.pen.forward(360)
        self.pen.right(90)
        self.pen.backward(90)
        self.pen.penup()

    def update_score(self, score1, score2):
        """تحديث عرض النتيجة بألوان متناسقة وتصميم نيون حديث"""
        self.score_pen.clear()
        self.score_pen.goto(0, 340)
        # Preserving original Rayan syntax formatting but giving it a premium glow look with emoji
        display_text = f"player1 : {score1}      ⚽      player2 : {score2}"
        self.score_pen.write(display_text, align="center", font=("Arial", 25, "bold"))
        
    def draw_overlay_text(self, text, size=40, y_offset=0, color="white", font_name="Arial"):
        """رسم نصوص الشاشات المؤقتة التفاعلية وتخزين مرجع لها لتنظيفها لاحقاً"""
        overlay = turtle.Turtle()
        overlay.speed(0)
        overlay.hideturtle()
        overlay.penup()
        overlay.color(color)
        overlay.goto(0, y_offset)
        overlay.write(text, align="center", font=(font_name, size, "bold"))
        return overlay


class Particle:
    """يمثل جسيماً فريداً في نظام المؤثرات البصرية التفاعلية"""
    def __init__(self):
        self.t = turtle.Turtle()
        self.t.shape("circle")
        self.t.shapesize(0.2, 0.2)
        self.t.penup()
        self.t.hideturtle()
        self.dx = 0
        self.dy = 0
        self.life = 0


class ParticleSystem:
    """
    نظام الجسيمات التفاعلي لإضافة تأثير نيون عند الاصطدام أو إحراز هدف.
    An interactive visual particle system that adds a stunning juicy visual effect.
    """
    def __init__(self, count=25):
        # Pre-allocate particle pool to prevent performance lag at runtime
        self.particles = [Particle() for _ in range(count)]
        
    def spawn(self, x, y, colors):
        """توليد جسيمات ملونة عشوائية السرعات عند إحداثيات الاصطدام"""
        for p in self.particles:
            if p.life <= 0:
                p.t.goto(x, y)
                p.t.color(random.choice(colors))
                p.t.showturtle()
                p.dx = random.uniform(-6, 6)
                p.dy = random.uniform(-6, 6)
                p.life = random.randint(15, 25) # Lifespan in frame counts
                
    def update(self):
        """تحديث حركة جميع الجسيمات الفعالة وتقليل عمرها الافتراضي"""
        for p in self.particles:
            if p.life > 0:
                p.t.goto(p.t.xcor() + p.dx, p.t.ycor() + p.dy)
                p.life -= 1
                if p.life <= 0:
                    p.t.hideturtle()


class KeyboardController:
    """
    نظام تحكم متطور يتتبع حالة المفاتيح لتوجيه اللعبة وإدارة التبادل بين اللعب وقائمة الإعدادات.
    Advanced controller that manages active key bindings based on the current state.
    """
    def __init__(self, wind, game):
        self.wind = wind
        self.game = game
        self.keys = {
            "Up": False, "Down": False,
            "a": False, "z": False,
            "w": False, "s": False
        }
        
    def set_key(self, key, state):
        self.keys[key] = state
        
    def set_mode(self, mode):
        """إعادة ربط المفاتيح لتلائم حالة الشاشة النشطة"""
        self.wind.listen()
        
        # Reset current moving states
        for k in self.keys:
            self.keys[k] = False
            
        if mode == "gameplay":
            # 1. Clear previous settings keys
            self.wind.onkeypress(None, "Left")
            self.wind.onkeypress(None, "Right")
            self.wind.onkeypress(None, "Return")
            self.wind.onkeypress(None, "Escape")
            
            # 2. Continuous gameplay bindings
            # Right Player (Arrow keys)
            self.wind.onkeypress(lambda: self.set_key("Up", True), "Up")
            self.wind.onkeyrelease(lambda: self.set_key("Up", False), "Up")
            self.wind.onkeypress(lambda: self.set_key("Down", True), "Down")
            self.wind.onkeyrelease(lambda: self.set_key("Down", False), "Down")
            
            # Left Player (Classic A/Z and ALT W/S keys)
            self.wind.onkeypress(lambda: self.set_key("a", True), "a")
            self.wind.onkeyrelease(lambda: self.set_key("a", False), "a")
            self.wind.onkeypress(lambda: self.set_key("z", True), "z")
            self.wind.onkeyrelease(lambda: self.set_key("z", False), "z")
            
            self.wind.onkeypress(lambda: self.set_key("w", True), "w")
            self.wind.onkeyrelease(lambda: self.set_key("w", False), "w")
            self.wind.onkeypress(lambda: self.set_key("s", True), "s")
            self.wind.onkeyrelease(lambda: self.set_key("s", False), "s")
            
            # 3. Game Management Hotkeys
            self.wind.onkeypress(self.game.toggle_pause, "p")
            self.wind.onkeypress(self.game.toggle_pause, "P")
            self.wind.onkeypress(self.game.press_space, "space")
            self.wind.onkeypress(self.game.toggle_settings, "t")
            self.wind.onkeypress(self.game.toggle_settings, "T")
            self.wind.onkeypress(self.game.toggle_settings, "s")
            self.wind.onkeypress(self.game.toggle_settings, "S")
            
        elif mode == "settings":
            # 1. Unbind gameplay keys to prevent moving paddles in settings
            self.wind.onkeyrelease(None, "Up")
            self.wind.onkeyrelease(None, "Down")
            self.wind.onkeyrelease(None, "a")
            self.wind.onkeyrelease(None, "z")
            self.wind.onkeyrelease(None, "w")
            self.wind.onkeyrelease(None, "s")
            
            # 2. Bind Settings Navigation Controls
            self.wind.onkeypress(lambda: self.game.navigate_settings(-1), "Up")
            self.wind.onkeypress(lambda: self.game.navigate_settings(1), "Down")
            self.wind.onkeypress(lambda: self.game.adjust_setting(-1), "Left")
            self.wind.onkeypress(lambda: self.game.adjust_setting(1), "Right")
            self.wind.onkeypress(self.game.trigger_setting_action, "Return")
            
            # 3. Save & Close Triggers
            self.wind.onkeypress(self.game.toggle_settings, "Escape")
            self.wind.onkeypress(self.game.toggle_settings, "t")
            self.wind.onkeypress(self.game.toggle_settings, "T")
            self.wind.onkeypress(self.game.toggle_settings, "s")
            self.wind.onkeypress(self.game.toggle_settings, "S")


class FootballGame:
    """
    المنسق الرئيسي لجميع عناصر اللعبة، والفيزياء، وإدارة الحالات.
    The primary game orchestrator, managing physics, scoring, overlays, and loop updates.
    """
    # Game States
    STATE_START = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    STATE_GAME_OVER = 3
    STATE_SETTINGS = 4
    STATE_COUNTDOWN = 5

    def __init__(self):
        # 1. Screen setup (إعداد الشاشة والنافذة)
        self.wind = turtle.Screen()
        self.wind.title("ping pong game made by rayan - Ultimate Edition")
        self.wind.bgcolor(GameConfig.THEMES["EMERALD"]["bg"])
        self.wind.setup(width=GameConfig.WIDTH, height=GameConfig.HEIGHT)
        self.wind.tracer(0) # تعطيل التحديث التلقائي للتحكم فيه يدوياً لمعدل إطارات مستقر
        
        # 2. Setup HUD and Systems (إعداد لوحة النتيجة ورسم الملعب والأنظمة المساعدة)
        self.hud = StadiumHUD()
        self.sound = SoundManager()
        self.particles = ParticleSystem(30)
        self.controller = KeyboardController(self.wind, self)
        
        # Setup static stadium markings
        self.hud.draw_pitch_with_color(GameConfig.THEMES["EMERALD"]["lines"])
        
        # Match scores
        self.score1 = 0
        self.score2 = 0
        self.hud.update_score(self.score1, self.score2)
        
        # 3. Setup Entities (إعداد عناصر اللعب)
        self.madrab1 = Paddle(700, GameConfig.THEMES["EMERALD"]["paddle_right"])   # Right Paddle (المضرب الأول)
        self.madrab2 = Paddle(-700, GameConfig.THEMES["EMERALD"]["paddle_left"])  # Left Paddle (المضرب الثاني)
        self.ball = Ball()
        
        # 4. In-Game Settings Engine Configurations
        self.settings_options = [
            {"name": "AI Opponent", "key": "ai_mode", "values": ["OFF", "ON"], "index": 0},
            {"name": "Difficulty", "key": "difficulty", "values": ["EASY", "NORMAL", "HARD", "INSANE"], "index": 1},
            {"name": "Arena Theme", "key": "theme", "values": ["EMERALD", "GOLDEN", "CYBER RED", "STEEL"], "index": 0},
            {"name": "Sound Effects", "key": "sound", "values": ["UNMUTED", "MUTED"], "index": 0},
            {"name": "Ball Speed", "key": "ball_speed", "values": ["SLOW", "NORMAL", "FAST"], "index": 1},
            {"name": "Paddle Glide", "key": "paddle_speed", "values": ["SLOW", "NORMAL", "FAST"], "index": 1},
            {"name": "Left Controls", "key": "bindings", "values": ["A/Z KEYS", "W/S KEYS"], "index": 0},
            {"name": "Screen Mode", "key": "fullscreen", "values": ["WINDOWED", "FULLSCREEN"], "index": 0},
            {"name": "Restart Match", "key": "action", "action": "restart"},
            {"name": "Exit Safely", "key": "action", "action": "exit"}
        ]
        self.selected_setting_index = 0
        self.ai_mode = "OFF"
        self.difficulty = "NORMAL"
        self.active_theme_name = "EMERALD"
        
        # 5. Difficulty scaled values
        self.difficulty_settings = {
            "EASY": {"ai_speed": 4.5, "ai_margin": 45, "ball_multiplier": 0.8},
            "NORMAL": {"ai_speed": 7.0, "ai_margin": 25, "ball_multiplier": 1.0},
            "HARD": {"ai_speed": 10.5, "ai_margin": 10, "ball_multiplier": 1.25},
            "INSANE": {"ai_speed": 14.0, "ai_margin": 2, "ball_multiplier": 1.5}
        }
        
        # Start game triggers
        self.active_overlays = []
        self.previous_state = self.STATE_START
        self.state = self.STATE_START
        self.show_start_screen()
        self.controller.set_mode("gameplay")
        
        # Launch background audio loop securely
        self.sound.play_bg_music()
        
    def clear_overlays(self):
        """إزالة أي نصوص واجهة مؤقتة من الشاشة"""
        for t in self.active_overlays:
            t.clear()
            t.hideturtle()
        self.active_overlays.clear()
        
    def show_start_screen(self):
        """شاشة البداية الاحترافية للعبة"""
        self.clear_overlays()
        t1 = self.hud.draw_overlay_text("NEON FOOTBALL CLASSIC", size=48, y_offset=80, color=GameConfig.THEMES[self.active_theme_name]["paddle_right"])
        t2 = self.hud.draw_overlay_text("developed by Rayan", size=22, y_offset=20, color=GameConfig.THEMES[self.active_theme_name]["paddle_left"])
        t3 = self.hud.draw_overlay_text("Press SPACE to Kick Off!", size=26, y_offset=-60, color="#F8FAFC")
        t4 = self.hud.draw_overlay_text("Controls: Player 1 (Right): [Up/Down] | Player 2 (Left): [A/Z] or [W/S]", size=14, y_offset=-160, color="#64748B")
        t5 = self.hud.draw_overlay_text("Press [P] to Pause | Press [T] or [S] for In-Game Settings Panel", size=14, y_offset=-200, color="#64748B")
        self.active_overlays.extend([t1, t2, t3, t4, t5])
        
    def show_pause_screen(self):
        """واجهة إيقاف اللعبة المؤقت"""
        t1 = self.hud.draw_overlay_text("GAME PAUSED", size=45, y_offset=40, color="#FBBF24")
        t2 = self.hud.draw_overlay_text("Press P to Resume Match", size=22, y_offset=-30, color="#F8FAFC")
        self.active_overlays.extend([t1, t2])
        
    def show_winner_screen(self, winner_name, winner_color):
        """عرض واجهة الفوز وحفلة النصر النهائية"""
        t1 = self.hud.draw_overlay_text(f"🏆 {winner_name} WINS! 🏆", size=50, y_offset=60, color=winner_color)
        t2 = self.hud.draw_overlay_text("The Stadium Celebrates Your Victory!", size=20, y_offset=-10, color="#E2E8F0")
        t3 = self.hud.draw_overlay_text("Press SPACE to Rematch", size=24, y_offset=-90, color="#10B981")
        self.active_overlays.extend([t1, t2, t3])

    def show_settings_screen(self):
        """رسم لوحة إعدادات التحكم النشطة"""
        self.clear_overlays()
        
        t_header = self.hud.draw_overlay_text("⚙️ STADIUM SETTINGS PANEL ⚙️", size=28, y_offset=200, color="#F59E0B", font_name="Courier")
        self.active_overlays.append(t_header)
        
        start_y = 120
        for idx, opt in enumerate(self.settings_options):
            is_selected = (idx == self.selected_setting_index)
            color = GameConfig.THEMES[self.active_theme_name]["paddle_right"] if is_selected else "#64748B"
            cursor = "👉 " if is_selected else "   "
            
            if "values" in opt:
                current_val = opt["values"][opt["index"]]
                display_text = f"{cursor}{opt['name']:<20} : [ {current_val} ]"
            else:
                display_text = f"{cursor}[ {opt['name']} ]"
                
            t_opt = self.hud.draw_overlay_text(display_text, size=16, y_offset=start_y, color=color, font_name="Courier")
            self.active_overlays.append(t_opt)
            start_y -= 38
            
        t_footer1 = self.hud.draw_overlay_text("Use UP/DOWN Arrows to Navigate | LEFT/RIGHT to Change Values", size=11, y_offset=-265, color="#475569", font_name="Courier")
        t_footer2 = self.hud.draw_overlay_text("Press ENTER to Trigger Actions | Press ESC or 'T' to Save & Close", size=11, y_offset=-295, color="#475569", font_name="Courier")
        self.active_overlays.extend([t_footer1, t_footer2])

    def start_countdown(self):
        """تشغيل عداد تنازلي تفاعلي مع إصدار نغمات تنبيه قبل انطلاق الكرة"""
        self.state = self.STATE_COUNTDOWN
        self.clear_overlays()
        
        def step(count):
            self.clear_overlays()
            if count > 0:
                t = self.hud.draw_overlay_text(str(count), size=75, y_offset=0, color=GameConfig.THEMES[self.active_theme_name]["paddle_left"])
                self.active_overlays.append(t)
                self.sound.play_click()
                self.wind.ontimer(lambda: step(count - 1), 700) # Run next number in 700ms asynchronously
            else:
                t = self.hud.draw_overlay_text("GO!", size=60, y_offset=0, color=GameConfig.THEMES[self.active_theme_name]["paddle_right"])
                self.active_overlays.append(t)
                self.sound.play_resume()
                
                def resume():
                    self.clear_overlays()
                    self.state = self.STATE_PLAYING
                self.wind.ontimer(resume, 500)
                
        step(3)

    def toggle_settings(self):
        """التبديل بين وضع اللعب وقائمة الإعدادات"""
        if self.state != self.STATE_SETTINGS:
            self.previous_state = self.state
            self.state = self.STATE_SETTINGS
            self.controller.set_mode("settings")
            self.sound.play_click()
            self.show_settings_screen()
        else:
            self.exit_settings()

    def navigate_settings(self, direction):
        """التنقل بين خيارات قائمة الإعدادات للأعلى والأسفل"""
        self.selected_setting_index = (self.selected_setting_index + direction) % len(self.settings_options)
        self.sound.play_click()
        self.show_settings_screen()

    def adjust_setting(self, direction):
        """تعديل قيم الخيارات باليمين واليسار وتطبيق التغييرات فوراً"""
        opt = self.settings_options[self.selected_setting_index]
        if "values" in opt:
            opt["index"] = (opt["index"] + direction) % len(opt["values"])
            val = opt["values"][opt["index"]]
            
            # Action: Audio Mute logic
            if opt["key"] == "sound":
                self.sound.muted = (val == "MUTED")
                
            # Action: AI Engine Toggle
            elif opt["key"] == "ai_mode":
                self.ai_mode = val
                
            # Action: Difficulty
            elif opt["key"] == "difficulty":
                self.difficulty = val
                
            # Action: Color Themes
            elif opt["key"] == "theme":
                self.active_theme_name = val
                self.apply_theme(val)
                
            # Action: Screen mode toggle
            elif opt["key"] == "fullscreen":
                self.toggle_fullscreen(val)
                
            self.sound.play_click()
            self.show_settings_screen()

    def trigger_setting_action(self):
        """تفعيل الأفعال الإجرائية المختارة مثل إعادة المباراة أو إغلاق الشاشة"""
        opt = self.settings_options[self.selected_setting_index]
        if "action" in opt:
            action = opt["action"]
            self.sound.play_click()
            if action == "restart":
                self.reset_entire_match()
                self.exit_settings()
            elif action == "exit":
                self.wind.bye()

    def apply_theme(self, theme_name):
        """تطبيق المظهر والنمط اللوني المختار فوراً على كافة عناصر اللعبة"""
        theme = GameConfig.THEMES[theme_name]
        self.wind.bgcolor(theme["bg"])
        self.madrab1.color(theme["paddle_right"])
        self.madrab2.color(theme["paddle_left"])
        self.ball.color(theme["ball"])
        self.hud.draw_pitch_with_color(theme["lines"])
        self.hud.score_pen.color(theme["text"])
        self.hud.update_score(self.score1, self.score2)

    def toggle_fullscreen(self, mode):
        """إدخال النافذة بوضع ملء الشاشة الكامل أو إعادة تقليصها"""
        try:
            is_fs = (mode == "FULLSCREEN")
            self.wind._root.attributes("-fullscreen", is_fs)
        except Exception:
            pass

    def exit_settings(self):
        """الخروج الآمن من الإعدادات وإعادة ربط المفاتيح والعودة للعب بعد عداد تنازلي"""
        self.clear_overlays()
        self.sound.play_resume()
        self.controller.set_mode("gameplay")
        
        # Apply current configs values
        # 1. Ball Base speed
        ball_speed_opt = self.settings_options[4]["values"][self.settings_options[4]["index"]]
        self.ball.set_base_speed(ball_speed_opt)
        
        # 2. Paddle Gliding Speed
        paddle_speed_opt = self.settings_options[5]["values"][self.settings_options[5]["index"]]
        p_speed = 8 if paddle_speed_opt == "SLOW" else (12 if paddle_speed_opt == "NORMAL" else 18)
        self.madrab1.speed_level = p_speed
        self.madrab2.speed_level = p_speed
        
        self.state = self.previous_state
        if self.state == self.STATE_PLAYING:
            self.start_countdown()
        elif self.state == self.STATE_START:
            self.show_start_screen()
        elif self.state == self.STATE_PAUSED:
            self.show_pause_screen()
        elif self.state == self.STATE_GAME_OVER:
            # Re-freeze ball
            self.freeze_ball()

    def toggle_pause(self):
        """تفعيل الإيقاف المؤقت أثناء المباراة"""
        if self.state == self.STATE_PLAYING:
            self.state = self.STATE_PAUSED
            self.sound.play_pause()
            self.show_pause_screen()
        elif self.state == self.STATE_PAUSED:
            self.clear_overlays()
            self.sound.play_resume()
            self.start_countdown()

    def press_space(self):
        """زر المسافة لبدء المنافسة أو إعادة خوض المباراة"""
        if self.state == self.STATE_START:
            self.clear_overlays()
            self.start_countdown()
        elif self.state == self.STATE_GAME_OVER:
            self.reset_entire_match()
            self.clear_overlays()
            self.start_countdown()

    def update_ai(self):
        """توجيه ذكاء اصطناعي تفاعلي لمضرب الخصم الأيسر بفيزياء ارتداد ومستويات تتبع مختلفة"""
        if self.state == self.STATE_PLAYING and self.ai_mode == "ON":
            ball_y = self.ball.ycor()
            paddle_y = self.madrab2.ycor()
            
            # Fetch properties matching selected difficulty level
            diff_config = self.difficulty_settings[self.difficulty]
            max_track_speed = diff_config["ai_speed"]
            deadzone_margin = diff_config["ai_margin"]
            
            # Glide smoothly towards ball Y alignment within limits
            if abs(paddle_y - ball_y) > deadzone_margin:
                if paddle_y < ball_y:
                    self.madrab2.sety(min(330, paddle_y + max_track_speed))
                else:
                    self.madrab2.sety(max(-330, paddle_y - max_track_speed))

    def handle_input(self):
        """معالجة استمرار حركة المضارب اليدوية للاعبين"""
        if self.state == self.STATE_PLAYING:
            # 1. Player 1 (Right Paddle Arrow movement)
            if self.controller.keys["Up"]:
                self.madrab1.move_up()
            if self.controller.keys["Down"]:
                self.madrab1.move_down()
                
            # 2. Player 2 (Left Paddle movement - active if AI is disabled)
            if self.ai_mode == "OFF":
                bindings_opt = self.settings_options[6]["values"][self.settings_options[6]["index"]]
                
                if bindings_opt == "A/Z KEYS":
                    if self.controller.keys["a"]:
                        self.madrab2.move_up()
                    if self.controller.keys["z"]:
                        self.madrab2.move_down()
                else: # W/S Bindings
                    if self.controller.keys["w"]:
                        self.madrab2.move_up()
                    if self.controller.keys["s"]:
                        self.madrab2.move_down()

    def check_collisions(self):
        """إدارة فيزياء الاصطدام والارتداد والحدود الخارجية والأهداف"""
        ball = self.ball
        madrab1 = self.madrab1
        madrab2 = self.madrab2
        
        # Adjust difficulty ball multiplier to scale movement speed if difficulty altered
        diff_mul = self.difficulty_settings[self.difficulty]["ball_multiplier"]
        curr_dx = ball.dx * diff_mul
        curr_dy = ball.dy * diff_mul
        
        # Apply movements
        ball.setx(ball.xcor() + curr_dx)
        ball.sety(ball.ycor() + curr_dy)
        
        # 1. Top and Bottom wall collisions (الاصطدام بالحوائط العلوية والسفلية)
        if ball.ycor() > GameConfig.Y_LIMIT:
            ball.sety(GameConfig.Y_LIMIT)
            ball.bounce_y()
            self.sound.play_wall_bounce()
            self.particles.spawn(ball.xcor(), ball.ycor(), ["#E2E8F0", "#94A3B8"])
            
        elif ball.ycor() < -GameConfig.Y_LIMIT:
            ball.sety(-GameConfig.Y_LIMIT)
            ball.bounce_y()
            self.sound.play_wall_bounce()
            self.particles.spawn(ball.xcor(), ball.ycor(), ["#E2E8F0", "#94A3B8"])
            
        # 2. Right Goal Collision (الكرة تتخطى الجدار الأيمن - هدف للاعب الأول)
        # الحفاظ على منطق الحساب الأصلي من ريان: score1 تزيد عند وصول الكرة للحافة اليمنى (x > 740)
        if ball.xcor() > GameConfig.X_GOAL_LIMIT:
            self.score1 += 1
            self.hud.update_score(self.score1, self.score2)
            self.sound.play_score()
            self.particles.spawn(0, 0, [GameConfig.THEMES[self.active_theme_name]["paddle_right"], "#F8FAFC"])
            ball.reset_to_center()
            self.check_game_over()
            if self.state == self.STATE_PLAYING:
                self.start_countdown()
            
        # 3. Left Goal Collision (الكرة تتخطى الجدار الأيسر - هدف للاعب الثاني)
        # الحفاظ على منطق الحساب الأصلي من ريان: score2 تزيد عند وصول الكرة للحافة اليسرى (x < -740)
        elif ball.xcor() < -GameConfig.X_GOAL_LIMIT:
            self.score2 += 1
            self.hud.update_score(self.score1, self.score2)
            self.sound.play_score()
            self.particles.spawn(0, 0, [GameConfig.THEMES[self.active_theme_name]["paddle_left"], "#F8FAFC"])
            ball.reset_to_center()
            self.check_game_over()
            if self.state == self.STATE_PLAYING:
                self.start_countdown()
            
        # 4. Right Paddle Collision (الاصطدام بالمضرب الأول الأيمن)
        # الحفاظ التام على أبعاد الارتداد الدقيقة ومحيط المضرب الأصلي: (x > 680 and x < 700)
        if 680 <= ball.xcor() <= 700 and ball.dx > 0:
            if madrab1.ycor() - GameConfig.PADDLE_COLLISION_Y_RANGE <= ball.ycor() <= madrab1.ycor() + GameConfig.PADDLE_COLLISION_Y_RANGE:
                ball.setx(680) # Anti-sticking fix (تأمين موقع الكرة لمنع تعليقها داخل المضرب)
                ball.bounce_x()
                ball.dx *= GameConfig.BALL_ACCELERATION
                ball.dy *= GameConfig.BALL_ACCELERATION
                self.sound.play_paddle_hit()
                self.particles.spawn(ball.xcor(), ball.ycor(), [GameConfig.THEMES[self.active_theme_name]["paddle_right"], "#FFFFFF"])
                
        # 5. Left Paddle Collision (الاصطدام بالمضرب الثاني الأيسر)
        # الحفاظ التام على أبعاد الارتداد ومحيط المضرب الأصلي: (x < -680 and x > -700)
        if -700 <= ball.xcor() <= -680 and ball.dx < 0:
            if madrab2.ycor() - GameConfig.PADDLE_COLLISION_Y_RANGE <= ball.ycor() <= madrab2.ycor() + GameConfig.PADDLE_COLLISION_Y_RANGE:
                ball.setx(-680) # Anti-sticking fix
                ball.bounce_x()
                ball.dx *= GameConfig.BALL_ACCELERATION
                ball.dy *= GameConfig.BALL_ACCELERATION
                self.sound.play_paddle_hit()
                self.particles.spawn(ball.xcor(), ball.ycor(), [GameConfig.THEMES[self.active_theme_name]["paddle_left"], "#FFFFFF"])

    def check_game_over(self):
        """التحقق من انتهاء المباراة وفوز أحد اللاعبين بنتيجة 10 أهداف"""
        if self.score1 >= GameConfig.MAX_SCORE:
            self.state = self.STATE_GAME_OVER
            self.sound.play_winner()
            self.show_winner_screen("PLAYER 1", GameConfig.THEMES[self.active_theme_name]["paddle_right"])
            self.freeze_ball()
        elif self.score2 >= GameConfig.MAX_SCORE:
            self.state = self.STATE_GAME_OVER
            self.sound.play_winner()
            self.show_winner_screen("PLAYER 2", GameConfig.THEMES[self.active_theme_name]["paddle_left"])
            self.freeze_ball()
            
    def freeze_ball(self):
        """إيقاف الكرة وتصفير حركتها عند نهاية اللعبة"""
        self.ball.goto(0, 0)
        self.ball.dx = 0
        self.ball.dy = 0
        
    def reset_entire_match(self):
        """إعادة تهيئة كاملة للمباراة وبدء منافسة جديدة"""
        self.score1 = 0
        self.score2 = 0
        self.hud.update_score(self.score1, self.score2)
        self.ball.reset_speed()
        self.ball.goto(0, 0)
        self.madrab1.goto(700, 0)
        self.madrab2.goto(-700, 0)
        self.clear_overlays()
        
    def run(self):
        """الحلقة الرئيسية المستمرة للعبة (Main Game Loop)"""
        while True:
            try:
                # 1. Update hand continuous keys movements
                self.handle_input()
                
                # 2. Update AI tracking if enabled
                self.update_ai()
                
                # 3. Physics updates if actively playing
                if self.state == FootballGame.STATE_PLAYING:
                    self.check_collisions()
                    
                # 4. Particle system ticks
                self.particles.update()
                
                # 5. Render window updates
                self.wind.update()
                
                # 6. Low footprint sleep delay to support consistent speeds on modern high-speed CPUs
                time.sleep(0.005)
                
            except turtle.Terminated:
                # Safe exit on window close
                break


if __name__ == "__main__":
    # Launching the Ultimate portfolio edition
    game = FootballGame()
    game.run()
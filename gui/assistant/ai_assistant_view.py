"""
In-App Interactive AI Assistant Interface (AIAssistantView).
Provides a dedicated conversational chat experience supporting both text and voice input,
suggestion prompt chips, and rich structured text-only card replies.
Operates 100% offline without API key requirements.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional, Callable

from services.ai_assistant_service import AIAssistantService
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import add_hover_effect


class AIAssistantView(tk.Frame):
    """Dedicated in-app chat interface for ContactAI."""

    def __init__(self, parent: tk.Widget, ai_service: AIAssistantService, on_action_done: Optional[Callable[[], None]] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.ai_service = ai_service
        self.on_action_done = on_action_done

        self._init_ui()
        self._send_welcome_message()

    def _init_ui(self):
        # 1. Header
        header = tk.Frame(self, bg=COLORS["bg_sidebar"], padx=25, pady=14, relief="solid", borderwidth=1)
        header.pack(fill="x")

        left_h = tk.Frame(header, bg=COLORS["bg_sidebar"])
        left_h.pack(side="left")

        tk.Label(
            left_h,
            text="🤖  ContactAI Assistant",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["gold_bright"],
            font=FONTS["title_large"]
        ).pack(anchor="w")

        status_row = tk.Frame(left_h, bg=COLORS["bg_sidebar"])
        status_row.pack(anchor="w", pady=(2, 0))

        tk.Label(status_row, text="●", bg=COLORS["bg_sidebar"], fg=COLORS["success"], font=FONTS["micro"]).pack(side="left", padx=(0, 4))
        tk.Label(
            status_row,
            text="Autonomous Offline NLP Engine Active • Standalone Executable Ready",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_muted"],
            font=FONTS["micro"]
        ).pack(side="left")

        btn_clear = tk.Button(
            header,
            text="🧹 Clear Chat",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"],
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._clear_chat
        )
        btn_clear.pack(side="right")

        # 2. Quick Suggestion Prompt Chips Bar
        chips_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=8)
        chips_frame.pack(fill="x")

        tk.Label(chips_frame, text="Quick Actions:", bg=COLORS["bg_main"], fg=COLORS["text_dim"], font=FONTS["micro"]).pack(side="left", padx=(0, 8))

        suggestions = [
            ("📊 Analyze Contacts", "Analyze my contacts"),
            ("🔍 Search Microsoft", "Search for Microsoft"),
            ("⚠️ Check Duplicates", "Check for duplicates"),
            ("⭐ Show Favorites", "Show my favorites"),
            ("❓ Help & Commands", "What can you do?"),
        ]
        for label, query in suggestions:
            btn = tk.Button(
                chips_frame,
                text=label,
                bg=COLORS["bg_card"],
                fg=COLORS["gold_bright"],
                font=FONTS["body_small"],
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda q=query: self._submit_prompt(q)
            )
            btn.pack(side="left", padx=4)
            add_hover_effect(btn, COLORS["bg_card_hover"], COLORS["bg_card"])

        # 3. Chat History Scrollable Area
        chat_container = tk.Frame(self, bg=COLORS["bg_main"], padx=25)
        chat_container.pack(fill="both", expand=True, pady=(0, 10))

        self.chat_canvas = tk.Canvas(chat_container, bg=COLORS["bg_main"], highlightthickness=0)
        chat_scroll = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        self.messages_frame = tk.Frame(self.chat_canvas, bg=COLORS["bg_main"])

        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        self.canvas_win = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=chat_scroll.set)

        def on_configure(event):
            self.chat_canvas.itemconfig(self.canvas_win, width=event.width)
        self.chat_canvas.bind("<Configure>", on_configure)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        chat_scroll.pack(side="right", fill="y")

        # 4. Input Controls Toolbar
        input_toolbar = tk.Frame(self, bg=COLORS["bg_sidebar"], padx=25, pady=12, relief="solid", borderwidth=1)
        input_toolbar.pack(fill="x", side="bottom")

        # Voice Input Button (with mic icon and clear wording)
        self.btn_voice = tk.Button(
            input_toolbar,
            text=LABELS["ACTION_VOICE_INPUT"],
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["body_bold"],
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._handle_voice_input
        )
        self.btn_voice.pack(side="left", padx=(0, 10))
        add_hover_effect(self.btn_voice, COLORS["bg_card_hover"], COLORS["bg_card"])

        # Text Input Entry
        self.entry_msg = tk.Entry(
            input_toolbar,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["gold"],
            font=FONTS["body"],
            relief="solid",
            borderwidth=1
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda e: self._send_user_message())
        self.entry_msg.focus()

        # Send Button
        btn_send = tk.Button(
            input_toolbar,
            text=LABELS["ACTION_SEND_MSG"],
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._send_user_message
        )
        btn_send.pack(side="right")
        add_hover_effect(btn_send, COLORS["sapphire_hover"], COLORS["sapphire"])

    def _send_welcome_message(self):
        """Display initial assistant greeting."""
        welcome_txt = (
            "👋 **Hello! I am your ContactAI Assistant.**\n\n"
            "I operate completely **offline** inside this application, allowing you to:\n"
            "• **Add contacts:** *'Add Sundar Pichai, 9876543210, sundar@google.com, Google, Chennai'*\n"
            "• **Analyze your database:** *'Analyze my contacts'*\n"
            "• **Search seamlessly:** *'Find contacts in Bangalore'* or *'Search for TCS'*\n"
            "• **Detect duplicates:** *'Check for duplicates'*\n"
            "• **Health check:** *'Who is missing email or phone?'*\n\n"
            "Type a command below or click **🎙️ Voice Input** to speak!"
        )
        self._add_message(sender="ai", text=welcome_txt)

    def _add_message(self, sender: str, text: str):
        """Render a chat bubble."""
        bubble_row = tk.Frame(self.messages_frame, bg=COLORS["bg_main"], pady=6)
        bubble_row.pack(fill="x", expand=True)

        if sender == "user":
            # Right-aligned User Bubble
            bubble = tk.Frame(bubble_row, bg=COLORS["sapphire"], padx=14, pady=10, relief="solid", borderwidth=1)
            bubble.pack(side="right", anchor="e", padx=(60, 0))

            tk.Label(bubble, text="👤 You", bg=COLORS["sapphire"], fg=COLORS["text_white"], font=FONTS["body_bold"]).pack(anchor="w")
            tk.Label(bubble, text=text, bg=COLORS["sapphire"], fg=COLORS["text_white"], font=FONTS["body"], wraplength=520, justify="left").pack(anchor="w", pady=(2, 0))

        else:
            # Left-aligned Assistant Bubble
            bubble = tk.Frame(bubble_row, bg=COLORS["bg_card"], padx=16, pady=12, relief="solid", borderwidth=1)
            bubble.pack(side="left", anchor="w", padx=(0, 60))

            header_f = tk.Frame(bubble, bg=COLORS["bg_card"])
            header_f.pack(fill="x", pady=(0, 4))
            tk.Label(header_f, text="🤖 ContactAI Assistant", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["body_bold"]).pack(side="left")
            tk.Label(header_f, text="Offline Engine", bg=COLORS["bg_input"], fg=COLORS["text_dim"], font=FONTS["micro"], padx=6, pady=1).pack(side="right")

            tk.Label(bubble, text=text, bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body"], wraplength=540, justify="left").pack(anchor="w")

        # Scroll to bottom
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _send_user_message(self):
        """Extract user input, render user bubble, and process with assistant."""
        query = self.entry_msg.get().strip()
        if not query:
            return
        self.entry_msg.delete(0, "end")
        self._submit_prompt(query)

    def _submit_prompt(self, query: str):
        """Submit a prompt and trigger AI processing."""
        self._add_message(sender="user", text=query)

        # Process via AIAssistantService
        response = self.ai_service.process_query(query)
        self._add_message(sender="ai", text=response)

        # If an operation was executed (e.g. Add, Merge), notify parent to refresh lists
        if self.on_action_done:
            self.on_action_done()

    def _handle_voice_input(self):
        """Listen to voice input using assistant service in background thread."""
        self.btn_voice.configure(text="🔴 Listening...", bg=COLORS["danger"])

        def worker():
            success, result_text = self.ai_service.transcribe_voice()
            self.after(0, lambda: self._on_voice_finished(success, result_text))

        threading.Thread(target=worker, daemon=True).start()

    def _on_voice_finished(self, success: bool, text: str):
        """Callback when voice transcription returns."""
        self.btn_voice.configure(text=LABELS["ACTION_VOICE_INPUT"], bg=COLORS["bg_card"])
        if success and text:
            self.entry_msg.delete(0, "end")
            self.entry_msg.insert(0, text)
            self._send_user_message()
        else:
            messagebox.showinfo("Voice Recognition", text)

    def _clear_chat(self):
        """Clear chat history and re-show welcome message."""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self._send_welcome_message()

#!/usr/bin/env python3
"""
画像クリックツール GUI版 v0.15
ワークフロー名前入力、自動保存、フォルダ整理対応
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pyautogui
from PIL import Image, ImageTk
import os
from pathlib import Path
from image_clicker import ImageClicker
import threading
import time
import json
from datetime import datetime

class SingleScreenshotSelector:
    """単一範囲選択用スクリーンショットセレクター"""
    
    def __init__(self, screenshot):
        self.screenshot = screenshot
        self.selection = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        # 全画面ウィンドウを作成
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(cursor="cross")
        
        # キャンバスを作成
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # スクリーンショットを表示
        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # イベントバインド
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.cancel())
        
        # 説明テキスト
        self.canvas.create_text(
            self.screenshot.width // 2, 30,
            text="ドラッグして範囲を選択 (ESCでキャンセル)",
            fill="white", font=("Arial", 16, "bold")
        )
        self.canvas.create_text(
            self.screenshot.width // 2, 32,
            text="ドラッグして範囲を選択 (ESCでキャンセル)",
            fill="black", font=("Arial", 16, "bold")
        )
    
    def on_press(self, event):
        """マウス押下時"""
        self.start_x = event.x
        self.start_y = event.y
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )
    
    def on_drag(self, event):
        """ドラッグ中"""
        if self.rect:
            self.canvas.coords(
                self.rect,
                self.start_x, self.start_y,
                event.x, event.y
            )
    
    def on_release(self, event):
        """マウスリリース時"""
        if self.start_x and self.start_y:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            if x2 - x1 > 10 and y2 - y1 > 10:  # 最小サイズチェック
                self.selection = (x1, y1, x2, y2)
                self.root.destroy()
    
    def cancel(self):
        """キャンセル"""
        self.selection = None
        self.root.destroy()
    
    def get_selection(self):
        """選択範囲を取得"""
        self.root.wait_window()
        return self.selection


class MultiScreenshotSelector:
    """複数範囲を連続選択できるスクリーンショットセレクター"""
    
    def __init__(self, screenshot, max_selections=4):
        self.screenshot = screenshot
        self.selections = []
        self.current_selection = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.max_selections = max_selections
        
        # 色のリスト（赤、青、緑、黄色）
        self.colors = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "magenta"]
        self.current_color_index = 0
        self.rectangles = []  # 描画した矩形を保持
        
        # 全画面ウィンドウを作成
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(cursor="cross")
        
        # キャンバスを作成
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # スクリーンショットを表示
        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # イベントバインド
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.finish())
        self.root.bind("<Return>", lambda e: self.finish())
        
        # 説明テキスト
        self.update_instruction()
    
    def update_instruction(self):
        """説明テキストを更新"""
        selection_count = len(self.selections)
        color = self.colors[self.current_color_index % len(self.colors)]
        
        text = f"範囲 {selection_count + 1}/{self.max_selections} を選択 (色: {color}) | Enter: 完了 | ESC: キャンセル"
        
        # 既存のテキストを削除
        self.canvas.delete("instruction")
        
        # 新しいテキストを表示
        self.canvas.create_text(
            self.screenshot.width // 2, 30,
            text=text, fill="white", font=("Arial", 14, "bold"),
            tags="instruction"
        )
        self.canvas.create_text(
            self.screenshot.width // 2, 32,
            text=text, fill="black", font=("Arial", 14, "bold"),
            tags="instruction"
        )
    
    def on_press(self, event):
        """マウス押下時"""
        self.start_x = event.x
        self.start_y = event.y
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        color = self.colors[self.current_color_index % len(self.colors)]
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=color, width=2
        )
    
    def on_drag(self, event):
        """ドラッグ中"""
        if self.rect:
            self.canvas.coords(
                self.rect,
                self.start_x, self.start_y,
                event.x, event.y
            )
    
    def on_release(self, event):
        """マウスリリース時"""
        if self.start_x and self.start_y:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            if x2 - x1 > 10 and y2 - y1 > 10:  # 最小サイズチェック
                # 選択範囲を保存
                self.selections.append({
                    'coords': (x1, y1, x2, y2),
                    'color': self.colors[self.current_color_index % len(self.colors)]
                })
                
                # 矩形を保持（削除しない）
                self.rectangles.append(self.rect)
                self.rect = None
                
                # 次の色へ
                self.current_color_index += 1
                
                # 説明を更新
                self.update_instruction()
                
                # 最大数に達したら自動終了
                if len(self.selections) >= self.max_selections:
                    self.root.after(500, self.finish)
    
    def finish(self):
        """選択完了"""
        self.root.destroy()
    
    def get_selections(self):
        """選択範囲を取得"""
        self.root.wait_window()
        return self.selections


class WorkflowRecorder:
    """操作記録用のワークフロー管理"""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.workflow = []
        self.is_recording = False
        self.current_step = 0
        self.workflow_name = ""
        
    def start_recording(self, workflow_name=""):
        """記録開始"""
        self.workflow = []
        self.is_recording = True
        self.current_step = 0
        self.workflow_name = workflow_name or f"workflow_{int(time.time())}"
        
    def add_step(self, action_type, data):
        """ステップを追加"""
        step = {
            'step': self.current_step,
            'type': action_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.workflow.append(step)
        self.current_step += 1
        
    def stop_recording(self):
        """記録停止"""
        self.is_recording = False
        
    def save_workflow(self, filename=None):
        """ワークフローを保存"""
        if not filename:
            # 自動保存用のファイル名を生成
            workflows_dir = Path("workflows")
            workflows_dir.mkdir(exist_ok=True)
            filename = workflows_dir / f"{self.workflow_name}.json"
        
        # ワークフローメタ情報を追加
        workflow_data = {
            'name': self.workflow_name,
            'created': datetime.now().isoformat(),
            'steps_count': len(self.workflow),
            'workflow': self.workflow
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, ensure_ascii=False, indent=2)
        
        return filename
            
    def load_workflow(self, filename):
        """ワークフローを読み込み"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 新形式の場合
        if 'workflow' in data:
            self.workflow_name = data.get('name', 'loaded_workflow')
            self.workflow = data['workflow']
        else:
            # 旧形式の場合
            self.workflow = data
            self.workflow_name = Path(filename).stem


class ImageClickerGUIv015:
    """メインGUIアプリケーション v0.15"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像クリックツール v0.15")
        self.root.geometry("900x750")
        
        # ImageClickerインスタンス
        self.clicker = ImageClicker(confidence=0.8)
        
        # 画像リスト
        self.image_files = []
        
        # ワークフローレコーダー
        self.recorder = WorkflowRecorder(self)
        
        # ディレクトリを作成
        self.setup_directories()
        
        # カスタムスタイル
        self.setup_styles()
        self.setup_ui()
        self.refresh_image_list()
    
    def setup_directories(self):
        """ディレクトリ構造をセットアップ"""
        # imagesディレクトリ
        self.clicker.images_dir.mkdir(exist_ok=True)
        
        # workflowsディレクトリ
        self.workflows_dir = Path("workflows")
        self.workflows_dir.mkdir(exist_ok=True)
    
    def setup_styles(self):
        """カスタムスタイル設定"""
        style = ttk.Style()
        
        # タブの色設定
        style.configure('Basic.TNotebook.Tab', background='lightblue', padding=[20, 10])
        style.configure('Multi.TNotebook.Tab', background='lightgreen', padding=[20, 10])
        style.configure('Workflow.TNotebook.Tab', background='lightyellow', padding=[20, 10])
        
        # 選択時の色
        style.map('Basic.TNotebook.Tab', background=[('selected', 'blue')])
        style.map('Multi.TNotebook.Tab', background=[('selected', 'green')])
        style.map('Workflow.TNotebook.Tab', background=[('selected', 'orange')])
    
    def setup_ui(self):
        """UI構築"""
        # タブコントロール
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 基本タブ（青色）
        basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(basic_tab, text="🔵 基本機能")
        self.setup_basic_tab(basic_tab)
        
        # 複数選択タブ（緑色）
        multi_tab = ttk.Frame(self.notebook)
        self.notebook.add(multi_tab, text="🟢 複数選択")
        self.setup_multi_tab(multi_tab)
        
        # ワークフロータブ（黄色）
        workflow_tab = ttk.Frame(self.notebook)
        self.notebook.add(workflow_tab, text="🟡 ワークフロー記録")
        self.setup_workflow_tab(workflow_tab)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了 - 🔵基本機能でスクショから始めましょう！")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
    
    def setup_basic_tab(self, parent):
        """基本タブのセットアップ"""
        # 説明文
        info_frame = ttk.LabelFrame(parent, text="📋 基本機能の使い方", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        info_text.pack(fill=tk.X)
        info_text.insert(tk.END, "【STEP1】 スクショボタンをクリック\n")
        info_text.insert(tk.END, "【STEP2】 3秒後に撮影される\n")
        info_text.insert(tk.END, "【STEP3】 ドラッグで範囲を赤枠で選択\n")
        info_text.insert(tk.END, "【STEP4】 保存した画像を選択してクリックボタン → 自動クリック！")
        info_text.config(state=tk.DISABLED)
        
        # スクリーンショット機能
        screenshot_frame = ttk.LabelFrame(parent, text="📷 スクリーンショット撮影", padding="10")
        screenshot_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            screenshot_frame,
            text="📷 スクリーンショットを撮る",
            command=self.take_screenshot,
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(screenshot_frame, text="※ 3秒後に撮影 → ドラッグで赤枠選択", foreground="red").pack(side=tk.LEFT, padx=10)
        
        # 画像リスト
        list_frame = ttk.LabelFrame(parent, text="💾 保存済み画像", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # リストボックスとスクロールバー
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=8)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # リスト操作ボタン
        list_buttons = ttk.Frame(list_frame)
        list_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(
            list_buttons,
            text="🔄 更新",
            command=self.refresh_image_list,
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            list_buttons,
            text="🗑️ 削除",
            command=self.delete_image,
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        # クリック機能
        click_frame = ttk.LabelFrame(parent, text="🖱️ クリック実行", padding="10")
        click_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 信頼度設定
        ttk.Label(click_frame, text="信頼度:").grid(row=0, column=0, padx=5)
        
        self.confidence_var = tk.DoubleVar(value=0.8)
        confidence_scale = ttk.Scale(
            click_frame,
            from_=0.5,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.confidence_var,
            length=200
        )
        confidence_scale.grid(row=0, column=1, padx=5)
        
        self.confidence_label = ttk.Label(click_frame, text="0.80")
        self.confidence_label.grid(row=0, column=2, padx=5)
        
        confidence_scale.configure(command=self.update_confidence_label)
        
        # クリックボタン
        click_button = ttk.Button(
            click_frame,
            text="🖱️ 選択した画像をクリック",
            command=self.click_selected_image,
            width=30
        )
        click_button.grid(row=1, column=0, columnspan=3, pady=10)
    
    def setup_multi_tab(self, parent):
        """複数選択タブのセットアップ"""
        # 説明文
        info_frame = ttk.LabelFrame(parent, text="📋 複数選択の使い方", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = tk.Text(info_frame, height=5, wrap=tk.WORD)
        info_text.pack(fill=tk.X)
        info_text.insert(tk.END, "【STEP1】 選択数とベース名を設定\n")
        info_text.insert(tk.END, "【STEP2】 複数範囲選択ボタンをクリック\n") 
        info_text.insert(tk.END, "【STEP3】 1個目→赤枠、2個目→青枠、3個目→緑枠...と連続選択\n")
        info_text.insert(tk.END, "【STEP4】 Enterキーで完了\n")
        info_text.insert(tk.END, "【結果】 button_01.png、button_02.png...と連番で自動保存")
        info_text.config(state=tk.DISABLED)
        
        # 設定フレーム
        settings_frame = ttk.LabelFrame(parent, text="⚙️ 複数選択設定", padding="10")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="選択数:").grid(row=0, column=0, padx=5)
        
        self.multi_count_var = tk.IntVar(value=3)
        multi_spinbox = ttk.Spinbox(
            settings_frame,
            from_=2,
            to=8,
            textvariable=self.multi_count_var,
            width=10
        )
        multi_spinbox.grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="ベース名:").grid(row=0, column=2, padx=5)
        
        self.base_name_var = tk.StringVar(value="capture")
        base_name_entry = ttk.Entry(settings_frame, textvariable=self.base_name_var, width=20)
        base_name_entry.grid(row=0, column=3, padx=5)
        
        # 実行ボタン
        ttk.Button(
            settings_frame,
            text="📷 複数範囲を選択して保存",
            command=self.take_multiple_screenshots,
            width=30
        ).grid(row=1, column=0, columnspan=4, pady=10)
        
        # 結果表示
        result_frame = ttk.LabelFrame(parent, text="📋 選択結果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.multi_result_text = scrolledtext.ScrolledText(result_frame, height=10, width=50)
        self.multi_result_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_workflow_tab(self, parent):
        """ワークフロータブのセットアップ"""
        # 説明文
        info_frame = ttk.LabelFrame(parent, text="📋 ワークフロー記録とは？", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        info_text.pack(fill=tk.X)
        info_text.insert(tk.END, "【概要】 操作手順を記録して自動化できます\n")
        info_text.insert(tk.END, "【簡単】 スクショを撮った順番に自動でクリックします\n")
        info_text.insert(tk.END, "【例】Google検索：検索ボックス→待機→検索ボタンの順で撮影\n")
        info_text.insert(tk.END, "【実行】 記録した順番で自動クリック！")
        info_text.config(state=tk.DISABLED)
        
        # 操作手順
        steps_frame = ttk.LabelFrame(parent, text="📝 操作手順（超シンプル）", padding="10")
        steps_frame.pack(fill=tk.X, padx=5, pady=5)
        
        steps_text = tk.Text(steps_frame, height=4, wrap=tk.WORD, background="#ffffcc")
        steps_text.pack(fill=tk.X)
        steps_text.insert(tk.END, "【STEP1】 ワークフロー名を入力して記録開始\n")
        steps_text.insert(tk.END, "【STEP2】 📸スクショ＋クリックで1つ目の画像（自動でクリック操作も追加）\n")
        steps_text.insert(tk.END, "【STEP3】 必要に応じて⏸️待機を追加、📸スクショ＋クリックで2つ目...\n")
        steps_text.insert(tk.END, "【STEP4】 記録停止で自動保存→▶️実行で撮った順番に自動クリック！")
        steps_text.config(state=tk.DISABLED)
        
        # ワークフロー名前設定
        name_frame = ttk.LabelFrame(parent, text="📝 ワークフロー名前", padding="10")
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="ワークフロー名:").pack(side=tk.LEFT, padx=5)
        
        self.workflow_name_var = tk.StringVar(value="")
        self.workflow_name_entry = ttk.Entry(name_frame, textvariable=self.workflow_name_var, width=30)
        self.workflow_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(name_frame, text="※空白の場合は自動命名", foreground="gray").pack(side=tk.LEFT, padx=10)
        
        # コントロールフレーム
        control_frame = ttk.LabelFrame(parent, text="🎬 ワークフロー記録", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.record_button = ttk.Button(
            control_frame,
            text="⏺️ 記録開始",
            command=self.toggle_recording,
            width=15
        )
        self.record_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(
            control_frame,
            text="📸 スクショ＋クリック",
            command=self.workflow_screenshot_and_click,
            width=18
        ).grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="待機時間(秒):").grid(row=1, column=0, padx=5, pady=5)
        
        self.wait_time_var = tk.DoubleVar(value=2.0)
        wait_spinbox = ttk.Spinbox(
            control_frame,
            from_=0.5,
            to=10.0,
            increment=0.5,
            textvariable=self.wait_time_var,
            width=10
        )
        wait_spinbox.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="⏸️ 待機追加",
            command=self.add_workflow_wait,
            width=15
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # ワークフロー管理
        management_frame = ttk.LabelFrame(parent, text="💾 ワークフロー管理", padding="10")
        management_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 保存済みワークフローリスト
        saved_frame = ttk.Frame(management_frame)
        saved_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(saved_frame, text="保存済み:").pack(side=tk.LEFT)
        
        self.saved_workflows_var = tk.StringVar()
        self.saved_workflows_combo = ttk.Combobox(saved_frame, textvariable=self.saved_workflows_var, width=30, state="readonly")
        self.saved_workflows_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(saved_frame, text="📁 読込", command=self.load_saved_workflow, width=10).pack(side=tk.LEFT, padx=2)
        
        # 管理ボタン
        mgmt_buttons = ttk.Frame(management_frame)
        mgmt_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(mgmt_buttons, text="🔄 更新", command=self.refresh_saved_workflows, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(mgmt_buttons, text="📥 外部読込", command=self.load_external_workflow, width=12).pack(side=tk.LEFT, padx=2)
        
        # ワークフロー表示
        workflow_frame = ttk.LabelFrame(parent, text="📋 記録されたワークフロー", padding="10")
        workflow_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.workflow_text = scrolledtext.ScrolledText(workflow_frame, height=8, width=50)
        self.workflow_text.pack(fill=tk.BOTH, expand=True)
        
        # 実行ボタン
        execute_frame = ttk.Frame(parent)
        execute_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            execute_frame,
            text="▶️ ワークフロー実行",
            command=self.execute_workflow,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # 初期化
        self.refresh_saved_workflows()
    
    def update_confidence_label(self, value):
        """信頼度ラベル更新"""
        self.confidence_label.config(text=f"{float(value):.2f}")
    
    def take_screenshot(self):
        """単一スクリーンショット撮影"""
        self.status_var.set("3秒後にスクリーンショットを撮影します...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        time.sleep(3)
        
        # スクリーンショット撮影
        screenshot = pyautogui.screenshot()
        
        # 範囲選択（単一用）
        selector = SingleScreenshotSelector(screenshot)
        selection = selector.get_selection()
        
        # 復元
        self.root.deiconify()
        
        if selection:
            # 選択範囲を切り出し
            x1, y1, x2, y2 = selection
            cropped = screenshot.crop((x1, y1, x2, y2))
            
            # ファイル名入力ダイアログ
            dialog = tk.Toplevel(self.root)
            dialog.title("保存")
            dialog.geometry("300x100")
            
            ttk.Label(dialog, text="ファイル名:").pack(pady=5)
            
            name_var = tk.StringVar(value=f"image_{int(time.time())}")
            entry = ttk.Entry(dialog, textvariable=name_var, width=30)
            entry.pack(pady=5)
            entry.select_range(0, tk.END)
            entry.focus()
            
            def save():
                filename = name_var.get()
                if filename:
                    if not filename.endswith('.png'):
                        filename += '.png'
                    
                    filepath = self.clicker.images_dir / filename
                    cropped.save(filepath)
                    
                    self.status_var.set(f"保存しました: {filename}")
                    self.refresh_image_list()
                    dialog.destroy()
            
            ttk.Button(dialog, text="保存", command=save).pack(pady=5)
            
            entry.bind('<Return>', lambda e: save())
        else:
            self.status_var.set("キャンセルされました")
    
    def workflow_screenshot_and_click(self):
        """ワークフロー用スクリーンショット撮影＋自動でクリック操作追加"""
        if not self.recorder.is_recording:
            messagebox.showwarning("警告", "先に「⏺️ 記録開始」をクリックしてください")
            return
        
        self.status_var.set("3秒後にスクリーンショットを撮影します...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        time.sleep(3)
        
        # スクリーンショット撮影
        screenshot = pyautogui.screenshot()
        
        # 範囲選択
        selector = SingleScreenshotSelector(screenshot)
        selection = selector.get_selection()
        
        # 復元
        self.root.deiconify()
        
        if selection:
            x1, y1, x2, y2 = selection
            cropped = screenshot.crop((x1, y1, x2, y2))
            
            # ファイル名生成
            timestamp = int(time.time())
            filename = f"workflow_{self.recorder.current_step}_{timestamp}.png"
            filepath = self.clicker.images_dir / filename
            
            # 保存
            cropped.save(filepath)
            
            # ワークフローに追加（スクリーンショット）
            self.recorder.add_step('screenshot', {
                'filename': filename,
                'coords': (x1, y1, x2, y2)
            })
            
            # 自動的にクリック操作も追加
            self.recorder.add_step('click', {
                'image': filename,
                'confidence': self.confidence_var.get()
            })
            
            # 表示更新
            self.workflow_text.insert(tk.END, f"[{self.recorder.current_step-2}] 📸 撮影: {filename}\n")
            self.workflow_text.insert(tk.END, f"[{self.recorder.current_step-1}] 🖱️ クリック: {filename}\n")
            
            self.status_var.set(f"✅ ワークフローに追加: 撮影→クリック {filename}")
    
    def take_multiple_screenshots(self):
        """複数範囲のスクリーンショット撮影"""
        self.status_var.set("3秒後に複数範囲選択を開始します...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        time.sleep(3)
        
        # スクリーンショット撮影
        screenshot = pyautogui.screenshot()
        
        # 複数範囲選択
        selector = MultiScreenshotSelector(screenshot, self.multi_count_var.get())
        selections = selector.get_selections()
        
        # 復元
        self.root.deiconify()
        
        if selections:
            base_name = self.base_name_var.get()
            timestamp = int(time.time())
            
            self.multi_result_text.delete(1.0, tk.END)
            self.multi_result_text.insert(tk.END, f"✅ 選択した範囲: {len(selections)}個\n\n")
            
            for i, selection in enumerate(selections, 1):
                # 選択範囲を切り出し
                x1, y1, x2, y2 = selection['coords']
                color = selection['color']
                cropped = screenshot.crop((x1, y1, x2, y2))
                
                # ファイル名生成
                filename = f"{base_name}_{timestamp}_{i:02d}.png"
                filepath = self.clicker.images_dir / filename
                
                # 保存
                cropped.save(filepath)
                
                # 結果表示
                result_text = f"{i}. {filename} (枠色: {color})\n"
                result_text += f"   範囲: ({x1}, {y1}) - ({x2}, {y2})\n"
                result_text += f"   サイズ: {x2-x1} x {y2-y1}\n\n"
                self.multi_result_text.insert(tk.END, result_text)
            
            self.status_var.set(f"✅ {len(selections)}個の画像を保存しました")
            self.refresh_image_list()
        else:
            self.status_var.set("選択がキャンセルされました")
    
    def toggle_recording(self):
        """記録の開始/停止"""
        if not self.recorder.is_recording:
            # ワークフロー名を取得（空白の場合はデフォルト名）
            workflow_name = self.workflow_name_var.get().strip()
            if not workflow_name:
                workflow_name = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.recorder.start_recording(workflow_name)
            self.record_button.config(text="⏹️ 記録停止")
            self.workflow_text.delete(1.0, tk.END)
            self.workflow_text.insert(tk.END, f"🔴 記録開始... ワークフロー名: {workflow_name}\n")
            self.workflow_text.insert(tk.END, "次は「📸 スクショ＋クリック」をクリックしてください\n")
            self.status_var.set(f"🔴 ワークフロー記録中（{workflow_name}）... 📸スクショ＋クリックをクリックしてください")
        else:
            self.recorder.stop_recording()
            self.record_button.config(text="⏺️ 記録開始")
            
            # 自動保存
            if self.recorder.workflow:
                saved_file = self.recorder.save_workflow()
                self.status_var.set(f"記録停止＆自動保存完了: {saved_file.name}")
                self.refresh_saved_workflows()
            else:
                self.status_var.set("記録を停止しました（保存なし）")
            
            self.update_workflow_display()
    
    def add_workflow_wait(self):
        """ワークフローに待機を追加"""
        if not self.recorder.is_recording:
            messagebox.showwarning("警告", "先に「⏺️ 記録開始」をクリックしてください")
            return
        
        wait_time = self.wait_time_var.get()
        
        # ワークフローに追加
        self.recorder.add_step('wait', {
            'duration': wait_time
        })
        
        self.workflow_text.insert(tk.END, f"[{self.recorder.current_step-1}] ⏸️ 待機: {wait_time}秒\n")
        self.status_var.set(f"✅ ワークフローに追加: 待機 {wait_time}秒")
    
    def refresh_saved_workflows(self):
        """保存済みワークフローリストを更新"""
        workflow_files = list(self.workflows_dir.glob("*.json"))
        workflow_names = [f.stem for f in sorted(workflow_files)]
        
        self.saved_workflows_combo['values'] = workflow_names
        if workflow_names and not self.saved_workflows_var.get():
            self.saved_workflows_combo.current(0)
    
    def load_saved_workflow(self):
        """保存済みワークフローを読み込み"""
        workflow_name = self.saved_workflows_var.get()
        if not workflow_name:
            messagebox.showwarning("警告", "ワークフローを選択してください")
            return
        
        workflow_file = self.workflows_dir / f"{workflow_name}.json"
        if workflow_file.exists():
            self.recorder.load_workflow(workflow_file)
            self.workflow_name_var.set(self.recorder.workflow_name)
            self.update_workflow_display()
            self.status_var.set(f"✅ ワークフローを読み込みました: {workflow_name}")
        else:
            messagebox.showerror("エラー", f"ファイルが見つかりません: {workflow_file}")
    
    def load_external_workflow(self):
        """外部ワークフローを読み込み"""
        filename = filedialog.askopenfilename(
            title="ワークフローファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self.recorder.load_workflow(filename)
            self.workflow_name_var.set(self.recorder.workflow_name)
            self.update_workflow_display()
            self.refresh_saved_workflows()
            messagebox.showinfo("成功", f"ワークフローを読み込みました: {Path(filename).name}")
    
    def update_workflow_display(self):
        """ワークフロー表示を更新"""
        self.workflow_text.delete(1.0, tk.END)
        if not self.recorder.workflow:
            self.workflow_text.insert(tk.END, "まだワークフローが記録されていません\n")
            return
            
        self.workflow_text.insert(tk.END, f"ワークフロー名: {self.recorder.workflow_name}\n")
        self.workflow_text.insert(tk.END, f"ステップ数: {len(self.recorder.workflow)}\n\n")
            
        for step in self.recorder.workflow:
            if step['type'] == 'screenshot':
                text = f"[{step['step']}] 📸 撮影: {step['data']['filename']}\n"
            elif step['type'] == 'click':
                text = f"[{step['step']}] 🖱️ クリック: {step['data']['image']}\n"
            elif step['type'] == 'wait':
                text = f"[{step['step']}] ⏸️ 待機: {step['data']['duration']}秒\n"
            else:
                text = f"[{step['step']}] {step['type']}\n"
            
            self.workflow_text.insert(tk.END, text)
    
    def execute_workflow(self):
        """ワークフローを実行"""
        if not self.recorder.workflow:
            messagebox.showwarning("警告", "実行するワークフローがありません")
            return
        
        result = messagebox.askyesno("確認", f"ワークフロー「{self.recorder.workflow_name}」\n（{len(self.recorder.workflow)}ステップ）を実行しますか？\n\nウィンドウが最小化され、自動操作が始まります。")
        if not result:
            return
        
        self.status_var.set(f"🚀 ワークフロー「{self.recorder.workflow_name}」実行中...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        
        def execute_task():
            for i, step in enumerate(self.recorder.workflow):
                self.status_var.set(f"🚀 ステップ {i+1}/{len(self.recorder.workflow)} を実行中...")
                
                if step['type'] == 'screenshot':
                    # スクリーンショットはスキップ（実行時には不要）
                    continue
                    
                elif step['type'] == 'click':
                    # 画像をクリック
                    self.clicker.confidence = step['data']['confidence']
                    success = self.clicker.click_image(step['data']['image'], timeout=10)
                    if not success:
                        print(f"❌ クリック失敗: {step['data']['image']}")
                    
                elif step['type'] == 'wait':
                    # 待機
                    time.sleep(step['data']['duration'])
            
            # 完了
            self.root.deiconify()
            self.status_var.set(f"✅ ワークフロー「{self.recorder.workflow_name}」実行完了！")
        
        # 別スレッドで実行
        thread = threading.Thread(target=execute_task)
        thread.daemon = True
        thread.start()
    
    def refresh_image_list(self):
        """画像リスト更新"""
        self.listbox.delete(0, tk.END)
        
        if self.clicker.images_dir.exists():
            self.image_files = list(self.clicker.images_dir.glob("*.png"))
            self.image_files.extend(list(self.clicker.images_dir.glob("*.jpg")))
            self.image_files.extend(list(self.clicker.images_dir.glob("*.jpeg")))
            
            for image_file in sorted(self.image_files):
                self.listbox.insert(tk.END, image_file.name)
        
        if not self.recorder.is_recording:
            self.status_var.set(f"📁 {len(self.image_files)}個の画像")
    
    def delete_image(self):
        """選択した画像を削除"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            image_file = self.image_files[index]
            
            if messagebox.askyesno("確認", f"{image_file.name}を削除しますか？"):
                try:
                    image_file.unlink()
                    self.refresh_image_list()
                    self.status_var.set(f"🗑️ 削除しました: {image_file.name}")
                except Exception as e:
                    messagebox.showerror("エラー", f"削除に失敗しました: {e}")
    
    def click_selected_image(self):
        """選択した画像をクリック"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "画像を選択してください")
            return
        
        index = selection[0]
        image_name = self.listbox.get(index)
        
        # 設定を更新
        self.clicker.confidence = self.confidence_var.get()
        
        self.status_var.set(f"🔍 画像を検索中: {image_name}")
        self.root.update()
        
        # 別スレッドで実行
        def click_task():
            # 少し待機
            time.sleep(0.5)
            
            success = self.clicker.click_image(image_name, timeout=10)
            
            if success:
                self.status_var.set(f"✅ クリック成功: {image_name}")
            else:
                self.status_var.set(f"❌ 画像が見つかりません: {image_name}")
        
        # 最小化してクリック実行
        self.root.iconify()
        thread = threading.Thread(target=click_task)
        thread.daemon = True
        thread.start()
        
        # 完了後に復元
        self.root.after(2000, self.root.deiconify)
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageClickerGUIv015()
    app.run()
#!/usr/bin/env python3
"""
画像クリックツール GUI版 v2
複数範囲選択、ワークフロー記録機能付き
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
        
    def start_recording(self):
        """記録開始"""
        self.workflow = []
        self.is_recording = True
        self.current_step = 0
        
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
        
    def save_workflow(self, filename):
        """ワークフローを保存"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.workflow, f, ensure_ascii=False, indent=2)
            
    def load_workflow(self, filename):
        """ワークフローを読み込み"""
        with open(filename, 'r', encoding='utf-8') as f:
            self.workflow = json.load(f)


class ImageClickerGUIv2:
    """メインGUIアプリケーション v2"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像クリックツール v0.11")
        self.root.geometry("800x650")
        
        # ImageClickerインスタンス
        self.clicker = ImageClicker(confidence=0.8)
        
        # 画像リスト
        self.image_files = []
        
        # ワークフローレコーダー
        self.recorder = WorkflowRecorder(self)
        
        self.setup_ui()
        self.refresh_image_list()
    
    def setup_ui(self):
        """UI構築"""
        # タブコントロール
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 基本タブ
        basic_tab = ttk.Frame(notebook)
        notebook.add(basic_tab, text="基本機能")
        self.setup_basic_tab(basic_tab)
        
        # 複数選択タブ
        multi_tab = ttk.Frame(notebook)
        notebook.add(multi_tab, text="複数選択")
        self.setup_multi_tab(multi_tab)
        
        # ワークフロータブ
        workflow_tab = ttk.Frame(notebook)
        notebook.add(workflow_tab, text="ワークフロー記録")
        self.setup_workflow_tab(workflow_tab)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
    
    def setup_basic_tab(self, parent):
        """基本タブのセットアップ"""
        # スクリーンショット機能
        screenshot_frame = ttk.LabelFrame(parent, text="スクリーンショット", padding="10")
        screenshot_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            screenshot_frame,
            text="📷 スクリーンショットを撮る",
            command=self.take_screenshot,
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(screenshot_frame, text="※ 3秒後に撮影されます").pack(side=tk.LEFT, padx=10)
        
        # 画像リスト
        list_frame = ttk.LabelFrame(parent, text="保存済み画像", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # リストボックスとスクロールバー
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
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
        click_frame = ttk.LabelFrame(parent, text="クリック実行", padding="10")
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
        ttk.Button(
            click_frame,
            text="🖱️ 選択した画像をクリック",
            command=self.click_selected_image,
            width=30
        ).grid(row=1, column=0, columnspan=3, pady=10)
    
    def setup_multi_tab(self, parent):
        """複数選択タブのセットアップ"""
        # 設定フレーム
        settings_frame = ttk.LabelFrame(parent, text="複数選択設定", padding="10")
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
        result_frame = ttk.LabelFrame(parent, text="選択結果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.multi_result_text = scrolledtext.ScrolledText(result_frame, height=10, width=50)
        self.multi_result_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_workflow_tab(self, parent):
        """ワークフロータブのセットアップ"""
        # コントロールフレーム
        control_frame = ttk.LabelFrame(parent, text="ワークフロー記録", padding="10")
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
            text="📸 スクショ追加",
            command=self.add_workflow_screenshot,
            width=15
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            control_frame,
            text="🖱️ クリック追加",
            command=self.add_workflow_click,
            width=15
        ).grid(row=0, column=2, padx=5)
        
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
        
        # ワークフロー表示
        workflow_frame = ttk.LabelFrame(parent, text="記録されたワークフロー", padding="10")
        workflow_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.workflow_text = scrolledtext.ScrolledText(workflow_frame, height=10, width=50)
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
        
        ttk.Button(
            execute_frame,
            text="💾 保存",
            command=self.save_workflow,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            execute_frame,
            text="📁 読込",
            command=self.load_workflow,
            width=10
        ).pack(side=tk.LEFT, padx=5)
    
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
        
        # 範囲選択
        from gui_app import ScreenshotSelector
        selector = ScreenshotSelector(screenshot)
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
            self.multi_result_text.insert(tk.END, f"選択した範囲: {len(selections)}個\n\n")
            
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
                result_text = f"{i}. {filename} (色: {color})\n"
                result_text += f"   範囲: ({x1}, {y1}) - ({x2}, {y2})\n"
                result_text += f"   サイズ: {x2-x1} x {y2-y1}\n\n"
                self.multi_result_text.insert(tk.END, result_text)
            
            self.status_var.set(f"{len(selections)}個の画像を保存しました")
            self.refresh_image_list()
        else:
            self.status_var.set("選択がキャンセルされました")
    
    def toggle_recording(self):
        """記録の開始/停止"""
        if not self.recorder.is_recording:
            self.recorder.start_recording()
            self.record_button.config(text="⏹️ 記録停止")
            self.workflow_text.delete(1.0, tk.END)
            self.workflow_text.insert(tk.END, "記録開始...\n")
            self.status_var.set("ワークフロー記録中...")
        else:
            self.recorder.stop_recording()
            self.record_button.config(text="⏺️ 記録開始")
            self.status_var.set("記録を停止しました")
            self.update_workflow_display()
    
    def add_workflow_screenshot(self):
        """ワークフローにスクリーンショットを追加"""
        if not self.recorder.is_recording:
            messagebox.showwarning("警告", "先に記録を開始してください")
            return
        
        self.status_var.set("3秒後にスクリーンショットを撮影します...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        time.sleep(3)
        
        # スクリーンショット撮影
        screenshot = pyautogui.screenshot()
        
        # 範囲選択
        from gui_app import ScreenshotSelector
        selector = ScreenshotSelector(screenshot)
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
            
            # ワークフローに追加
            self.recorder.add_step('screenshot', {
                'filename': filename,
                'coords': (x1, y1, x2, y2)
            })
            
            self.workflow_text.insert(tk.END, f"[{self.recorder.current_step-1}] スクリーンショット: {filename}\n")
            self.refresh_image_list()
    
    def add_workflow_click(self):
        """ワークフローにクリック操作を追加"""
        if not self.recorder.is_recording:
            messagebox.showwarning("警告", "先に記録を開始してください")
            return
        
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "クリックする画像を選択してください")
            return
        
        image_name = self.listbox.get(selection[0])
        
        # ワークフローに追加
        self.recorder.add_step('click', {
            'image': image_name,
            'confidence': self.confidence_var.get()
        })
        
        self.workflow_text.insert(tk.END, f"[{self.recorder.current_step-1}] クリック: {image_name}\n")
    
    def add_workflow_wait(self):
        """ワークフローに待機を追加"""
        if not self.recorder.is_recording:
            messagebox.showwarning("警告", "先に記録を開始してください")
            return
        
        wait_time = self.wait_time_var.get()
        
        # ワークフローに追加
        self.recorder.add_step('wait', {
            'duration': wait_time
        })
        
        self.workflow_text.insert(tk.END, f"[{self.recorder.current_step-1}] 待機: {wait_time}秒\n")
    
    def update_workflow_display(self):
        """ワークフロー表示を更新"""
        self.workflow_text.delete(1.0, tk.END)
        for step in self.recorder.workflow:
            if step['type'] == 'screenshot':
                text = f"[{step['step']}] スクリーンショット: {step['data']['filename']}\n"
            elif step['type'] == 'click':
                text = f"[{step['step']}] クリック: {step['data']['image']}\n"
            elif step['type'] == 'wait':
                text = f"[{step['step']}] 待機: {step['data']['duration']}秒\n"
            else:
                text = f"[{step['step']}] {step['type']}\n"
            
            self.workflow_text.insert(tk.END, text)
    
    def execute_workflow(self):
        """ワークフローを実行"""
        if not self.recorder.workflow:
            messagebox.showwarning("警告", "実行するワークフローがありません")
            return
        
        self.status_var.set("ワークフロー実行中...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        
        def execute_task():
            for step in self.recorder.workflow:
                if step['type'] == 'screenshot':
                    # スクリーンショットは実行時に再撮影
                    time.sleep(1)
                    screenshot = pyautogui.screenshot()
                    filename = f"exec_{step['data']['filename']}"
                    filepath = self.clicker.images_dir / filename
                    screenshot.save(filepath)
                    
                elif step['type'] == 'click':
                    # 画像をクリック
                    self.clicker.confidence = step['data']['confidence']
                    success = self.clicker.click_image(step['data']['image'], timeout=10)
                    if not success:
                        print(f"クリック失敗: {step['data']['image']}")
                    
                elif step['type'] == 'wait':
                    # 待機
                    time.sleep(step['data']['duration'])
            
            # 完了
            self.root.deiconify()
            self.status_var.set("ワークフロー実行完了")
        
        # 別スレッドで実行
        thread = threading.Thread(target=execute_task)
        thread.daemon = True
        thread.start()
    
    def save_workflow(self):
        """ワークフローを保存"""
        if not self.recorder.workflow:
            messagebox.showwarning("警告", "保存するワークフローがありません")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self.recorder.save_workflow(filename)
            messagebox.showinfo("成功", f"ワークフローを保存しました: {filename}")
    
    def load_workflow(self):
        """ワークフローを読み込み"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self.recorder.load_workflow(filename)
            self.update_workflow_display()
            messagebox.showinfo("成功", f"ワークフローを読み込みました: {filename}")
    
    def refresh_image_list(self):
        """画像リスト更新"""
        self.listbox.delete(0, tk.END)
        
        if self.clicker.images_dir.exists():
            self.image_files = list(self.clicker.images_dir.glob("*.png"))
            self.image_files.extend(list(self.clicker.images_dir.glob("*.jpg")))
            self.image_files.extend(list(self.clicker.images_dir.glob("*.jpeg")))
            
            for image_file in sorted(self.image_files):
                self.listbox.insert(tk.END, image_file.name)
        
        self.status_var.set(f"{len(self.image_files)}個の画像")
    
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
                    self.status_var.set(f"削除しました: {image_file.name}")
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
        
        self.status_var.set(f"画像を検索中: {image_name}")
        self.root.update()
        
        # 別スレッドで実行
        def click_task():
            # 少し待機
            time.sleep(0.5)
            
            success = self.clicker.click_image(image_name, timeout=10)
            
            if success:
                self.status_var.set(f"クリック成功: {image_name}")
            else:
                self.status_var.set(f"画像が見つかりません: {image_name}")
        
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
    app = ImageClickerGUIv2()
    app.run()
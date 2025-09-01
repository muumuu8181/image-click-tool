#!/usr/bin/env python3
"""
画像クリックツール GUI版
スクリーンショット撮影、範囲選択、保存、クリック機能を提供
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
from PIL import Image, ImageTk
import os
from pathlib import Path
from image_clicker import ImageClicker
import threading
import time

class ScreenshotSelector:
    """スクリーンショットの範囲選択ウィンドウ"""
    
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
            screenshot.width // 2, 30,
            text="ドラッグして範囲を選択 (ESCでキャンセル)",
            fill="white", font=("Arial", 16, "bold")
        )
        self.canvas.create_text(
            screenshot.width // 2, 32,
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


class ImageClickerGUI:
    """メインGUIアプリケーション"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像クリックツール")
        self.root.geometry("600x500")
        
        # ImageClickerインスタンス
        self.clicker = ImageClicker(confidence=0.8)
        
        # 画像リスト
        self.image_files = []
        
        self.setup_ui()
        self.refresh_image_list()
    
    def setup_ui(self):
        """UI構築"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # スクリーンショット機能
        screenshot_frame = ttk.LabelFrame(main_frame, text="スクリーンショット", padding="10")
        screenshot_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(
            screenshot_frame,
            text="📷 スクリーンショットを撮る",
            command=self.take_screenshot,
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(screenshot_frame, text="※ 3秒後に撮影されます").pack(side=tk.LEFT, padx=10)
        
        # 画像リスト
        list_frame = ttk.LabelFrame(main_frame, text="保存済み画像", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
        click_frame = ttk.LabelFrame(main_frame, text="クリック実行", padding="10")
        click_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
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
        
        # タイムアウト設定
        ttk.Label(click_frame, text="タイムアウト(秒):").grid(row=1, column=0, padx=5, pady=5)
        
        self.timeout_var = tk.IntVar(value=10)
        timeout_spinbox = ttk.Spinbox(
            click_frame,
            from_=1,
            to=60,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # クリックボタン
        ttk.Button(
            click_frame,
            text="🖱️ 選択した画像をクリック",
            command=self.click_selected_image,
            width=30
        ).grid(row=2, column=0, columnspan=3, pady=10)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # ウィンドウリサイズ設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def update_confidence_label(self, value):
        """信頼度ラベル更新"""
        self.confidence_label.config(text=f"{float(value):.2f}")
    
    def take_screenshot(self):
        """スクリーンショット撮影"""
        self.status_var.set("3秒後にスクリーンショットを撮影します...")
        self.root.update()
        
        # 最小化
        self.root.iconify()
        time.sleep(3)
        
        # スクリーンショット撮影
        screenshot = pyautogui.screenshot()
        
        # 範囲選択
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
        timeout = self.timeout_var.get()
        
        self.status_var.set(f"画像を検索中: {image_name}")
        self.root.update()
        
        # 別スレッドで実行
        def click_task():
            # 少し待機（ウィンドウを最小化する時間を与える）
            time.sleep(0.5)
            
            success = self.clicker.click_image(image_name, timeout=timeout)
            
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
    app = ImageClickerGUI()
    app.run()
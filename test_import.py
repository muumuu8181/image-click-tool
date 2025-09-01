#!/usr/bin/env python3
"""
動作確認用のテストスクリプト
"""

print("=== 画像クリックツール 動作確認 ===")

try:
    print("1. 基本モジュールのインポートテスト...")
    import os
    import sys
    import time
    from pathlib import Path
    print("✓ 基本モジュール: OK")
    
    print("2. ImageClickerクラスのインポートテスト...")
    # pyautoguiを直接インポートしないバージョンでテスト
    from image_clicker import ImageClicker
    print("✗ pyautoguiが必要です (WSL2環境ではX11設定が必要)")
    
except ImportError as e:
    print(f"✗ インポートエラー: {e}")
except Exception as e:
    print(f"✗ 予期しないエラー: {e}")

print("\n=== 使用方法 ===")
print("1. imagesフォルダに対象画像を配置")
print("2. 実行コマンド:")
print("   python3 image_clicker.py <画像ファイル名>")
print("   例: python3 image_clicker.py button.png")
print("\n3. プログラムでの使用:")
print("   from image_clicker import ImageClicker")
print("   clicker = ImageClicker()")
print("   clicker.click_image('target.png')")

print("\n=== WSL2での注意事項 ===")
print("X11サーバーまたはXサーバーが必要です:")
print("- VcXsrv, Xming等のWindowsXサーバーをインストール")
print("- WSL2のDISPLAY環境変数を設定")
print("- または、Windows側でPythonを実行することを推奨")
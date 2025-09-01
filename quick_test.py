#!/usr/bin/env python3
"""
画像クリックツールの簡単なテスト
スクリーンショットを撮影してから、その一部をクリックするテスト
"""

import pyautogui
import os
import time
from image_clicker import ImageClicker

def take_screenshot_and_crop():
    """スクリーンショットを撮影し、一部を切り出してテスト画像を作成"""
    print("=== テスト用画像の作成 ===")
    
    # sample_imagesディレクトリを作成
    os.makedirs("sample_images", exist_ok=True)
    
    # 3秒待機してからスクリーンショット
    print("3秒後にスクリーンショットを撮影します...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # フルスクリーンショット
    screenshot = pyautogui.screenshot()
    screenshot.save("sample_images/fullscreen.png")
    print("✓ フルスクリーンショットを保存しました: sample_images/fullscreen.png")
    
    # 画面の一部を切り出し（中央付近の小さな領域）
    width, height = screenshot.size
    left = width // 2 - 50
    top = height // 2 - 50
    right = width // 2 + 50
    bottom = height // 2 + 50
    
    cropped = screenshot.crop((left, top, right, bottom))
    cropped.save("sample_images/test_target.png")
    print("✓ テスト用ターゲット画像を作成しました: sample_images/test_target.png")
    
    return "sample_images/test_target.png"

def test_click_function(target_image):
    """作成したテスト画像でクリック機能をテスト"""
    print("\n=== クリック機能のテスト ===")
    
    clicker = ImageClicker(confidence=0.9, wait_time=0.5)
    
    print("5秒後にテストを開始します...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    success = clicker.click_image(target_image, timeout=10)
    
    if success:
        print("✓ テストクリックが成功しました")
        return True
    else:
        print("✗ テストクリックが失敗しました")
        return False

def main():
    """テストメイン処理"""
    print("画像クリックツール 簡単テスト")
    print("=" * 40)
    
    try:
        # テスト用画像を作成
        target_image = take_screenshot_and_crop()
        
        # クリック機能をテスト
        success = test_click_function(target_image)
        
        print("\n" + "=" * 40)
        if success:
            print("✓ テスト完了: 画像クリック機能は正常に動作しています")
        else:
            print("⚠ テスト完了: 画像が見つからないか設定を調整してください")
            print("  - 信頼度を下げてみる (0.7-0.8)")
            print("  - 画面の状態を確認する")
        
    except Exception as e:
        print(f"✗ テスト中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
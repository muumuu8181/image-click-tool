#!/usr/bin/env python3
"""
target.png画像をクリックするテスト
"""

from image_clicker import ImageClicker
import time

def test_target_click():
    """target.png画像をクリック"""
    print("=== target.png クリックテスト ===")
    print("5秒後に開始します...")
    time.sleep(5)
    
    # ImageClickerを初期化
    clicker = ImageClicker(confidence=0.7, wait_time=0.5)
    
    # target.pngをクリック
    print("target.pngを探しています...")
    success = clicker.click_image("target.png", timeout=10)
    
    if success:
        print("target.pngのクリックに成功しました！")
    else:
        print("target.pngが見つからないか、クリックに失敗しました")
        print("  画面上にtarget.pngと一致する画像があることを確認してください")

if __name__ == "__main__":
    test_target_click()
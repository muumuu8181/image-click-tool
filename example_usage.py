#!/usr/bin/env python3
"""
画像クリックツールの使用例
"""

from image_clicker import ImageClicker
import time

def example_single_click():
    """単一の画像をクリックする例"""
    print("=== 単一画像クリックの例 ===")
    
    # ImageClickerを初期化
    clicker = ImageClicker(confidence=0.8, wait_time=0.5)
    
    # imagesフォルダ内の画像をクリック
    success = clicker.click_image("sample_button.png", timeout=10)
    
    if success:
        print("ボタンのクリックに成功しました")
    else:
        print("ボタンが見つからないか、クリックに失敗しました")

def example_multiple_clicks():
    """複数の画像を順番にクリックする例"""
    print("\n=== 複数画像クリックの例 ===")
    
    clicker = ImageClicker(confidence=0.7)
    
    # imagesフォルダ内のクリックしたい画像のリスト
    images = [
        "button1.png",
        "button2.png", 
        "button3.png"
    ]
    
    results = clicker.click_multiple_images(images, timeout=5)
    
    for i, result in enumerate(results):
        status = "成功" if result else "失敗"
        print(f"画像 {i+1}: {status}")

def example_wait_and_click():
    """画像が表示されるまで待機してクリックする例"""
    print("\n=== 待機クリックの例 ===")
    
    clicker = ImageClicker(confidence=0.9)
    
    # 最大30秒間、2秒間隔でimagesフォルダ内の画像の出現を待機
    success = clicker.wait_and_click("loading_complete.png", max_wait=30, check_interval=2)
    
    if success:
        print("読み込み完了ボタンをクリックしました")
    else:
        print("読み込み完了ボタンが見つかりませんでした")

def example_custom_settings():
    """カスタム設定での例"""
    print("\n=== カスタム設定の例 ===")
    
    # 高精度、長い待機時間で設定
    clicker = ImageClicker(confidence=0.95, wait_time=2.0)
    
    success = clicker.click_image("precise_target.png", timeout=15)
    
    if success:
        print("高精度でのクリックに成功しました")
    else:
        print("高精度でのクリックに失敗しました")

def example_error_handling():
    """エラーハンドリングの例"""
    print("\n=== エラーハンドリングの例 ===")
    
    clicker = ImageClicker()
    
    try:
        # imagesフォルダ内の存在しない画像を試行
        success = clicker.click_image("nonexistent.png", timeout=3)
        
        if not success:
            print("画像が見つからなかった場合の処理")
            # フォールバック処理をここに書く
            
    except Exception as e:
        print(f"予期しないエラー: {e}")

if __name__ == "__main__":
    print("画像クリックツール使用例")
    print("注意: imagesフォルダ内に実際の画像ファイルが必要です")
    print("5秒後に開始...")
    
    time.sleep(5)
    
    # 各例を実行（実際の画像がないため、失敗するのは正常）
    example_single_click()
    example_multiple_clicks() 
    example_wait_and_click()
    example_custom_settings()
    example_error_handling()
    
    print("\n使用例の実行完了")
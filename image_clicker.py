#!/usr/bin/env python3
"""
画像クリックツール
pyautoguiを使用して画面上の指定された画像を検索してクリックします
"""

import pyautogui
import time
import os
import sys
from pathlib import Path


class ImageClicker:
    def __init__(self, confidence=0.8, wait_time=1.0, images_dir="images"):
        """
        ImageClickerを初期化
        
        Args:
            confidence (float): 画像マッチングの信頼度 (0.0-1.0)
            wait_time (float): クリック前の待機時間（秒）
            images_dir (str): 画像ファイルを配置するディレクトリ
        """
        self.confidence = confidence
        self.wait_time = wait_time
        self.images_dir = Path(images_dir)
        
        # imagesディレクトリを作成（存在しない場合）
        self.images_dir.mkdir(exist_ok=True)
        
        # フェイルセーフを有効化（マウスを画面の隅に移動するとプログラムが停止）
        pyautogui.FAILSAFE = True
        
        # マウス移動の間隔を設定
        pyautogui.PAUSE = 0.25
    
    def click_image(self, image_name, timeout=10):
        """
        指定された画像を画面上で検索してクリック
        
        Args:
            image_name (str): クリックしたい画像のファイル名（imagesフォルダ内）
            timeout (int): タイムアウト時間（秒）
            
        Returns:
            bool: クリックが成功したかどうか
        """
        # imagesディレクトリ内のパスを生成
        image_path = self.images_dir / image_name
        
        if not image_path.exists():
            print(f"エラー: 画像ファイルが見つかりません: {image_path}")
            return False
        
        print(f"画像を検索中: {image_path}")
        print(f"信頼度: {self.confidence}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 画面上で画像を検索
                location = pyautogui.locateOnScreen(
                    str(image_path), 
                    confidence=self.confidence
                )
                
                if location:
                    # 画像の中心座標を取得
                    center = pyautogui.center(location)
                    
                    print(f"画像が見つかりました: {center}")
                    
                    # 待機時間
                    time.sleep(self.wait_time)
                    
                    # クリック実行
                    pyautogui.click(center)
                    
                    print(f"クリック完了: ({center.x}, {center.y})")
                    return True
                    
            except pyautogui.ImageNotFoundException:
                pass
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                return False
            
            # 短時間待機してから再試行
            time.sleep(0.5)
        
        print(f"タイムアウト: {timeout}秒以内に画像が見つかりませんでした")
        return False
    
    def click_multiple_images(self, image_names, timeout=10):
        """
        複数の画像を順番にクリック
        
        Args:
            image_names (list): 画像ファイル名のリスト（imagesフォルダ内）
            timeout (int): 各画像のタイムアウト時間（秒）
            
        Returns:
            list: 各クリックの成功/失敗のリスト
        """
        results = []
        
        for i, image_name in enumerate(image_names):
            print(f"\n--- 画像 {i+1}/{len(image_names)} ---")
            result = self.click_image(image_name, timeout)
            results.append(result)
            
            if result:
                print("成功")
            else:
                print("失敗")
                
            # 次の画像への待機時間
            time.sleep(1.0)
        
        return results
    
    def wait_and_click(self, image_name, max_wait=60, check_interval=2):
        """
        画像が表示されるまで待機してからクリック
        
        Args:
            image_name (str): クリックしたい画像のファイル名（imagesフォルダ内）
            max_wait (int): 最大待機時間（秒）
            check_interval (int): チェック間隔（秒）
            
        Returns:
            bool: クリックが成功したかどうか
        """
        print(f"画像の出現を待機中: {image_name}")
        print(f"最大待機時間: {max_wait}秒")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.click_image(image_name, timeout=1):
                return True
            
            print(f"待機中... ({int(time.time() - start_time)}秒経過)")
            time.sleep(check_interval)
        
        print(f"最大待機時間を超過しました: {max_wait}秒")
        return False


def main():
    """メイン関数 - コマンドライン引数から画像をクリック"""
    if len(sys.argv) < 2:
        print("使用方法: python image_clicker.py <画像ファイル名> [信頼度]")
        print("例: python image_clicker.py button.png 0.9")
        print("注意: 画像ファイルはimagesフォルダ内に配置してください")
        sys.exit(1)
    
    image_name = sys.argv[1]
    confidence = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
    
    # ImageClickerを初期化
    clicker = ImageClicker(confidence=confidence)
    
    print("=== 画像クリックツール ===")
    print(f"対象画像: images/{image_name}")
    print("3秒後に開始します...")
    
    # 開始前の待機時間
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # 画像をクリック
    success = clicker.click_image(image_name)
    
    if success:
        print("✓ クリックが完了しました")
    else:
        print("✗ クリックに失敗しました")


if __name__ == "__main__":
    main()
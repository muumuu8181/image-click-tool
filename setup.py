#!/usr/bin/env python3
"""
画像クリックツールのセットアップスクリプト
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """必要なパッケージをインストール"""
    print("=== 依存パッケージのインストール ===")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ 依存パッケージのインストールが完了しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ パッケージのインストールに失敗しました: {e}")
        return False

def create_sample_images():
    """サンプル画像ディレクトリを作成"""
    print("\n=== サンプル画像ディレクトリの作成 ===")
    
    sample_dir = Path("sample_images")
    sample_dir.mkdir(exist_ok=True)
    
    print(f"✓ サンプル画像ディレクトリを作成しました: {sample_dir}")
    print("  実際の画像ファイルをここに配置してください")

def show_usage():
    """使用方法を表示"""
    print("\n=== 使用方法 ===")
    print("1. 基本的な使用:")
    print("   python image_clicker.py <画像ファイルパス>")
    print("   例: python image_clicker.py sample_images/button.png")
    print()
    print("2. 信頼度を指定:")
    print("   python image_clicker.py <画像ファイルパス> <信頼度>")
    print("   例: python image_clicker.py sample_images/button.png 0.9")
    print()
    print("3. プログラムで使用:")
    print("   from image_clicker import ImageClicker")
    print("   clicker = ImageClicker()")
    print("   clicker.click_image('button.png')")
    print()
    print("4. 使用例を確認:")
    print("   python example_usage.py")
    print()
    print("注意事項:")
    print("- マウスを画面の左上隅に移動するとプログラムが緊急停止します")
    print("- 画像は PNG, JPG, BMP 形式をサポートしています")
    print("- 信頼度は 0.0～1.0 の範囲で設定してください（推奨: 0.7～0.9）")

def main():
    """メインセットアップ処理"""
    print("画像クリックツール セットアップ")
    print("=" * 40)
    
    # カレントディレクトリを確認
    current_dir = Path.cwd()
    print(f"セットアップディレクトリ: {current_dir}")
    
    # 依存パッケージのインストール
    if not install_requirements():
        print("\nセットアップに失敗しました")
        return False
    
    # サンプルディレクトリの作成
    create_sample_images()
    
    # 使用方法の表示
    show_usage()
    
    print("\n" + "=" * 40)
    print("✓ セットアップが完了しました")
    print("今すぐ使用を開始できます！")
    
    return True

if __name__ == "__main__":
    main()
# Windows での画像クリックツール セットアップ手順

## 🚀 推奨方法: Windows PowerShell/Command Prompt で実行

### 1. Python インストール確認
```powershell
python --version
# または
python3 --version
```

### 2. 必要パッケージのインストール
```powershell
cd "C:\Users\kakar\OneDrive\デスクトップ\work\90_cc\0901\image-click-tool"
pip install -r requirements.txt
```

### 3. 実行テスト
```powershell
# 使用方法表示
python image_clicker.py

# 画像クリック実行（imagesフォルダに画像配置後）
python image_clicker.py button.png
```

## 🔧 Visual Studio Code Cloud Code 統合

### A. VSCode での開発環境セットアップ
1. **VSCode インストール** (未インストールの場合)
   - https://code.visualstudio.com/

2. **Python 拡張機能インストール**
   - VSCode で `Ctrl+Shift+X`
   - "Python" 検索 → インストール

3. **プロジェクトを開く**
   ```
   code "C:\Users\kakar\OneDrive\デスクトップ\work\90_cc\0901\image-click-tool"
   ```

### B. Claude Code との連携
1. **Claude Code CLI インストール**
   - PowerShell (管理者権限で実行):
   ```powershell
   iwr -useb https://claude.ai/cli/install.ps1 | iex
   ```

2. **プロジェクト内でClaude Code開始**
   ```powershell
   cd "C:\Users\kakar\OneDrive\デスクトップ\work\90_cc\0901\image-click-tool"
   claude-code
   ```

## 🐍 Python 仮想環境での実行 (推奨)

### Windows PowerShell:
```powershell
cd "C:\Users\kakar\OneDrive\デスクトップ\work\90_cc\0901\image-click-tool"

# 仮想環境作成
python -m venv venv

# 仮想環境有効化
.\venv\Scripts\Activate.ps1

# パッケージインストール
pip install -r requirements.txt

# 実行
python image_clicker.py button.png
```

### Command Prompt:
```cmd
cd "C:\Users\kakar\OneDrive\デスクトップ\work\90_cc\0901\image-click-tool"

# 仮想環境作成
python -m venv venv

# 仮想環境有効化
venv\Scripts\activate

# パッケージインストール
pip install -r requirements.txt

# 実行
python image_clicker.py button.png
```

## 🎯 使用方法

1. **imagesフォルダに対象画像を配置**
   ```
   images/
   ├── button.png
   ├── submit.png
   └── target.png
   ```

2. **単一画像クリック**
   ```powershell
   python image_clicker.py button.png
   ```

3. **プログラムでの使用**
   ```python
   from image_clicker import ImageClicker
   
   clicker = ImageClicker()
   success = clicker.click_image("button.png")
   ```

## ⚠️ 注意事項

- **WSL2の制限**: GUI操作にはX11サーバーが必要
- **Windows直接実行**: 最も簡単で確実
- **管理者権限**: 一部操作で必要な場合あり
- **ウイルスソフト**: pyautoguiがブロックされる場合は例外設定が必要

## 🔍 トラブルシューティング

### Python が見つからない場合:
```powershell
# Microsoft Store からPythonインストール
# または python.org からダウンロード
```

### pip が動作しない場合:
```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### パッケージインストールエラー:
```powershell
pip install --user pyautogui pillow opencv-python
```
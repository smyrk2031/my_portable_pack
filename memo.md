
# ナビアプリ開発メモ
- 開発期間：20241005より
- フロントエンドで完結するナビアプリの作成



# ----------------------------------------------------
# ----------------------------------------------------

# テスト方法
## 1. 自己署名証明書の作成
    - opensslをインストール
    - openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
    - key.pemとcert.pemの2ファイルが作成されればOK（後でパス指定で設定するのに使う）
## 2. IPアドレスの取得
    - ipconfig
    ※ wifiのipv4のIPを取得する：例 192.168.0.9
    ※ パソコンとクライアントデバイスは同一ネットワークに接続している事

## 3. 簡易serverでデプロイ
### 方法1. pythonでサーバを立ち上げる方法
    ```
    import http.server
    import ssl

    # ポート番号とディレクトリの設定
    PORT = 4443
    DIRECTORY = "."

    # HTTPリクエストハンドラーの設定
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

    # サーバーを作成
    httpd = http.server.HTTPServer(('localhost', PORT), MyHandler)

    # SSLラップ
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True)

    print(f"Serving HTTPS on https://localhost:{PORT}")
    httpd.serve_forever()
    ```

### 方法2. vscodeのLive Serverを使って簡易デプロイ（おすすめ！）
    - vscodeの拡張のLive Serverをインストール
    - settingでLive Serverを検索し、下記項目を設定
        1. hostにipconfigで取得したIPアドレス
        2. httpsのenable=trueに変更し、certとkeyにそれぞれ自己署名証明書のファイルパスを設定
        3. vscode右下のGo Liveボタンを押すとサーバが立ち上がりデプロイされる

## 4.クライアントデバイスからアクセスする方法
    - ブラウザを起動する
    - http://<WindowsのIPアドレス(ipconfigで取得したipv4)>:8000
    - http://<WindowsのIPアドレス(ipconfigで取得したipv4)>:8000/about.html
        ※ ブラウザではセキュリティのない接続ですと表示されるが、気にせずアクセス！


# ----------------------------------------------------
# ----------------------------------------------------


# 機能要件
## 環境
    - iPhoneSE2をターゲットにする
    - デプロイ先はサーバ

## Step1.MAP機能
    - マップ上に位置情報を更新し続ける
## Step2.経路表示
    - 経路データをマップ上に表示する
    - 経路データの計測・保存をする
## Step3.開発者モード
    - 位置情報の計測精度確認の為に、グラフにリアルタイムプロットして可視化する
    - 
## Step4.その他機能
    - デザインモードの切り替え機能
    - 危険個所マップ表示機能
    - 交差点の写真表示機能
    - 右左折ポイントの目印紹介機能
    - 走行前のアクシデントテスト機能
    - 3Dマップで確認する機能
    - 撮影した動画を確認する機能
    - 


## ---------------------------------------------------------------------------

# 開発メモ

### 経路データ.json
``` json
{
    "type":"FeatureCollection",
    "features":[
        {
            "type":"Feature",
            "properties":{},
            "geometry":{
                "type":"LineString",
                "coordinates":[
                    [137.0095616,35.1404032],
                    [137.0095616,35.1404032],
                ]
            }
        }
    ]
} 
```
#### 緯度経度の格納テクニック
    - サンプリングをすべて格納する問題点
        - ノイズ多い
        - メモリ負荷高い
    - 対策案
        - 停止判定：緯度経度が0.001以内の変化の場合は、保存しないようにする？
        - カルマンフィルタとかで簡素な位置推定してきれいな経路にする


#### leafletの地図上に表示するマーカーに、自作のsvgカスタムアイコンを埋め込む

- 緑のマーカーピン
```
<svg xmlns="http://www.w3.org/2000/svg" width="30" height="40" viewBox="0 0 30 40">
                        <path d="M15 0C7.2 0 0 7.2 0 15c0 8.1 15 25 15 25s15-16.9 15-25c0-7.8-7.2-15-15-15zm0 22c-3.9 0-7-3.1-7-7s3.1-7 7-7 7 3.1 7 7-3.1 7-7 7z" fill="green"/>
</svg>
```

- 鋭角ピン (小さな丸)
```
<svg xmlns="http://www.w3.org/2000/svg" width="30" height="40" viewBox="0 0 30 40">
    <path d="M15 0C8 0 2 6 2 12c0 8.3 13 24 13 24s13-15.7 13-24c0-6-6-12-13-12zm0 20c-3.5 0-6-3-6-6s2.5-6 6-6 6 2.5 6 6-2.5 6-6 6z" fill="green"/>
</svg>
```

- 鋭角ピン (小さめの丸)
```
<svg xmlns="http://www.w3.org/2000/svg" width="30" height="40" viewBox="0 0 30 40">
    <path d="M15 0C9 0 3 7 3 12c0 8 12 24 12 24s12-16 12-24c0-5-5-12-12-12zm0 18c-2.5 0-4.5-2-4.5-4.5S12.5 11 15 11s4.5 2 4.5 4.5S17.5 18 15 18z" fill="green"/>
</svg>

```

- 鋭角ピン (よりシャープなデザイン)
```
<svg xmlns="http://www.w3.org/2000/svg" width="30" height="40" viewBox="0 0 30 40">
    <path d="M15 0C8.5 0 2 6.5 2 12.5c0 8 13 24 13 24s13-15.5 13-24c0-6-6.5-12.5-13-12.5zm0 22c-3 0-5-2.5-5-5s2-5 5-5 5 2.5 5 5-2 5-5 5z" fill="green"/>
</svg>

```

```
```

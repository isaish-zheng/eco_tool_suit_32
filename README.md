> # 产品信息
> **Eco Tool Suit**


> # 本产品包含以下内容
> * **Eco Downloader**
> * **Eco Viewer**


> # 功能说明
> ## Eco Downloader
> 1. 使用ccp协议下载程序
> 2. 使用uds协议下载程序
> ## Eco Viewer
> 1. 使用ccp协议监视测量对象


> # 使用说明
> ## 操作系统
> **Windows10及以上版本(x86/x64)**
> ## Python版本
> **Pyhton3.10.11** [Python解释器下载](https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe)
> ## 外部依赖（建议使用项目提供的文件）
> 1. 安装PCAN驱动程序 [PEAK-System_Driver下载](https://peak-system.com.cn/wp-content/uploads/2024/07/PEAK-System_Driver-Setup-v4.5.0.zip)
> 2. 将.dll文件按照如下路径放置
>    * For x64 Windows systems [PCAN-Basic API下载](https://peak-system.com.cn/wp-content/uploads/2023/05/PCAN-Basic_Windows-4.7.zip)
>      - PCAN-Basic\x86\PCANBasic.dll --> C:\Windows\SysWOW64
>      - PCAN-Basic\x64\PCANBasic.dll --> C:\Windows\System32
>    * PCCP.dll --> Eco Tool Suit.exe同级路径 [PCAN-CCP API下载](https://peak-system.com.cn/wp-content/uploads/2022/06/PCAN-CCP.zip)
>    * PCAN-ISO-TP.dll --> Eco Tool Suit.exe同级路径 [PCAN-ISO-TP API下载](https://peak-system.com.cn/wp-content/uploads/2022/06/PCAN-ISO-TP.zip)
>    * PCAN-UDS.dll --> Eco Tool Suit.exe同级路径 [PCAN-UDS API下载](https://peak-system.com.cn/wp-content/uploads/2023/05/PCAN-UDS.zip)
> ## 打包方式
> **PyInstaller**
> * 安装pyinstaller模块，打开cmd窗口，运行以下命令
> 
>   `pip install pyinstaller`
> * 打包成exe，按住shift+鼠标右键弹出菜单，点击打开powershell，运行以下命令
> 
>   `pyinstaller main.py -F -w -i .\icons\Z.ico -n "Eco Tool Suit"`
> 
> ## 运行exe
> * 以管理员身份运行Eco Tool Suit.exe
> 
> ### 使用Eco Downloader
> 1. 选择刷写密钥
>   * CCP -> PG_Default.dll
>   * UDS -> UdsSeedKeyDll.dll
> 2. 打开程序文件(.mot)
> 3. 点击下载按钮
>
> ### 使用Eco Viewer
> 1. 点击打开按钮，打开程序文件(.mot)和测量标定文件(.a2l)
> 2. 在测量对象列表中选中待监视对象后，点击确定按钮添加至监视列表
> 3. 点击连接按钮连接VCU
> 4. 连接成功后，可点击启动按钮开始监视

> # 其它
> * 本产品仅用于学习交流，请勿用于商业用途

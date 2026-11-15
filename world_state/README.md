# README.md
# Closed Habitat Sim - World State Service
> 密闭栖息地仿真 - 世界状态服务（影视中控道具版）
独立微服务，用于存储、管理密闭栖息地全局仿真状态，提供事件驱动状态更新、快照保存/回滚、多终端局域网同步。可打包为Mac单文件可执行程序，直接U盘交付片场。

## ✨ 功能简介
1. 状态域管理
- `environment_state`：舱内环境参数（温度、气压、氧含量等）
- `crew_state`：乘员生命体征、位置、人员状态
- `equipment_state`：舱内各类设备运行参数、工作状态
- `alert_state`：告警信息，支持多级告警维护

2. 核心能力
- 事件总线：接收事件，校验业务规则，更新全局WorldState
- 状态快照：保存任意时刻全局状态，按数字版本号一键回滚
- 内置Web中控面板：浏览器可视化查看、手动提交事件、管理快照、查看事件日志
- 局域网多屏同步：一台主控启动，同WiFi下多台平板/电脑访问，所有页面共享同一套仿真状态

## 📦 部署方式
### 方式1：打包单文件交付（Mac）
1. 运行打包命令生成dist/main可执行文件
2. 终端执行 `./main` 启动服务
3. 本机访问：`[http://127.0.0.1:8000](http://127.0.0.1:8000)`
4. 局域网其他设备访问：`http://[主控内网IP]:8000`
> ⚠️ 注意：启动后不要关闭终端窗口；Mac首次打开需右键放行未识别开发者；拍摄前关闭电脑自动睡眠。

### 方式2：开发环境直接运行
```bash
uv run main.py
```

## 🔌 核心API接口
| 接口 | 方法 | 说明 |
| ---- | ---- | ---- |
| `/` | GET | 中控Web面板页面 |
| `/api/event/submit` | POST | 提交事件，更新对应域状态（事件总线入口） |
| `/api/worldstate` | GET | 获取完整全局世界状态 |
| `/api/snapshot/save` | POST | 保存当前状态，生成新版本快照 |
| `/api/snapshot/list` | GET | 获取全部快照版本列表 |
| `/api/snapshot/rollback` | POST | 回滚到指定版本快照 |

## 📁 项目目录
```
world_state/
├── main.py                 # 服务入口
├── src/
│   ├── core/               # 全局配置、日志
│   ├── domains/            # 四大业务状态域
│   │   ├── alert_state
│   │   ├── crew_state
│   │   ├── environment_state
│   │   └── equipment_state
│   ├── store.py            # 全局WorldState存储
│   └── web/
│       ├── templates/      # dashboard.html 中控页面
│       └── static/         # CSS静态样式
└── requirements.txt
```

## ⚠️ 影视道具使用要点
1. 所有屏幕共用同一个状态，一处修改，全部面板实时同步
2. 快照使用纯数字版本号管理，简洁直观
3. 拍摄使用独立局域网，不需要外网
4. 适合科幻影片舱内中控屏幕实拍，**不是预录视频，全部交互真实生效**

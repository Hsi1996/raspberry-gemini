# test.py 程式說明

## 這是什麼？

這是一個 **Open WebUI Filter 插件**的範例程式。

Open WebUI 是一個可以自架的 AI 聊天介面（類似 ChatGPT），支援載入自訂插件來擴充功能。
Filter（過濾器）插件可以在對話流程中「攔截」訊息，在送給 AI 之前或 AI 回應之後做額外處理。

---

## 對話流程示意

```
使用者輸入訊息
      ↓
  [ inlet ]  ← Filter 在這裡攔截，可以檢查、修改、或拒絕請求
      ↓
   AI 模型處理
      ↓
  [ outlet ] ← Filter 在這裡攔截，可以檢查或修改 AI 的回應
      ↓
顯示回應給使用者
```

---

## 程式結構

### `class Filter`
插件的主體類別，Open WebUI 會自動識別並載入它。

---

### `class Valves`（管理員設定）

```python
class Valves(BaseModel):
    priority: int = Field(default=0, ...)
    max_turns: int = Field(default=8, ...)
```

- 由**管理員**在後台設定，使用者看不到也改不了
- `priority`：當有多個 Filter 插件時，決定執行順序（數字越小越先）
- `max_turns`：整個系統允許的最大對話輪數，預設 **8 輪**

---

### `class UserValves`（使用者設定）

```python
class UserValves(BaseModel):
    max_turns: int = Field(default=4, ...)
```

- 每個**使用者**可以自行調整的設定
- `max_turns`：使用者自己設定的對話輪數上限，預設 **4 輪**

---

### `__init__`（初始化）

```python
def __init__(self):
    self.valves = self.Valves()
```

- 插件載入時自動執行
- 建立 `Valves` 實例，套用管理員設定

---

### `inlet`（入口攔截）

```python
def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
```

**執行時機**：使用者送出訊息後，AI 處理之前

**這個範例做了什麼：**
1. 印出目前的請求內容和使用者資訊（除錯用）
2. 檢查使用者角色是否為 `user` 或 `admin`
3. 計算實際允許的輪數上限：取使用者設定和管理員設定的**較小值**
4. 如果對話歷史超過上限，**拋出例外**中止請求，並顯示錯誤訊息

**輪數上限計算範例：**
| 管理員設定 (Valves) | 使用者設定 (UserValves) | 實際上限 |
|---|---|---|
| 8 | 4 | 4（取較小值）|
| 8 | 10 | 8（取較小值）|
| 3 | 4 | 3（取較小值）|

---

### `outlet`（出口攔截）

```python
def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
```

**執行時機**：AI 產生回應後，顯示給使用者之前

**這個範例做了什麼：**
1. 印出回應內容和使用者資訊（除錯用）
2. 直接回傳原本的回應（沒有做額外修改）

實際應用中可以在這裡過濾敏感詞、記錄 log、或修改回應格式。

---

## 使用的套件

| 套件 | 用途 |
|---|---|
| `pydantic` | 定義設定資料結構，自動驗證型別 |
| `typing.Optional` | 標記參數可以是 `None` |

---

## 延伸應用方向

- 在 `inlet` 加入關鍵字過濾，阻擋不當輸入
- 在 `outlet` 記錄對話到資料庫
- 修改 `max_turns` 邏輯，針對不同使用者群組設定不同上限
- 啟用 `self.file_handler = True` 自訂檔案上傳處理邏輯

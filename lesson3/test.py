"""
title: Example Filter
author: open-webui
author_url: https://github.com/open-webui
funding_url: https://github.com/open-webui
version: 0.1

這是一個 Open WebUI 的 Filter（過濾器）插件範例。
Filter 插件可以在使用者送出訊息「之前」(inlet) 和 AI 回應「之後」(outlet) 攔截並處理資料。
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    """
    Filter 類別是 Open WebUI 插件的主體。
    Open WebUI 會自動載入這個類別，並在對話流程中呼叫 inlet / outlet 方法。
    """

    class Valves(BaseModel):
        """
        Valves（閥門）是「管理員層級」的設定，由管理員在後台配置。
        使用 Pydantic BaseModel 定義，每個欄位都有預設值和說明。
        """
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
            # 過濾器的優先順序，數字越小越先執行
        )
        max_turns: int = Field(
            default=8, description="Maximum allowable conversation turns for a user."
            # 管理員設定的對話輪數上限，預設 8 輪
        )
        pass

    class UserValves(BaseModel):
        """
        UserValves 是「使用者層級」的設定，每個使用者可以自行調整。
        通常上限不能超過 Valves 的設定值。
        """
        max_turns: int = Field(
            default=4, description="Maximum allowable conversation turns for a user."
            # 使用者自己設定的對話輪數上限，預設 4 輪
        )
        pass

    def __init__(self):
        """
        初始化 Filter 插件。
        在這裡建立 Valves 實例，載入管理員設定。
        """
        # self.file_handler = True
        # 若取消註解，代表這個插件會自己處理檔案上傳邏輯，
        # 不使用 WebUI 預設的檔案處理流程。

        # 建立 Valves 實例，套用管理員預設設定
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        inlet（入口）：在使用者訊息送到 AI 之前執行。
        可以用來：驗證輸入、修改請求內容、限制對話輪數等。

        參數：
            body: 完整的請求內容，包含 messages（對話歷史）等資訊
            __user__: 目前使用者的資訊，包含角色(role)和個人設定(valves)

        回傳：
            修改後（或原本）的 body，會繼續傳給 AI 處理
        """
        print("使用者輸入")
        

        # 只對 "user" 和 "admin" 角色進行輪數限制檢查
        if __user__.get("role", "admin") in ["user", "admin"]:
            messages = body.get("messages", [])  # 取得對話歷史列表

            # 取使用者設定和管理員設定中「較小的值」作為實際上限
            # 防止使用者把自己的上限設得比管理員允許的還高
            max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)

            # 如果對話輪數超過上限，直接拋出例外，中止這次請求
            if len(messages) > max_turns:
                raise Exception(
                    f"Conversation turn limit exceeded. Max turns: {max_turns}"
                )

        return body  # 回傳（可能已修改的）請求內容

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        outlet（出口）：在 AI 回應產生之後執行。
        可以用來：記錄回應、過濾敏感內容、修改回應格式等。

        參數：
            body: AI 回應的完整內容
            __user__: 目前使用者的資訊

        回傳：
            修改後（或原本）的 body，會顯示給使用者
        """
        print("模型輸出")
        

        return body  # 回傳（可能已修改的）回應內容

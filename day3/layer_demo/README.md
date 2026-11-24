# 分層檢查示範

`src/service/report_service.py` 故意 import 了 `src.ui.formatting`，違反「service 不可依賴 ui」的規則。

```bash
make test    # 通過：程式本身能跑
make lint    # 失敗：分層規則被違反，錯誤訊息附修正方式
```

重點：測試通過不代表架構正確。修正步驟見 `../lab6.md` 的 Part A。

#!/bin/bash
# 輸出最新標籤，以及該標籤之後的 commit（一行一筆）
tag=$(git describe --tags --abbrev=0 2>/dev/null) || { echo "沒有標籤"; git log --oneline; exit 0; }
echo "最新標籤：$tag"
git log --oneline "$tag"..HEAD

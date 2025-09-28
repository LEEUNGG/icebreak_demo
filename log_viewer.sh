#!/bin/bash

# 日志查看器脚本
# 此脚本用于实时查看conversation.log文件

LOG_FILE="conversation.log"

# 检查日志文件是否存在
if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  日志文件 $LOG_FILE 尚未创建"
    echo "💡  请先运行主程序以生成日志文件"
    echo "📝  之后可以使用 'tail -f $LOG_FILE' 命令实时查看日志"
    exit 1
fi

# 使用tail命令实时查看日志
echo "🚀  启动实时日志查看器..."
echo "📋  查看文件: $LOG_FILE"
echo "💡  按 Ctrl+C 终止查看"
echo ""

tail -f "$LOG_FILE"
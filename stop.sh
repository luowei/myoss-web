#!/bin/bash

################################################################################
# MyOSS 停止脚本
# 功能：
#   1. 停止运行的应用
#   2. 清理端口占用
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PORT=${PORT:-5001}
PID_FILE="logs/app.pid"

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 停止应用
stop_app() {
    print_info "停止 MyOSS 应用..."
    
    # 方式 1: 通过 PID 文件停止
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            print_info "发现运行中的进程 (PID: $PID)"
            kill $PID
            
            # 等待进程停止
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    break
                fi
                sleep 0.5
            done
            
            # 如果还在运行，强制停止
            if ps -p $PID > /dev/null 2>&1; then
                print_warning "进程未响应，强制停止..."
                kill -9 $PID
            fi
            
            print_success "应用已停止"
        else
            print_warning "PID 文件存在但进程未运行"
        fi
        rm -f $PID_FILE
    else
        print_info "未找到 PID 文件"
    fi
    
    # 方式 2: 通过端口停止
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_warning "端口 $PORT 仍被占用，清理中..."
        
        PID=$(lsof -ti:$PORT)
        if [ ! -z "$PID" ]; then
            kill -9 $PID
            sleep 1
            
            if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
                print_error "无法释放端口，请手动处理"
                exit 1
            else
                print_success "端口已释放"
            fi
        fi
    fi
    
    print_success "========================================="
    print_success "MyOSS 应用已停止"
    print_success "========================================="
}

# 查看状态
check_status() {
    print_info "检查应用状态..."
    
    # 检查 PID 文件
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            print_success "应用正在运行 (PID: $PID)"
        else
            print_warning "PID 文件存在但进程未运行"
        fi
    else
        print_info "未找到 PID 文件"
    fi
    
    # 检查端口
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -ti:$PORT)
        print_warning "端口 $PORT 被占用 (PID: $PID)"
    else
        print_success "端口 $PORT 可用"
    fi
}

# 显示使用帮助
show_help() {
    echo "MyOSS 停止脚本"
    echo ""
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help    显示帮助信息"
    echo "  -s, --status  查看状态"
    echo "  -p, --port    指定端口（默认：5001）"
    echo ""
    echo "示例:"
    echo "  $0              # 停止应用"
    echo "  $0 -s          # 查看状态"
    echo "  $0 -p 5002     # 停止 5002 端口的应用"
    echo ""
}

# 主函数
main() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--status)
                check_status
                exit 0
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            *)
                print_error "未知选项：$1"
                show_help
                exit 1
                ;;
        esac
    done
    
    stop_app
}

main "$@"

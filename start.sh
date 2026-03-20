#!/bin/bash

################################################################################
# MyOSS 一键启动脚本
# 功能：
#   1. 检查并创建虚拟环境
#   2. 自动安装依赖
#   3. 检查端口占用并清理
#   4. 启动 Flask 应用
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
VENV_DIR=".venv"
PORT=${PORT:-5001}
LOG_FILE="logs/app.log"
PID_FILE="logs/app.pid"

# 打印带颜色的消息
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

# 检查是否在项目根目录
check_project_root() {
    if [ ! -f "app/__init__.py" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查并创建虚拟环境
check_venv() {
    print_info "检查虚拟环境..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "虚拟环境不存在，正在创建..."
        
        # 检查 Python 版本
        if ! command -v python3 &> /dev/null; then
            print_error "未找到 Python3，请先安装 Python 3.10+"
            exit 1
        fi
        
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_info "当前 Python 版本：$PYTHON_VERSION"
        
        # 创建虚拟环境
        python3 -m venv $VENV_DIR
        
        if [ $? -eq 0 ]; then
            print_success "虚拟环境创建成功"
        else
            print_error "虚拟环境创建失败"
            exit 1
        fi
    else
        print_success "虚拟环境已存在"
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source $VENV_DIR/bin/activate
        print_success "虚拟环境已激活"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    print_info "检查并安装依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "未找到 requirements.txt"
        exit 1
    fi
    
    # 升级 pip
    print_info "升级 pip..."
    pip install --upgrade pip -q
    
    # 安装依赖
    print_info "安装依赖包（这可能需要几分钟）..."
    pip install -r requirements.txt -q
    
    if [ $? -eq 0 ]; then
        print_success "依赖安装完成"
    else
        print_error "依赖安装失败"
        exit 1
    fi
}

# 检查并创建日志目录
check_logs_dir() {
    if [ ! -d "logs" ]; then
        print_info "创建日志目录..."
        mkdir -p logs
    fi
    
    if [ ! -d "data" ]; then
        print_info "创建数据目录..."
        mkdir -p data
    fi
}

# 检查端口占用并清理
check_and_kill_process() {
    print_info "检查端口 $PORT 占用情况..."
    
    # 检查端口是否被占用
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_warning "端口 $PORT 被占用，正在清理..."
        
        # 获取占用端口的进程 PID
        PID=$(lsof -ti:$PORT)
        
        if [ ! -z "$PID" ]; then
            print_info "发现进程 PID: $PID"
            
            # 检查是否是之前的应用进程
            PROCESS_NAME=$(ps -p $PID -o comm= 2>/dev/null || echo "")
            print_info "进程名称：$PROCESS_NAME"
            
            # 杀掉进程
            kill -9 $PID 2>/dev/null
            
            if [ $? -eq 0 ]; then
                print_success "已停止旧进程 (PID: $PID)"
                sleep 1
                
                # 验证端口是否已释放
                if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
                    print_error "端口仍然被占用，请手动处理"
                    exit 1
                else
                    print_success "端口已释放"
                fi
            else
                print_error "无法停止旧进程，请手动处理"
                exit 1
            fi
        fi
    else
        print_success "端口 $PORT 可用"
    fi
}

# 检查环境变量
check_env_vars() {
    print_info "检查环境变量..."
    
    # 检查必要的环境变量
    if [ -z "$OSS_ACCESS_KEY_ID" ]; then
        print_warning "环境变量 OSS_ACCESS_KEY_ID 未设置"
        
        # 尝试从 .env 文件加载
        if [ -f ".env" ]; then
            print_info "从 .env 文件加载配置..."
            export $(cat .env | grep -v '^#' | xargs)
            print_success "配置已加载"
        else
            print_warning "未找到 .env 文件，使用默认配置（仅限测试）"
        fi
    fi
    
    # 显示当前配置
    print_info "当前配置:"
    echo "  - OSS_ACCESS_KEY_ID: ${OSS_ACCESS_KEY_ID:0:10}***"
    echo "  - OSS_ENDPOINT: ${OSS_ENDPOINT:-未设置}"
    echo "  - OSS_BUCKET_NAME: ${OSS_BUCKET_NAME:-未设置}"
    echo "  - PORT: $PORT"
}

# 启动应用
start_app() {
    print_info "启动 MyOSS 应用..."
    
    # 设置环境变量
    export PORT=$PORT
    export PYTHONUNBUFFERED=1
    
    # 检查是否已经有进程在运行
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat $PID_FILE)
        if ps -p $OLD_PID > /dev/null 2>&1; then
            print_warning "检测到应用已在运行 (PID: $OLD_PID)"
            read -p "是否停止旧进程并重启？(y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill $OLD_PID
                sleep 1
                print_success "旧进程已停止"
            else
                print_info "取消启动"
                exit 0
            fi
        fi
        rm -f $PID_FILE
    fi
    
    # 启动应用
    print_info "日志文件：$LOG_FILE"
    print_info "访问地址：http://localhost:$PORT"
    echo ""
    
    # 后台运行
    nohup python3 app/__init__.py > $LOG_FILE 2>&1 &
    APP_PID=$!
    
    # 保存 PID
    echo $APP_PID > $PID_FILE
    
    # 等待应用启动
    sleep 3
    
    # 检查应用是否正常启动
    if ps -p $APP_PID > /dev/null 2>&1; then
        print_success "========================================="
        print_success "MyOSS 应用启动成功！"
        print_success "========================================="
        print_success "访问地址：http://localhost:$PORT"
        print_success "进程 PID: $APP_PID"
        print_success "日志文件：$LOG_FILE"
        print_success ""
        print_info "停止命令：./stop.sh"
        print_info "查看日志：tail -f $LOG_FILE"
        print_success "========================================="
    else
        print_error "应用启动失败，请查看日志：$LOG_FILE"
        exit 1
    fi
}

# 显示使用帮助
show_help() {
    echo "MyOSS 一键启动脚本"
    echo ""
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -p, --port      指定端口（默认：5001）"
    echo "  -r, --reinstall 重新安装依赖"
    echo "  -v, --verbose   显示详细信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用默认端口启动"
    echo "  $0 -p 5002           # 使用 5002 端口启动"
    echo "  $0 -r                # 重新安装依赖后启动"
    echo ""
}

# 主函数
main() {
    # 解析命令行参数
    REINSTALL=false
    VERBOSE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -r|--reinstall)
                REINSTALL=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            *)
                print_error "未知选项：$1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo ""
    echo "========================================="
    echo "  MyOSS 一键启动脚本"
    echo "========================================="
    echo ""
    
    # 执行检查
    check_project_root
    check_venv
    activate_venv
    
    # 重新安装依赖或检查依赖
    if [ "$REINSTALL" = true ]; then
        install_dependencies
    else
        print_info "如需重新安装依赖，请使用 -r 选项"
    fi
    
    # 创建目录
    check_logs_dir
    
    # 检查环境和端口
    check_env_vars
    check_and_kill_process
    
    # 启动应用
    start_app
}

# 运行主函数
main "$@"

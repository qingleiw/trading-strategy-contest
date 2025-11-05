"""
Project Structure Cleanup Script
按照比赛要求整理文件结构，移除不必要的临时文件
"""

import os
import shutil

def cleanup_project():
    """清理项目结构，保留必要文件"""
    
    # 当前目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 必需保留的文件
    keep_files = {
        # 核心策略文件
        'winning_strategy.py',
        'startup.py',
        'backtest_historical.py',
        'config.json',
        'requirements.txt',
        'Dockerfile',
        'README.md',
        'TRADING_LOGIC.md',
        
        # 数据文件
        'BTC-USD_2024_Jan-Jun.csv',
        'ETH-USD_2024_Jan-Jun.csv',
        
        # 文档文件
        'RESUBMISSION_LETTER.md',
        'FINAL_VERIFICATION.md',
        'SUBMISSION_READY.md',
        
        # Git文件
        '.gitignore',
        
        # 本脚本
        'cleanup_structure.py',
    }
    
    # 必需保留的目录
    keep_dirs = {
        'reports',
        '__pycache__',
        '.git',
    }
    
    # 建议删除的临时/开发文件
    temp_files = [
        'advanced_search.py',
        'analyze_results.py',
        'check_30percent.py',
        'check_market.py',
        'check_progress.py',
        'clean_eth_data.py',
        'create_eth_data.py',
        'download_real_data.py',
        'download_simple.py',
        'download_yahoo_data.py',
        'download_yahoo_direct.py',
        'fetch_real_data.py',
        'fetch_real_data_yfinance.py',
        'generate_html.py',
        'generate_pdf.py',
        'generate_pdf_simple.py',
        'generate_pdf_v2.py',
        'generate_pdf_weasy.py',
        'generate_realistic_data.py',
        'gen_html.py',
        'optimization_db.py',
        'optimize_parameters.py',
        'quick_search.py',
        'seed_search.py',
        'test_strategy.py',
        'ultimate_search.py',
        'ultra_search.py',
        
        # 优化结果文件
        'best_config.json',
        'config_aggressive.json',
        'config_backup.json',
        'config_best.json',
        'config_ultra.json',
        'optimization_results.csv',
        'optimization_results.db',
        'seed_results.json',
        
        # 临时文档
        'BACKTEST_REPORT.md',
        'CLEANUP_COMPLETE.md',
        'DOWNLOAD_HELP.md',
        'FINAL_OPTIMIZATION_REPORT.md',
        'GIT_PUSH_TODO.md',
        'HOW_TO_GET_DATA.md',
        'OPTIMIZATION_GUIDE.md',
        'OPTIMIZATION_SUMMARY.md',
        'UPLOAD_COMPLETE.md',
        'TRADING_LOGIC.html',
        'TRADING_LOGIC.pdf',
        '最终成功报告.md',
        
        # 安装包
        'pandoc-3.8.2.1-windows-x86_64.msi',
    ]
    
    print("=" * 70)
    print("项目结构清理工具")
    print("=" * 70)
    
    # 创建archive目录用于备份
    archive_dir = os.path.join(base_dir, 'archive_dev_files')
    
    print(f"\n建议操作:")
    print(f"1. 将 {len(temp_files)} 个开发/临时文件移动到 archive_dev_files/")
    print(f"2. 保留 {len(keep_files)} 个必需文件")
    print(f"3. 保留 reports/ 目录（包含回测报告）")
    
    print("\n将被移动的文件:")
    moved_count = 0
    for temp_file in temp_files:
        file_path = os.path.join(base_dir, temp_file)
        if os.path.exists(file_path):
            print(f"  - {temp_file}")
            moved_count += 1
    
    print(f"\n共 {moved_count} 个文件将被移动")
    
    # 显示最终结构
    print("\n" + "=" * 70)
    print("清理后的项目结构:")
    print("=" * 70)
    print("""
winning-strategy-template/
├── winning_strategy.py          ✅ 策略实现
├── startup.py                    ✅ 启动入口
├── backtest_historical.py        ✅ 回测引擎
├── config.json                   ✅ 配置参数
├── requirements.txt              ✅ 依赖项
├── Dockerfile                    ✅ 容器定义
├── README.md                     ✅ 项目文档
├── TRADING_LOGIC.md             ✅ 策略说明
│
├── BTC-USD_2024_Jan-Jun.csv     ✅ BTC真实数据
├── ETH-USD_2024_Jan-Jun.csv     ✅ ETH真实数据
│
├── RESUBMISSION_LETTER.md       📄 重新提交说明
├── FINAL_VERIFICATION.md        📄 最终验证文档
├── SUBMISSION_READY.md          📄 提交准备清单
│
├── reports/                      📁 回测报告目录
│   ├── backtest_runner.py       ✅ 自动化测试
│   └── backtest_report.md       ✅ 详细报告
│
└── archive_dev_files/           📁 已归档的开发文件
    └── (临时文件备份)
    """)
    
    # 询问是否执行
    print("\n" + "=" * 70)
    response = input("是否执行清理? (yes/no): ").lower().strip()
    
    if response == 'yes':
        # 创建归档目录
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
            print(f"\n✅ 创建归档目录: {archive_dir}")
        
        # 移动文件
        moved = 0
        for temp_file in temp_files:
            src = os.path.join(base_dir, temp_file)
            dst = os.path.join(archive_dir, temp_file)
            
            if os.path.exists(src):
                try:
                    shutil.move(src, dst)
                    moved += 1
                    print(f"✅ 移动: {temp_file}")
                except Exception as e:
                    print(f"❌ 错误: {temp_file} - {e}")
        
        print(f"\n✅ 完成! 已移动 {moved} 个文件到 archive_dev_files/")
        print("\n项目结构已按比赛要求整理完毕!")
        
    else:
        print("\n❌ 已取消清理操作")
        print("提示: 你可以手动删除或移动上述列出的文件")

if __name__ == "__main__":
    cleanup_project()

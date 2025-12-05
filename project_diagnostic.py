"""
OmniMarket 金融监控系统 - 项目诊断工具
检查项目健康状况并提供开发建议
"""

import os
import sys
import json
from pathlib import Path

class ProjectDiagnostic:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.suggestions = []
        
    def check_backend(self):
        """检查后端状态"""
        print("\n1️⃣ 后端检查")
        print("=" * 60)
        
        backend_path = self.project_root / "backend"
        
        # 检查主文件
        main_file = backend_path / "main.py"
        if main_file.exists():
            print("  ✅ main.py 存在")
        else:
            print("  ❌ main.py 缺失")
            self.issues.append("缺少后端入口文件 main.py")
        
        # 检查服务模块
        services_path = backend_path / "services"
        if services_path.exists():
            service_files = list(services_path.glob("*.py"))
            print(f"  ✅ 服务模块: {len(service_files)} 个")
            
            for service in service_files:
                size_kb = service.stat().st_size / 1024
                print(f"     • {service.name} ({size_kb:.1f} KB)")
        else:
            print("  ❌ services 目录缺失")
            self.issues.append("缺少 services 目录")
        
        # 检查配置文件
        config_file = backend_path / "config.py"
        if config_file.exists():
            print("  ✅ config.py 存在")
        else:
            print("  ⚠️ config.py 缺失")
            self.suggestions.append("创建配置文件 config.py")
        
        # 检查数据库配置
        db_file = backend_path / "database.py"
        if db_file.exists():
            print("  ✅ database.py 存在")
        else:
            print("  ⚠️ database.py 缺失")
        
        # 检查依赖文件
        req_file = backend_path / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                deps = f.readlines()
            print(f"  ✅ requirements.txt ({len(deps)} 个依赖)")
        else:
            print("  ⚠️ requirements.txt 缺失")
            self.suggestions.append("创建 requirements.txt")
    
    def check_frontend(self):
        """检查前端状态"""
        print("\n2️⃣ 前端检查")
        print("=" * 60)
        
        frontend_path = self.project_root / "frontend"
        
        # 检查package.json
        package_file = frontend_path / "package.json"
        if package_file.exists():
            print("  ✅ package.json 存在")
            with open(package_file) as f:
                package_data = json.load(f)
                print(f"     • 项目: {package_data.get('name', 'N/A')}")
                print(f"     • 版本: {package_data.get('version', 'N/A')}")
        else:
            print("  ❌ package.json 缺失")
            self.issues.append("前端配置文件缺失")
        
        # 检查src目录
        src_path = frontend_path / "src"
        if src_path.exists():
            js_files = list(src_path.rglob("*.js")) + list(src_path.rglob("*.jsx"))
            ts_files = list(src_path.rglob("*.ts")) + list(src_path.rglob("*.tsx"))
            print(f"  ✅ src 目录存在")
            print(f"     • JS/JSX: {len(js_files)} 个")
            print(f"     • TS/TSX: {len(ts_files)} 个")
        else:
            print("  ❌ src 目录缺失")
            self.issues.append("前端源码目录缺失")
        
        # 检查node_modules
        node_modules = frontend_path / "node_modules"
        if node_modules.exists():
            print("  ✅ node_modules 已安装")
        else:
            print("  ⚠️ node_modules 未安装")
            self.suggestions.append("运行 npm install")
    
    def check_documentation(self):
        """检查文档"""
        print("\n3️⃣ 文档检查")
        print("=" * 60)
        
        docs = {
            "README.md": "项目说明",
            "DEVELOPMENT_ROADMAP.md": "开发路线图",
            "PROJECT_UI_STANDARDS.md": "UI规范",
            "API_DOCS.md": "API文档",
            "DEPLOYMENT.md": "部署文档"
        }
        
        for doc, desc in docs.items():
            doc_path = self.project_root / doc
            if doc_path.exists():
                size = doc_path.stat().st_size / 1024
                print(f"  ✅ {doc} ({desc}) - {size:.1f} KB")
            else:
                print(f"  ⚠️ {doc} ({desc}) - 缺失")
                if doc in ["API_DOCS.md", "DEPLOYMENT.md"]:
                    self.suggestions.append(f"创建 {doc}")
    
    def check_git_status(self):
        """检查Git状态"""
        print("\n4️⃣ Git 状态")
        print("=" * 60)
        
        git_path = self.project_root / ".git"
        if git_path.exists():
            print("  ✅ Git 仓库已初始化")
            
            # 检查.gitignore
            gitignore = self.project_root / ".gitignore"
            if gitignore.exists():
                print("  ✅ .gitignore 存在")
            else:
                print("  ⚠️ .gitignore 缺失")
                self.suggestions.append("创建 .gitignore")
        else:
            print("  ⚠️ Git 未初始化")
            self.suggestions.append("初始化 Git 仓库")
    
    def analyze_features(self):
        """分析功能完成度"""
        print("\n5️⃣ 功能分析")
        print("=" * 60)
        
        features = {
            "市场数据服务": "data_service.py",
            "技术指标分析": "technical_analysis_service.py",
            "窝轮分析": "warrants_analysis_service.py",
            "自动交易": "auto_trading_service.py",
            "半自动交易": "semi_auto_trading_service.py",
            "虚拟交易": "virtual_trading_engine.py",
            "回测系统": "lean_backtest_service.py",
            "预警系统": "alert_service.py",
            "数据质量监控": "data_quality_monitor.py"
        }
        
        backend_services = self.project_root / "backend" / "services"
        completed = 0
        
        for feature, file in features.items():
            file_path = backend_services / file
            if file_path.exists():
                size = file_path.stat().st_size / 1024
                status = "✅" if size > 5 else "⚠️"
                print(f"  {status} {feature:<15} ({size:.1f} KB)")
                if size > 5:
                    completed += 1
            else:
                print(f"  ❌ {feature:<15} (缺失)")
        
        completion = (completed / len(features)) * 100
        print(f"\n  完成度: {completion:.1f}%")
        
        return completion
    
    def generate_report(self):
        """生成完整报告"""
        print("\n" + "=" * 60)
        print("🏥 OmniMarket 金融监控系统 - 诊断报告")
        print("=" * 60)
        
        self.check_backend()
        self.check_frontend()
        self.check_documentation()
        self.check_git_status()
        completion = self.analyze_features()
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 诊断总结")
        print("=" * 60)
        
        print(f"\n  项目完成度: {completion:.1f}%")
        print(f"  发现问题: {len(self.issues)} 个")
        print(f"  改进建议: {len(self.suggestions)} 条")
        
        if self.issues:
            print("\n❌ 需要修复的问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.suggestions:
            print("\n💡 改进建议:")
            for i, suggestion in enumerate(self.suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        # 下一步建议
        print("\n" + "=" * 60)
        print("🎯 下一步开发建议")
        print("=" * 60)
        
        if completion < 50:
            print("\n  优先级: 🔴 高")
            print("  建议: 完善核心功能模块")
            print("    • 实现完整的市场数据服务")
            print("    • 开发技术指标分析")
            print("    • 建立数据库连接")
        elif completion < 80:
            print("\n  优先级: 🟡 中")
            print("  建议: 完善高级功能")
            print("    • 开发窝轮分析系统")
            print("    • 实现自动交易功能")
            print("    • 完善前后端集成")
        else:
            print("\n  优先级: 🟢 低")
            print("  建议: 优化和测试")
            print("    • 添加单元测试")
            print("    • 性能优化")
            print("    • 完善文档")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnostic = ProjectDiagnostic()
    diagnostic.generate_report()

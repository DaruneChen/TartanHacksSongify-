#!/usr/bin/env python3
"""
Screen to Song - System Test Script
Tests all components of the system
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_python():
    """Test Python installation"""
    print_header("Testing Python")
    try:
        version = sys.version.split()[0]
        major, minor = map(int, version.split('.')[:2])
        if major >= 3 and minor >= 8:
            print(f"✓ Python {version} (OK)")
            return True
        else:
            print(f"✗ Python {version} (Need 3.8+)")
            return False
    except Exception as e:
        print(f"✗ Python test failed: {e}")
        return False

def test_node():
    """Test Node.js installation"""
    print_header("Testing Node.js")
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        print(f"✓ Node.js {version}")
        return True
    except FileNotFoundError:
        print("✗ Node.js not found")
        return False

def test_ffmpeg():
    """Test FFmpeg installation"""
    print_header("Testing FFmpeg")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        version_line = result.stdout.split('\n')[0]
        print(f"✓ {version_line}")
        return True
    except FileNotFoundError:
        print("✗ FFmpeg not found")
        print("  Install: sudo apt-get install ffmpeg (Ubuntu)")
        print("          brew install ffmpeg (macOS)")
        return False

def test_python_packages():
    """Test Python package installation"""
    print_header("Testing Python Packages")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "anthropic",
        "openai",
        "PIL",
        "imagehash"
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package if package != "PIL" else "PIL")
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} not installed")
            all_ok = False
    
    if not all_ok:
        print("\nInstall missing packages:")
        print("  cd backend && pip install -r requirements.txt")
    
    return all_ok

def test_api_keys():
    """Test API key configuration"""
    print_header("Testing API Keys")
    
    env_file = Path(__file__).parent.parent / "backend" / ".env"
    
    if not env_file.exists():
        print("✗ .env file not found")
        print("  Copy .env.example to backend/.env and add your API keys")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    has_anthropic = "ANTHROPIC_API_KEY=sk-" in content
    has_openai = "OPENAI_API_KEY=sk-" in content
    
    if has_anthropic:
        print("✓ Anthropic API key configured")
    if has_openai:
        print("✓ OpenAI API key configured")
    
    if not has_anthropic and not has_openai:
        print("✗ No API keys configured")
        print("  Add either ANTHROPIC_API_KEY or OPENAI_API_KEY to .env")
        return False
    
    return True

def test_backend_imports():
    """Test backend can import properly"""
    print_header("Testing Backend Imports")
    
    backend_dir = Path(__file__).parent.parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    try:
        import main
        print("✓ Backend main.py imports successfully")
        return True
    except Exception as e:
        print(f"✗ Backend import failed: {e}")
        return False

def test_scripts():
    """Test utility scripts"""
    print_header("Testing Scripts")
    
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))
    
    all_ok = True
    
    try:
        import music_generator
        print("✓ music_generator.py")
    except Exception as e:
        print(f"✗ music_generator.py: {e}")
        all_ok = False
    
    try:
        import video_assembler
        print("✓ video_assembler.py")
    except Exception as e:
        print(f"✗ video_assembler.py: {e}")
        all_ok = False
    
    try:
        import pipeline
        print("✓ pipeline.py")
    except Exception as e:
        print(f"✗ pipeline.py: {e}")
        all_ok = False
    
    return all_ok

def main():
    print("\n🎸 Screen to Song - System Test")
    print("Testing all components...\n")
    
    results = {
        "Python": test_python(),
        "Node.js": test_node(),
        "FFmpeg": test_ffmpeg(),
        "Python Packages": test_python_packages(),
        "API Keys": test_api_keys(),
        "Backend": test_backend_imports(),
        "Scripts": test_scripts()
    }
    
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Start backend:  cd backend && ./start.sh")
        print("  2. Start frontend: cd frontend && ./start.sh")
        print("  3. Open http://localhost:3000")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

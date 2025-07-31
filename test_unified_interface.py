#!/usr/bin/env python3
"""
Test script for the unified Oneverter interface.
This script tests the new unified architecture without running the full application.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic UI imports
        import customtkinter as ctk
        from ui.theme import apply_theme, Colors, Fonts
        print("✅ Basic UI imports successful")
        
        # Test unified main window
        from ui.unified_main_window import UnifiedMainWindow, NavigationManager, CategorySidebar
        print("✅ Unified main window imports successful")
        
        # Test converter panel base class
        from ui.converter_panel import ConverterPanel, TabConverterPanel, GridConverterPanel
        print("✅ Converter panel base classes imported successfully")
        
        # Test panel registry
        from ui.panels import get_panel_class, PANEL_REGISTRY
        print("✅ Panel registry imported successfully")
        
        # Test individual panels
        from ui.panels.audio_converter_panel import AudioConverterPanel
        from ui.panels.video_tools_panel import VideoToolsPanel
        from ui.panels.document_converter_panel import DocumentConverterPanel
        from ui.panels.image_converter_panel import ImageConverterPanel
        from ui.panels.archive_converter_panel import ArchiveConverterPanel
        from ui.panels.data_converter_panel import DataConverterPanel
        print("✅ All converter panels imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_panel_registry():
    """Test the panel registry functionality."""
    print("\n🧪 Testing panel registry...")
    
    try:
        from ui.panels import get_panel_class, PANEL_REGISTRY
        
        expected_categories = ['Audio', 'Video', 'Document', 'Image', 'Archive', 'Data']
        
        print("Available panels:")
        for category in expected_categories:
            panel_class = get_panel_class(category)
            if panel_class:
                print(f"  ✅ {category}: {panel_class.__name__}")
            else:
                print(f"  ❌ {category}: Not found")
                return False
                
        print(f"✅ All {len(expected_categories)} panels registered correctly")
        return True
        
    except Exception as e:
        print(f"❌ Panel registry error: {e}")
        return False

def test_theme_system():
    """Test the theme system."""
    print("\n🧪 Testing theme system...")
    
    try:
        from ui.theme import Colors, Fonts, get_button_style, get_frame_style
        
        # Test color constants
        assert hasattr(Colors, 'BACKGROUND')
        assert hasattr(Colors, 'FRAME')
        assert hasattr(Colors, 'BUTTON')
        assert hasattr(Colors, 'TEXT')
        print("✅ Color constants available")
        
        # Test font constants
        assert hasattr(Fonts, 'TITLE')
        assert hasattr(Fonts, 'HEADING')
        assert hasattr(Fonts, 'BODY')
        print("✅ Font constants available")
        
        # Test style functions
        button_style = get_button_style()
        assert isinstance(button_style, dict)
        print("✅ Button style function works")
        
        frame_style = get_frame_style()
        assert isinstance(frame_style, dict)
        print("✅ Frame style function works")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme system error: {e}")
        return False

def test_navigation_manager():
    """Test the navigation manager."""
    print("\n🧪 Testing navigation manager...")
    
    try:
        import customtkinter as ctk
        from ui.unified_main_window import NavigationManager
        
        # Create a mock main window
        class MockMainWindow:
            def update_breadcrumbs(self):
                pass
            def show_home(self):
                pass
            def show_category(self, category):
                pass
            def show_tool(self, category, tool):
                pass
        
        mock_window = MockMainWindow()
        nav_manager = NavigationManager(mock_window)
        
        # Test navigation
        nav_manager.navigate_to("Audio")
        assert len(nav_manager.current_path) == 2  # Home + Audio
        print("✅ Category navigation works")
        
        nav_manager.navigate_to("Audio", "Converter", "Audio Converter")
        assert len(nav_manager.current_path) == 3  # Home + Audio + Tool
        print("✅ Tool navigation works")
        
        # Test breadcrumbs
        breadcrumb = nav_manager.get_breadcrumb_text()
        assert "Home" in breadcrumb
        assert "Audio" in breadcrumb
        print("✅ Breadcrumb generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Navigation manager error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Unified Oneverter Interface")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_panel_registry,
        test_theme_system,
        test_navigation_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The unified interface is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
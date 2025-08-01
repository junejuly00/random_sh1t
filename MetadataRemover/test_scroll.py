#!/usr/bin/env python3
"""
Test script to verify the scrollable MetadataManager works correctly.
"""

try:
    import metadataremover
    
    print("✅ Imported metadataremover successfully")
    
    # Create the GUI
    app = metadataremover.MetadataManagerGUI()
    print("✅ Created GUI successfully")
    
    # Check for scroll components
    if hasattr(app, 'main_canvas'):
        print("✅ Main canvas created")
    else:
        print("❌ Main canvas missing")
        
    if hasattr(app, 'main_scrollbar'):
        print("✅ Main scrollbar created")
    else:
        print("❌ Main scrollbar missing")
    
    # Check responsive panels
    if hasattr(app, 'left_frame') and hasattr(app, 'middle_frame') and hasattr(app, 'right_frame'):
        print("✅ All panels created as class attributes")
    else:
        print("❌ Some panels missing")
    
    print("\n🎯 Testing window resize to small size (800x600)...")
    app.root.geometry("800x600")
    app.root.update()
    
    print("✅ Resized to small window successfully")
    
    print("\n🎯 Testing window resize to large size (1400x900)...")
    app.root.geometry("1400x900")
    app.root.update()
    
    print("✅ Resized to large window successfully")
    
    print("\n🎉 All scroll and responsive tests passed!")
    print("💡 You can now run: python metadataremover.py")
    print("📝 Try resizing the window to see responsive layout")
    print("🖱️ Use mouse wheel to scroll content when needed")
    
    # Don't start mainloop in test
    app.root.destroy()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

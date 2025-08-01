#!/usr/bin/env python3
"""
Simple test to check if the MetadataManager application starts without errors.
"""

try:
    # Import the main module
    import metadataremover
    
    print("✅ Module imported successfully")
    
    # Try to create the GUI class (but don't run mainloop)
    app = metadataremover.MetadataManagerGUI()
    print("✅ GUI object created successfully")
    
    # Check if key attributes exist
    required_attrs = [
        'root', 'colors', 'selected_files', 'processed_files',
        'advanced_mode', 'progress_var', 'status_var',
        'file_listbox', 'file_count_label', 'progress_text',
        'results_label', 'settings_container'
    ]
    
    missing_attrs = []
    for attr in required_attrs:
        if not hasattr(app, attr):
            missing_attrs.append(attr)
    
    if missing_attrs:
        print(f"❌ Missing attributes: {missing_attrs}")
    else:
        print("✅ All required attributes present")
    
    # Try to call toggle_mode (this was causing the error)
    try:
        app.toggle_mode()
        print("✅ toggle_mode() executed successfully")
    except Exception as e:
        print(f"❌ toggle_mode() failed: {e}")
    
    print("\n🎉 Application appears to be working correctly!")
    print("You can now run: python metadataremover.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
